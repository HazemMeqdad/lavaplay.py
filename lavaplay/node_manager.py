import asyncio
import typing as t
from lavaplay.exceptions import TrackLoadFailed
from .emitter import Emitter
from .ws import WS
from .rest import RestApi
from .objects import Stats, Track, ConnectionInfo, PlayList
from .events import Event
from . import __version__
from .utlits import get_event_loop, prossing_tracks
import logging
from .player import Player

_LOG = logging.getLogger("lavaplay.node")

class Node:
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
        user_id: t.Optional[int],
        resume_key: str = None, 
        resume_timeout: int = 180,
        shards_count: int = 1,
        is_ssl: bool = False,
        loop: t.Optional[asyncio.AbstractEventLoop] = None,
        **kwargs
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.user_id = user_id
        self.shards_count = shards_count
        self.is_ssl = is_ssl
        
        self.loop = loop or get_event_loop()
        self.event_manager = Emitter(self.loop)
        self._ws: t.Optional[WS] = None

        # Unique identifier for the client.
        self.rest = RestApi(host=self.host, port=self.port, password=self.password, is_ssl=self.is_ssl)
        self.stats: Stats = None
        self._voice_handlers: t.Dict[int, ConnectionInfo] = {}

        self.session_id: t.Optional[str] = None

        self.players: t.Dict[int, Player] = {}
    
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

    def create_player(self, guild_id: int) -> Player:
        """
        Create a player for guild id.

        Parameters
        ---------
        guild_id: :class:`int`
            The guild id for player.
        """
        player = Player(self, guild_id)
        self.players[guild_id] = player
        return player
    
    def destroy_player(self, guild_id: int) -> None:
        """
        Destroy a player for guild id.

        Parameters
        ---------
        guild_id: :class:`int`
            The guild id for player.
        """
        del self.players[guild_id]

    def get_player(self, guild_id: int) -> Player:
        """
        Get player for guild id.

        Parameters
        ---------
        guild_id: :class:`int`
            The guild id for player.
        """
        return self.players.get(guild_id)
    
    def get_players(self) -> t.List[Player]:
        """
        Get all players.
        """
        return list(self.players.values())
    
    def change_player(self, guild_id: int, player: Player) -> None:
        """
        Change player for guild id.

        Parameters
        ---------
        guild_id: :class:`int`
            The guild id for player.
        player: :class:`Player`
            The player to change.
        """
        self.players[guild_id] = player

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
        return self._ws.is_connect if self._ws else False

    def connect(self):
        """
        Connect to the lavalink websocket
        """
        self._ws = WS(
            node=self, 
            host=self.host, 
            port=self.port, 
            is_ssl=self.is_ssl, 
            password=self.password, 
            user_id=self.user_id, 
            shards_count=self.shards_count,
        )
        asyncio.run_coroutine_threadsafe(self._ws._connect(), self.loop)

    async def close(self):
        """
        Disconnect from the lavalink websocket
        """
        await self._ws.ws.close()
