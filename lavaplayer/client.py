import asyncio
import typing as t
from lavaplayer.exceptions import NodeError, VolumeError
from .emitter import Emitter
from .websocket import WS
from .api import Api
from .objects import Info, Track, Node, Filters
from lavaplayer import __version__
import random


class LavalinkClient:
    """
    Represents a Lavalink client used to manage nodes and connections.

    Parameters
    ---------
    host: :class:`str`
        ip address for lavalink server, default ip address for lavalink is ``127.0.0.1``
    port: :class:`int`
        The port to use for websocket and REST connections.
    password: :class:`str`
        The password used for authentication.
    bot_id: :class:`int`
        The bot id
    num_shards: :class:`int`
        The count shards for websocket
    is_ssl: :class:`bool`
        Is server using ssl
    """
    def __init__(
        self,
        *,
        host: t.Optional[str] = "127.0.0.1",
        port: int,
        password: str,
        bot_id: int,
        num_shards: int = 1,
        is_ssl: bool = False,
    ) -> None:
        try:
            self._loop = asyncio.get_event_loop()
        except:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self._headers = {
            "Authorization": password,
            "User-Id": str(bot_id),
            "Client-Name": f"Lavaplayer/{__version__}",
            "Num-Shards": str(num_shards)
        }
        self.event_manger = Emitter(self._loop)
        self._ws = WS(self, host, port, is_ssl)
        self.info: Info = None
        self.host = host
        self.port = port
        self.is_ssl = is_ssl
        self.password = password
        self._api = Api(host=self.host, port=self.port, password=self.password, is_ssl=self.is_ssl)
        self._nodes: dict[int, Track] = {}

    def _prossing_tracks(self, tracks: list) -> t.List[Track]:
        _tracks = []
        for track in tracks:
            info = track["info"]
            _tracks.append(
                Track(
                    track=track["track"],
                    identifier=info["identifier"],
                    isSeekable=info["isSeekable"],
                    author=info["author"],
                    length=info["length"],
                    isStream=info["isStream"],
                    position=info["position"],
                    sourceName=info["sourceName"],
                    title=info["title"],
                    uri=info["uri"]
                )
            )
        return _tracks

    async def voice_update(self, guild_id: int, /, session_id: str, token: str, endpoint: str, channel_id: t.Optional[int]) -> None:
        """
        Update the voice connection for a guild.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        session_id: :class:`str`
            session id for connection
        token: :class:`str`
            token for connection
        endpoint: :class:`str`
            endpoint for connection
        channel_id: :class:`int`
            channel id for connection, if not give channel_id the connection will be closed
        """
        if not channel_id:
            await self.destroy(guild_id)
            return
        await self._ws.send({
            "op": "voiceUpdate",
            "guildId": str(guild_id),
            "sessionId": session_id,
            "event": {
                "token": token,
                "guild_id": str(guild_id),
                "endpoint": endpoint.replace("wss://", "")
            }
        })
        self._nodes[guild_id] = Node(guild_id, [], 100)

    async def search_youtube(self, query: str) -> t.Optional[t.List[Track]]:
        """
        Search for tracks with youtube.

        Parameters
        ---------
        query: :class:`str`
            words for search with youtube. if not found result retrun empty :class:`list`
        """
        result = await self._api.request("GET", "/loadtracks", data={"identifier": f"ytsearch:{query}"})
        if result["loadType"] == "NO_MATCHES":
            return []
        return self._prossing_tracks(result["tracks"])

    async def get_tracks(self, query: str) -> t.Optional[t.List[Track]]:
        """
        Load tracks for unknow sits or youtube or soundcloud or radio.

        Parameters
        ---------
        query: :class:`str`
            track url, if not found result retrun empty :class:`list`
        """
        result = await self._api.request("GET", "/loadtracks", data={"identifier": query})
        if result["loadType"] == "NO_MATCHES":
            return []
        return self._prossing_tracks(result["tracks"])

    async def _decodetrack(self, track: str) -> Track:
        result = await self._api.request("GET", "/decodetrack", data={"track": track})
        return Track(track, **result)

    async def _decodetracks(self, tracks: t.List[t.Dict]) -> t.List[Track]:
        result = await self._api.request("POST", "/decodetrack", json=tracks)
        return self._prossing_tracks(result)

    async def auto_search_tracks(self, query: str) -> t.Optional[t.List[Track]]:
        """
        Load tracks for youtube search or other urls.

        Parameters
        ---------
        query: :class:`str`
            url or words to search, if not found result retrun empty :class:`list`
        """
        if "http" in query:
            return await self.get_tracks(query)
        return await self.search_youtube(query)

    async def get_guild_node(self, guild_id: int, /) -> t.Optional[Node]:
        """
        Get guild info from node cache memory.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        """
        node = self._nodes.get(guild_id)
        return node

    async def remove_guild_node(self, guild_id: int, /) -> None:
        """
        Remove guild info from node cache memory.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        """
        node = await self.get_guild_node(guild_id)
        self._nodes.pop(node.guild_id)

    async def set_guild_node(self, guild_id: int, /, node: Node) -> None:
        """
        Set guild info from node cache memory.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        """
        await self.get_guild_node(guild_id)
        self._nodes[guild_id] = node

    async def quene(self, guild_id: int, /) -> t.List[Track]:
        """
        Get guild quene list from node cache memory.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        """
        node = await self.get_guild_node(guild_id)
        return node.queue

    async def repeat(self, guild_id: int, /, stats: bool) -> None:
        """
        Repeat the track for every.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        stats: :class:`bool`
            the stats for repeat track
        """
        node = await self.get_guild_node(guild_id)
        node.repeat = stats
        await self.set_guild_node(guild_id, node)

    async def play(self, guild_id: int, /, track: Track, requester: int, start: bool = False) -> None:
        """
        Play track or add to the queue list.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        requester: :class:`bool`
            user id for requester the play track
        start: :class:`bool`
            force play queue is ignored
        
        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        pyload = {
            "op": "play",
            "guildId": str(guild_id),
            "track": track.track,
            "startTime": "0",
            "noReplace": False
        }
        if start:
            await self._ws.send(pyload)
            return
        track.requester = requester
        node.queue.append(track)
        await self.set_guild_node(guild_id, node)
        if len(node.queue) != 1:
            return
        await self._ws.send(pyload)

    async def filters(self, guild_id: int, /, filters: Filters) -> None:
        """
        Repeat the track for every.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        filters: :class:`Filters`
            add filters to the track  
        
        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        filters._pyload["guildId"] = str(guild_id)
        await self._ws.send(filters._pyload)

    async def stop(self, guild_id: int, /) -> None:
        """
        Stop the track.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        
        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if len(node.queue) == 0:
            raise NodeError("Node not found", guild_id)
        node.queue.clear()
        await self.set_guild_node(guild_id, node)
        await self._ws.send({
            "op": "stop",
            "guildId": str(guild_id)
        })
        return node

    async def skip(self, guild_id: int, /) -> None:
        """
        Skip the track

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server

        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        if len(node.queue) == 0:
            return
        node.queue.pop(0)
        await self.set_guild_node(guild_id, node)
        await self._ws.send({
            "op": "stop",
            "guildId": str(guild_id)
        })
        return node

    async def pause(self, guild_id: int, /, stats: bool) -> None:
        """
        Pause the track.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        stats: :class:`bool`
            the stats for repeat track

        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        await self._ws.send({
            "op": "pause",
            "guildId": str(guild_id),
            "pause": stats
        })

    async def seek(self, guild_id: int, /, position: int) -> None:
        """
        seek to custom position for the track, the position is in milliseconds.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        position: :class:`int`    
            the position is in milliseconds

        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        await self._ws.send({
            "op": "seek",
            "guildId": str(guild_id),
            "position": position
        })

    async def volume(self, guild_id: int, /, volume: int) -> None:
        """
        Set volume for a player track.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        volume: :class:`int`
            Volume may range from 0 to 1000. 100 is default
        :exc:`.VolumeError`
            Volume may range from 0 to 1000.

        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        :exc:`.VolumeError`
            if volume is not in range from 0 to 1000.
        """
        if volume < 0 or volume > 1000:
            raise VolumeError("Volume may range from 0 to 1000. 100 is default", guild_id)
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        node.volume = volume
        await self.set_guild_node(guild_id, node)
        await self._ws.send({
            "op": "volume",
            "guildId": str(guild_id),
            "volume": volume
        })

    async def destroy(self, guild_id: int, /) -> None:
        """
        Tell the server to potentially disconnect from the voice server and potentially remove the player with all its data. 
        This is useful if you want to move to a new node for a voice connection. 
        Calling this function does not affect voice state, and you can send the same VOICE_SERVER_UPDATE to a new node.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server

        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        await self.remove_guild_node(guild_id)
        await self._ws.send({
            "op": "destroy",
            "guildId": str(guild_id)
        })

    async def shuffle(self, guild_id: int, /) -> t.Optional[Node]:
        """
        Add shuffle to the track.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        
        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)
        if not node.queue:
            return []
        np = node.queue[0]
        node.queue.remove(np)
        node.queue = random.sample(node.queue, len(node.queue))
        node.queue.insert(0, np)
        await self.set_guild_node(guild_id, node)
        return node


    def listner(self, event: t.Union[str, t.Any]) -> t.Callable[[t.Any], t.Any]:
        """
        The register function for listner handler

        Parameters
        ---------
        event: :class:`Any` | :class:`str`
            event name or class for event
        """
        def deco(func: t.Callable[[t.Any], t.Any]) -> t.Callable[[t.Any], t.Any]:
            self.event_manger.add_listner(event, func)
        return deco

    @property
    def is_connect(self) -> bool:
        """
        Check if the client is connect to the voice server.
        """
        return self._ws.is_connect

    async def connect(self):
        """
        Connect to the lavalink websocket
        """
        self._loop.create_task(self._ws._connect())
