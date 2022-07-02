import asyncio
import time
import typing as t
import random
from lavaplayer.exceptions import NodeError, VolumeError, TrackLoadFailed
from .emitter import Emitter
from .websocket import WS
from .api import LavalinkRest
from .objects import Info, Track, Node, Filters, ConnectionInfo, Event, PlayList
from . import __version__
from .utlits import get_event_loop, prossing_tracks


class Lavalink:
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
    user_id: :class:`int | None`
        The bot id when you keep None you need to set on a started event on ur library used.
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
        user_id: t.Optional[int] = None,
        num_shards: int = 1,
        is_ssl: bool = False,
        loop: t.Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.user_id = user_id
        self.num_shards = num_shards
        self.is_ssl = is_ssl
        
        self.loop = loop or get_event_loop()
        self.event_manager = Emitter(self.loop)
        self._ws: t.Optional[WS] = None

        # Unique identifier for the client.
        self.rest = LavalinkRest(host=self.host, port=self.port, password=self.password, is_ssl=self.is_ssl)
        self.info: Info = None
        self._nodes: t.Dict[int, Node] = {}
        self._voice_handlers: t.Dict[int, ConnectionInfo] = {}
        self._task_loop: asyncio.Task = None

    def set_user_id(self, user_id: int) -> None:
        """
        Set the bot id for the client requird set after call :meth:`connect` if not setup.

        Parameters
        ---------
        user_id: :class:`int`
            The bot id.
        """
        self.user_id = user_id
    
    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Set the event loop for the client requird set after call :meth:`connect`,

        Parameters
        ---------
        loop: :class:`asyncio.AbstractEventLoop`
            The event loop to use.
        """
        asyncio.set_event_loop(loop)
        self.loop = loop
        self.event_manager._loop = loop

    def set_host(self, host: str) -> None:
        """
        Set the host for the client.

        Parameters
        ---------
        host: :class:`str`
            The host to use.
        """
        self.host = host
    
    def set_port(self, port: int) -> None:
        """
        Set the port for the client.

        Parameters
        ---------
        port: :class:`int`
            The port to use.
        """
        self.port = port
    
    def set_password(self, password: str) -> None:
        """
        Set the password for the client.

        Parameters
        ---------
        password: :class:`str`
            The password to use.
        """
        self.password = password
    
    def set_num_shards(self, num_shards: int) -> None:
        """
        Set the count shards for websocket
        """
        self.num_shards = num_shards
    
    def set_is_ssl(self, is_ssl: bool) -> None:
        """
        Set the is_ssl for the client.

        Parameters
        ---------
        is_ssl: :class:`bool`
            The is_ssl to use.
        """
        self.is_ssl = is_ssl

    async def search_youtube(self, query: str) -> t.Optional[t.Union[t.List[Track], TrackLoadFailed]]:
        """
        Search for tracks with youtube.

        Parameters
        ---------
        query: :class:`str`
            words for search with youtube. if not found result retrun empty :class:`list`
        
        Exceptions
        ----------
        :class:`lavaplayer.exceptions.TrackLoadFailed`
            If the track could not be loaded.
        """
        result = await self.rest.load_tracks(f"ytsearch:{query}")
        if result["loadType"] == "NO_MATCHES":
            return []
        if result["loadType"] == "LOAD_FAILED":
            return TrackLoadFailed(result["exception"]["message"], result["exception"]["severity"])
        return prossing_tracks(result["tracks"])

    async def get_tracks(self, query: str) -> t.Optional[t.Union[t.List[Track], PlayList, TrackLoadFailed]]:
        """
        Load tracks for unknow sits or youtube or soundcloud or radio.

        Parameters
        ---------
        query: :class:`str`
            track url, if not found result retrun empty :class:`list`
        
        Exceptions
        ----------
        :class:`lavaplayer.exceptions.TrackLoadFailed`
            If the track could not be loaded.
        """
        result = await self.rest.load_tracks(query)
        if result["loadType"] == "NO_MATCHES":
            return []
        if result["loadType"] == "LOAD_FAILED":
            raise TrackLoadFailed(result["exception"]["message"], result["exception"]["severity"])
        if result["loadType"] == "PLAYLIST_LOADED":
            return PlayList(result["playlistInfo"]["name"], result["playlistInfo"]["selectedTrack"], prossing_tracks(result["tracks"]))
        return prossing_tracks(result["tracks"])

    async def decodetrack(self, track: str) -> Track:
        """
        This method is used to decode a track from base64 only server can resolve, to info can anyone understanding it
        
        Parameters
        ---------
        track: :class:`str`
            track result from base64
        """
        result = await self.rest.decode_track(track)
        return Track(
            track,
            identifier=result["identifier"],
            is_seekable=result["isSeekable"],
            author=result["author"],
            length=result["length"],
            is_stream=result["isStream"],
            position=result["position"],
            source_name=result.get("sourceName", None),
            title=result.get("title", None),
            uri=result["uri"]
        )

    async def decodetracks(self, tracks: t.List[t.Dict]) -> t.List[Track]:
        """
        This method is used to decode a tracks from base64 only server can resolve, to info can anyone understanding it

        Parameters
        ---------
        tracks: :class:`list`
            tracks result from base64
        """
        result = await self.rest.decode_tracks(tracks)
        return prossing_tracks(result)

    async def auto_search_tracks(self, query: str) -> t.Union[t.Optional[t.List[Track]], t.Optional[PlayList]]:
        """
        Load tracks for youtube search or other urls.

        Parameters
        ---------
        query: :class:`str`
            url or words to search, if not found result retrun empty :class:`list`

        Exceptions
        ----------
        :class:`lavaplayer.exceptions.TrackLoadFailed`
            If the track could not be loaded.
        """
        if "http" in query:
            return await self.get_tracks(query)
        return await self.search_youtube(query)

    async def create_new_node(self, guild_id: int, /, is_connected: bool = False) -> Node:
        node = Node(guild_id, [], 100, is_connected=is_connected)
        self._nodes[guild_id] = node
        return node

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

    async def add_to_queue(self, guild_id: int, /, tracks: t.List[Track], requester: t.Optional[int] = None) -> None:
        """
        Add tracks to queue. use to load a playlist result.

        >>> playlist = await lavaplayer.search_youtube("playlist url")
        >>> await lavaplayer.add_to_queue(guild_id, playlist.tracks)

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        tracks: :class:`list`
            tracks to add to queue
        """
        node = await self.get_guild_node(guild_id)
        if not node:
            raise NodeError("Node not found", guild_id)

        for track in tracks:
            self.loop.create_task(self.play(guild_id, track, requester))

    async def play(self, guild_id: int, /, track: Track, requester: t.Optional[int] = None, start: bool = False) -> None:
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
        payload = {
            "op": "play",
            "guildId": str(guild_id),
            "track": track.track,
            "startTime": "0",
            "noReplace": False
        }
        if start:
            await self._ws.send(payload)
            return
        track.requester = requester
        node.queue.append(track)
        await self.set_guild_node(guild_id, node)
        if len(node.queue) != 1:
            return
        await self._ws.send(payload)

    async def queue(self, guild_id: int, /) -> t.List[Track]:
        """
        Get guild queue list from node cache memory.

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

    async def queue_repeat(self, guild_id: int, /, stats: bool) -> None:
        """
        Repeat the queue for every.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        stats: :class:`bool`
            the stats for repeat queue
        """
        node = await self.get_guild_node(guild_id)
        node.queue_repeat = stats
        node.repeat = False
        await self.set_guild_node(guild_id, node)

    async def filters(self, guild_id: int, /, filters: t.Optional[Filters]) -> None:
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
        if not filters:
            filters = Filters()
        filters._payload["guildId"] = str(guild_id)
        await self._ws.send(filters._payload)

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

    async def shuffle(self, guild_id: int, /) -> t.Union[Node, t.List]:
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

    async def remove(self, guild_id: int, /, position: int) -> t.Union[Node, t.List]:
        """
        Remove a track from the queue.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        position: :class:`int`
            the position of the track in the queue
        
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
        node.queue.pop(position)
        await self.set_guild_node(guild_id, node)
        return node
    
    async def index(self, guild_id: int, /, position: int) -> t.Union[Node, t.List]:
        """
        Get the track at a specific position in the queue.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        position: :class:`int`
            the position of the track in the queue
        
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
        return node.queue[position]
    

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
        await self.create_new_node(guild_id, is_connected=True)

    async def raw_voice_state_update(self, guild_id: int, /, user_id: int, session_id: str, channel_id: t.Optional[int]) -> None:
        """
        A voice state update has been received from Discord.
        
        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        user_id: :class:`int`
            user id
        session_id: :class:`str`
            session id
        channel_id: :class:`int` | :class:`None`
            the channel id, if not give the channel id will automatically destroy node.
        """
        if user_id != self.user_id:
            return
        elif not channel_id:
            await self.destroy(guild_id)
            return
        self._voice_handlers[guild_id] = ConnectionInfo(guild_id, session_id, channel_id)

    async def raw_voice_server_update(self, guild_id: int, /, endpoint: str, token: str) -> None:
        """
        A voice server update has been received from Discord.
        
        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        endpoint: :class:`str`
            the endpoint for the voice server
        token: :class:`str`
            the token for the voice server
        """
        connection_info = self._voice_handlers.get(guild_id)
        if not connection_info:
            return
        await self.voice_update(guild_id, connection_info.session_id, token, endpoint, connection_info.channel_id)

    async def wait_for_connection(self, guild_id: int, /) -> t.Optional[Node]:
        """
        Wait for the voice connection to be established.

        Parameters
        ---------
        guild_id: :class:`int`
            guild id for server
        """
        while not (await self.get_guild_node(guild_id)):
            await asyncio.sleep(0.1)
        return await self.get_guild_node(guild_id)

    async def wait_for_remove_connection(self, guild_id: int, /) -> None:
        """
        Wait for the voice connection to be removed.

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
        while (await self.get_guild_node(guild_id)):
            await asyncio.sleep(0.1)

    def listen(self, event: t.Union[str, Event]) -> t.Callable[..., t.Awaitable]:
        """
        The register function for listener handler

        Parameters
        ---------
        event: :class:`Any` | :class:`str`
            event name or class for event
        """
        def deco(func: t.Awaitable) -> t.Callable[..., t.Awaitable]:
            self.event_manager.add_listener(event, func)
        return deco

    @property
    def is_connect(self) -> bool:
        """
        Check if the client is connect to the voice server.
        """
        return self._ws.is_connect

    def connect(self):
        """
        Connect to the lavalink websocket
        """
        self._ws = WS(
            client=self, 
            host=self.host, 
            port=self.port, 
            is_ssl=self.is_ssl, 
            password=self.password, 
            user_id=self.user_id, 
            num_shards=self.num_shards
        )
        self.loop.create_task(self._ws._connect())

    async def close(self):
        """
        Disconnect from the lavalink websocket
        """
        await self._ws.ws.close()

    @property
    def nodes(self):
        return self._nodes

class LavalinkClient(Lavalink):
    """
    Inherit from :class:`Lavalink`, ill remove it later..
    """
