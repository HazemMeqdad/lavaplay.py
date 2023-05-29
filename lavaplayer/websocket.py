import asyncio
import aiohttp
import logging
from lavaplayer.utlits import generate_resume_key
from .objects import *
from .events import *
from .emitter import Emitter
import typing as t
from . import __version__

if t.TYPE_CHECKING:
    from .client import Lavalink


_LOGGER = logging.getLogger("lavaplayer.ws")


class WS:
    def __init__(
        self,
        client: "Lavalink",
        host: str,
        port: int,
        is_ssl: bool = False,
        password: str = None,
        user_id: int = None,
        num_shards: int = None,
        resume_key: t.Optional[str] = None,
        loop: t.Optional[asyncio.AbstractEventLoop] = None,
        v4: bool = True,
    ) -> None:
        self.ws = None
        self.ws_url = f"{'wss' if is_ssl else 'ws'}://{host}:{port}"
        if v4 is False:
            self.ws_url += "/v3/websocket"
        self.client = client
        self._headers = {
            "Authorization": password,
            "User-Id": str(user_id),
            "Client-Name": f"Lavaplayer-py/{__version__}",
            "Num-Shards": str(num_shards)
        }
        self._loop = loop or client.loop
        self.emitter: Emitter = client.event_manager
        self.is_connect: bool = False
        self.resume_key = resume_key
        self._session_id: str = None
    
    @property
    def session_id(self) -> str:
        return self._session_id

    async def _connect(self):
        if self.resume_key:
            self._headers["Resume-Key"] = self.resume_key
        async with aiohttp.ClientSession(headers=self._headers, loop=self._loop) as session:
            self.session = session
            try:
                self.ws = await self.session.ws_connect(self.ws_url)
                if session is None:
                    await self.check_connection()
            except (aiohttp.ClientConnectorError, aiohttp.WSServerHandshakeError, aiohttp.ServerDisconnectedError) as error:
                if isinstance(error, (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError)):
                    _LOGGER.error(f"Could not connect to websocket: {error}")
                    _LOGGER.warning("Reconnecting to websocket after 10 seconds")  
                    await asyncio.sleep(10)
                    await self._connect()
                    return
                elif isinstance(error, aiohttp.WSServerHandshakeError):
                    if error.status in (403, 401):  # Unauthorized or Forbidden
                        _LOGGER.warning("Password authentication failed - closing websocket")
                        return
                    _LOGGER.warning("Please check your websocket port - closing websocket")
            self.is_connect = True

            self.resume_key = generate_resume_key()
            await self.send({
                "op": "configureResuming",
                "key": self.resume_key,
                "timeout": 60
            })

            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    self._loop.create_task(self.callback(msg.json()))
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                    _LOGGER.error("Websocket closed")
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOGGER.error(msg.data)
                    break

    async def check_connection(self):
        while self.ws.closed is None or not self.ws.closed or not self.is_connected:
            _LOGGER.warning("Websocket closed unexpectedly - reconnecting in 10 seconds")
            if self.client.nodes:
                self.client.nodes.clear()
            await asyncio.sleep(10)
            await self._connect()

    async def callback(self, payload: dict):
        # https://github.com/freyacodes/Lavalink/blob/master/IMPLEMENTATION.md#ready-op
        if payload["op"] == "ready":
            _LOGGER.info("Lavalink client is ready")
            self._session_id = payload["sessionId"]
            self.emitter.emit("ready", data=ReadyEvent.from_kwargs(**payload))
        
        # https://github.com/freyacodes/Lavalink/blob/master/IMPLEMENTATION.md#player-update-op
        elif payload["op"] == "playerUpdate":
            payload.pop("op")
            guild_id = int(payload["guildId"])
            node = await self.client.get_guild_node(guild_id)
            if node is None:
                return
            position = payload["state"].get("position")
            position = position / 1000 if isinstance(position, int) else None
            if node.queue:
                node.queue[0].position = position
                await self.client.set_guild_node(guild_id, node)
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
            self.client.stats = Stats.from_kwargs(**payload)
            self.emitter.emit("StatsUpdateEvent", StatsUpdateEvent(self.client.stats))

        # https://github.com/freyacodes/Lavalink/blob/master/IMPLEMENTATION.md#event-op
        elif payload["op"] == "event" and payload.get("track") is not None:
            await self.event_dispatch(payload)
            
    async def event_dispatch(self, payload: dict):
        # encodedTrack is for Lavalink new version v4
        print(payload)
        if payload.get("encodedTrack"):
            track = await self.client.decodetrack(payload.get("encodedTrack"))
        event = payload["type"]

        guild_id = int(payload["guildId"])
        payload.pop("op")
        payload.pop("type")
        payload.pop("guildId")
        payload["guild_id"] = guild_id

        node = await self.client.get_guild_node(guild_id)

        if event == "TrackStartEvent":
            self.emitter.emit("TrackStartEvent", TrackStartEvent(track, guild_id))

        elif event == "TrackEndEvent":
            self.emitter.emit("TrackEndEvent", TrackEndEvent(track, guild_id, payload["reason"]))
            if not node or not node.queue:
                return
            if node.queue_repeat:
                node.queue.append(node.queue.pop(0))
                await self.client.set_guild_node(guild_id, node)
                if len(node.queue) == 0:
                    return
                await self.client.play(guild_id, node.queue[0], node.queue[0].requester, True)
                return
            if node.repeat:
                await self.client.play(guild_id, track, node.queue[0].requester, True)
                return
            del node.queue[0]
            await self.client.set_guild_node(guild_id, node)
            if len(node.queue) != 0:
                await self.client.play(guild_id, node.queue[0], node.queue[0].requester, True)

        elif event == "TrackExceptionEvent":
            payload["exception"] = TrackException.from_kwargs(**payload["exception"])
            self.emitter.emit("TrackExceptionEvent", TrackExceptionEvent.from_kwargs(**payload))

        elif event == "TrackStuckEvent":
            self.emitter.emit("TrackStuckEvent", TrackStuckEvent.from_kwargs(**payload))

        elif event == "WebSocketClosedEvent":
            self.emitter.emit("WebSocketClosedEvent", WebSocketClosedEvent.from_kwargs(**payload))
        
        else:
            _LOGGER.warning(f"Unknown event: {event}")

    @property
    def is_connected(self) -> bool:
        return self.is_connect and self.ws.closed is False

    async def send(self, payload):  # only dict
        """
        Will not be call on new lavalink version v4
        """
        if not self.is_connected:
            _LOGGER.error("Not connected to websocket")
            return
        try:
            await self.ws.send_json(payload)
        except ConnectionResetError:
            _LOGGER.error("ConnectionResetError: Cannot write to closing transport")
            await self.check_connection()
            return
