import asyncio
import aiohttp
import logging
from .utlits import event_track
from .objects import (
    Stats, Cpu, Memory, FrameStats
)
from .events import (
    TrackEndEvent, TrackExceptionEvent, TrackStuckEvent, 
    TrackStartEvent, ReadyEvent, PlayerState, 
    PlayerUpdateEvent, StatsUpdateEvent, TrackException,
    WebSocketClosedEvent
)
from .emitter import Emitter
import typing as t
from . import __version__
if t.TYPE_CHECKING:
    from .node_manager import Node

_LOG = logging.getLogger("lavaplay.ws")

class WS:
    def __init__(
        self,
        node: "Node",
        host: str,
        port: int,
        ssl: bool = False,
        password: str = None,
        user_id: int = None,
        shards_count: int = None,
        loop: t.Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self.ws = None
        self.ws_url = f"{'wss' if ssl else 'ws'}://{host}:{port}/v4/websocket"
        self.node = node
        self._headers = {
            "Authorization": password,
            "User-Id": str(user_id),
            "Client-Name": f"Lavaplay.py/{__version__}",
            "Num-Shards": str(shards_count)
        }
        self._loop = loop or node.loop
        self.emitter: Emitter = node.event_manager
        self.is_connect: bool = False
        self._session_id: str = None
    
    @property
    def session_id(self) -> str:
        return self._session_id

    async def _connect(self):
        async with aiohttp.ClientSession(headers=self._headers, loop=self._loop) as session:
            self.session = session
            _LOG.info(f"Connecting to websocket {self.ws_url}")
            try:
                self.ws = await self.session.ws_connect(self.ws_url)
                if session is None:
                    await self.check_connection()
            except (aiohttp.ClientConnectorError, aiohttp.WSServerHandshakeError, aiohttp.ServerDisconnectedError) as error:
                if isinstance(error, (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError)):
                    _LOG.error(f"Could not connect to websocket: {error}")
                    _LOG.warning("Reconnecting to websocket after 10 seconds")  
                    await asyncio.sleep(10)
                    await self._connect()
                    return
                elif isinstance(error, aiohttp.WSServerHandshakeError):
                    if error.status in (403, 401):  # Unauthorized or Forbidden
                        _LOG.warning("Password authentication failed - closing websocket")
                        return
                    _LOG.warning("Please check your websocket port - closing websocket")
            self.is_connect = True

            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    self._loop.create_task(self.callback(msg.json()))
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                    _LOG.error("Websocket closed")
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOG.error(msg.data)
                    break

    async def check_connection(self):
        while self.ws.closed is None or not self.ws.closed or not self.is_connected:
            _LOG.warning("Websocket closed unexpectedly - reconnecting in 10 seconds")
            if self.node.nodes:
                self.node.nodes.clear()
            await asyncio.sleep(10)
            await self._connect()

    async def callback(self, payload: dict):
        # https://github.com/freyacodes/Lavalink/blob/master/IMPLEMENTATION.md#ready-op
        if payload["op"] == "ready":
            _LOG.info("Lavalink client is ready")
            self._session_id = payload["sessionId"]
            self.node.session_id = self._session_id
            await self.node.rest.update_session(
                self._session_id,
                data={
                    "resuming": False,
                    "timeout": self.node._resume_timeout or 180
                }
            )
            if payload["resumed"] is True:
                _LOG.info("Lavalink client resumed session successfully")
            else:
                _LOG.info("Lavalink client started a new session successfully")
            self.emitter.emit("ready", data=ReadyEvent.from_kwargs(**payload))
        
        # https://github.com/freyacodes/Lavalink/blob/master/IMPLEMENTATION.md#player-update-op
        elif payload["op"] == "playerUpdate":
            payload.pop("op")
            guild_id = int(payload["guildId"])
            player = self.node.get_player(guild_id)
            if player is None:
                return
            position = payload["state"].get("position")
            position = position / 1000 if isinstance(position, int) else None
            if player.queue:
                player.queue[0].position = position
            payload["state"]["position"] = position
            payload["state"] = PlayerState.from_kwargs(**payload["state"])
            data = PlayerUpdateEvent.from_kwargs(**payload)
            self.emitter.emit("PlayerUpdateEvent", data)
        
        # https://github.com/freyacodes/Lavalink/blob/master/IMPLEMENTATION.md#stats-op
        elif payload["op"] == "stats":
            payload.pop("op")
            # Fix types
            if payload.get("frameStats") is not None:
                payload["frameStats"] = FrameStats.from_kwargs(**payload["frameStats"])
            payload["memory"] = Memory.from_kwargs(**payload["memory"])
            payload["cpu"] = Cpu.from_kwargs(**payload["cpu"])
            self.node.stats = Stats.from_kwargs(**payload)
            self.emitter.emit("StatsUpdateEvent", StatsUpdateEvent(self.node.stats))

        # https://github.com/freyacodes/Lavalink/blob/master/IMPLEMENTATION.md#event-op
        elif payload["op"] == "event" and payload.get("track") is not None:
            await self.event_dispatch(payload)
            
    async def event_dispatch(self, payload: dict):
        # encodedTrack is for Lavalink new version v4
        if payload["track"]["encoded"]:
            track = payload["track"]
        event = payload["type"]

        guild_id = int(payload["guildId"])
        payload.pop("op")
        payload.pop("type")
        payload.pop("guildId")
        payload["guild_id"] = guild_id

        player = self.node.get_player(guild_id)

        if event == "TrackStartEvent":
            self.emitter.emit("TrackStartEvent", TrackStartEvent(event_track(track), guild_id))

        elif event == "TrackEndEvent":
            self.emitter.emit("TrackEndEvent", TrackEndEvent(event_track(track), guild_id, payload["reason"]))
            # reason = payload["reason"]
            if not player or not player.queue:
                return
            if player._queue_repeat:
                player.queue.append(player.queue.pop(0))
                if len(player.queue) == 0:
                    return
                await player.play(player.queue[0], player.queue[0].requester, True)
                return
            if player._repeat:
                await player.play(track, player.queue[0].requester, True)
                return
            player.queue.pop(0)
            if len(player.queue) != 0:
                await player.play(player.queue[0], player.queue[0].requester, True)

        elif event == "TrackExceptionEvent":
            payload["exception"] = TrackException.from_kwargs(**payload["exception"])
            self.emitter.emit("TrackExceptionEvent", TrackExceptionEvent.from_kwargs(**payload))

        elif event == "TrackStuckEvent":
            self.emitter.emit("TrackStuckEvent", TrackStuckEvent.from_kwargs(**payload))

        elif event == "WebSocketClosedEvent":
            self.emitter.emit("WebSocketClosedEvent", WebSocketClosedEvent.from_kwargs(**payload))
        
        else:
            _LOG.warning(f"Unknown event: {event}")

    @property
    def is_connected(self) -> bool:
        return self.is_connect and self.ws.closed is False

    async def send(self, payload):  # only dict
        """
        Will not be call on new lavalink version v4
        """
        if not self.is_connected:
            _LOG.error("Not connected to websocket")
            return
        try:
            await self.ws.send_json(payload)
        except ConnectionResetError:
            _LOG.error("ConnectionResetError: Cannot write to closing transport")
            await self.check_connection()
            return
