import typing as t
import asyncio
from .objects import Track, Filters, ConnectionInfo , PlayList
from .exceptions import VolumeError
import random
import logging
if t.TYPE_CHECKING:
    from .node_manager import Node

_LOG = logging.getLogger("lavaplay.player")


class Player:
    def __init__(self, node: "Node", guild_id: int) -> None:
        self.guild_id = guild_id
        self.node = node
        self.rest = node.rest
        self._voice_state: t.Optional[dict] = None
        self.user_id: int = node.user_id
        self._voice_handlers: t.Dict[int, ConnectionInfo] = {}

        self._volume: int = 100
        self._filters: Filters = Filters()
        self.queue: t.List[Track] = []
        self.loop: asyncio.AbstractEventLoop = node.loop

        self._repeat = False
        self._queue_repeat = False
        self._is_connected = False
        self._ping = 0

    def add_to_queue(self, tracks: t.List[Track], requester: t.Optional[int] = None) -> None:
        """
        Add tracks to queue. use to load a playlist result.

        >>> playlist = lavaplay.search_youtube("playlist url")
        >>> lavaplay.add_to_queue(playlist.tracks)

        Parameters
        ---------
        tracks: :class:`list`
            tracks to add to queue
        """
        for track in tracks:
            self.loop.create_task(self.play(self.guild_id, track, requester))

    async def play(self, track: Track, requester: t.Optional[int] = None, start: bool = False) -> None:
        """
        Play track or add to the queue list.

        Parameters
        ---------
        requester: :class:`bool`
            user id for requester the play track
        start: :class:`bool`
            force play queue is ignored
        """
        if not track.encoded:
            raise ValueError("Encoded of the track is None")

        if len(self.queue) == 0 or start:
            await self.rest.update_player(
                session_id=self.node.session_id,
                guild_id=self.guild_id,
                data={"track": {"encoded": track.encoded}}
            )
        if not start:
            track.requester = requester
            self.queue.append(track)

    async def play_playlist(self, playlist: PlayList):
        """
        Play track or add to the queue list.

        Parameters
        ---------
        playlist: :class:`bool`
            user id for requester the play track
        """
        for track in playlist.tracks:
            await self.play(track)

    def repeat(self, stats: bool) -> None:
        """
        Repeat the track for every.

        Parameters
        ---------
        stats: :class:`bool`
            the stats for repeat track
        """
        self._repeat = stats

    def queue_repeat(self, stats: bool) -> None:
        """
        Repeat the queue for every.

        Parameters
        ---------
        stats: :class:`bool`
            the stats for repeat queue
        """
        self._queue_repeat = stats
        self._repeat = False

    async def filters(self, filters: t.Optional[Filters]) -> None:
        """
        Repeat the track for every.

        Parameters
        ---------
        filters: :class:`Filters`
            add filters to the track
        """     
        if not filters:
            filters = Filters()
        filters._payload["guildId"] = str(self.guild_id)
        await self.rest.update_player(
            session_id=self.node.session_id,
            guild_id=self.guild_id,
            data={
                "filters": filters._payload
            }
        )

    async def stop(self) -> None:
        """
        Stop the track.
        """
        if len(self.queue) == 0:
            return
        self.queue.clear()
        await self.rest.update_player(
            session_id=self.node.session_id,
            guild_id=self.guild_id,
            data={"track": {"encoded": None}}
        )

    async def skip(self) -> None:
        """
        Skip the track
        """        
        if len(self.queue) == 0:
            return
        await self.rest.update_player(
            session_id=self.node.session_id,
            guild_id=self.guild_id,
            data={"track": {"encoded": None}}
        )

    async def pause(self, stats: bool) -> None:
        """
        Pause the track.

        Parameters
        ---------
        stats: :class:`bool`
            the stats for repeat track
        """        
        await self.rest.update_player(
            session_id=self.node.session_id,
            guild_id=self.guild_id,
            data={
                "paused": stats
            }
        )

    async def seek(self, position: int) -> None:
        """
        seek to custom position for the track, the position is in milliseconds.

        Parameters
        ---------
        position: :class:`int`
            the position is in milliseconds
        """        
        await self.rest.update_player(
            session_id=self.node.session_id,
            guild_id=self.guild_id,
            data={
                "position": position
            }
        )

    async def volume(self, volume: int) -> None:
        """
        Set volume for a player track.

        Parameters
        ---------
        volume: :class:`int`
            Volume may range from 0 to 1000. 100 is default

        Raises
        --------
        :exc:`.VolumeError`
            if volume is not in range from 0 to 1000.
        """
        if volume < 0 or volume > 1000:
            raise VolumeError("Volume may range from 0 to 1000. 100 is default", self.guild_id)        
        self._volume = volume
        await self.rest.update_player(
            session_id=self.node.session_id,
            guild_id=self.guild_id,
            data={
                "volume": volume
            }
        )

    async def destroy(self) -> None:
        """
        Tell the server to potentially disconnect from the voice server and potentially remove the player with all its data.
        This is useful if you want to move to a new node for a voice connection.
        Calling this function does not affect voice state, and you can send the same VOICE_SERVER_UPDATE to a new node.

        Parameters
        ---------

        Raises
        --------
        :exc:`.NodeError`
            If guild not found in nodes cache.
        """        
        await self.rest.destroy_player(self.node.session_id, self.guild_id)

    def shuffle(self, state: bool = True) -> t.Union["Node", t.List]:
        """
        Add shuffle to the track.

        Parameters
        ---------
        state: :class:`bool`
            the stats for shuffle track
        """        
        if not self.queue:
            return []
        self._shuffle = state
        np = self.queue[0]
        self.queue.remove(np)
        self.queue = random.sample(self.queue, len(self.queue))
        self.queue.insert(0, np)
        return self.queue

    def remove(self, position: int) -> None:
        """
        Remove a track from the queue.

        Parameters
        ---------
        position: :class:`int`
            the position of the track in the queue
        """        
        if not self.queue:
            return []
        self.queue.pop(position)
    
    def index(self, position: int) -> t.Union[Track, None]:
        """
        Get the track at a specific position in the queue.

        Parameters
        ---------
        position: :class:`int`
            the position of the track in the queue
        """        
        if not self.queue:
            return None
        elif position > len(self.queue):
            return None
        return self.queue[position]

    async def voice_update(self, session_id: str, token: str, endpoint: str, channel_id: t.Optional[int]) -> None:
        """
        Update the voice connection for a guild.

        Parameters
        ---------
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
            await self.destroy()
            return
        res = await self.rest.update_player(
            session_id=self.node.session_id,
            guild_id=self.guild_id,
            data={
                "voice": {
                    "token": token,
                    "sessionId": session_id,
                    "endpoint": endpoint.replace("wss://", "")
                }
            }
        )
        self._is_connected = res["state"]["connected"]
        self._ping = res["state"]["ping"]

    async def raw_voice_state_update(self, user_id: int, session_id: str, channel_id: t.Optional[int]) -> None:
        """
        A voice state update has been received from Discord.
        
        Parameters
        ---------
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
            await self.destroy()
            return
        self._voice_handlers[self.guild_id] = ConnectionInfo(self.guild_id, session_id, channel_id)

    async def raw_voice_server_update(self, endpoint: str, token: str) -> None:
        """
        A voice server update has been received from Discord.
        
        Parameters
        ---------
        endpoint: :class:`str`
            the endpoint for the voice server
        token: :class:`str`
            the token for the voice server
        """
        connection_info = self._voice_handlers.get(self.guild_id)
        if not connection_info:
            return
        await self.voice_update(connection_info.session_id, token, endpoint, connection_info.channel_id)

    @property
    def is_connected(self) -> bool:
        """
        Return if the player is connected to voice channel.
        """
        return self._is_connected

    @property
    def ping(self) -> int:
        """
        Return the ping of the player.
        """
        return self._ping
    
    @property
    def is_playing(self) -> bool:
        """
        Return if the player is playing.
        """
        return len(self.queue) > 0
