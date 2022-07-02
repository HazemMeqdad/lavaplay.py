import asyncio
import aiohttp
import logging
from lavaplayer.utlits import generate_resume_key
from .objects import (
    Info,
    PlayerUpdateEvent,
    TrackStartEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStuckEvent,
    WebSocketClosedEvent,
)
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
        loop: t.Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.ws = None
        self.ws_url = f"{'wss' if is_ssl else 'ws'}://{host}:{port}"
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
            _LOGGER.info("Connected to websocket")
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
        if payload["op"] == "stats":
            self.client.info = Info(
                playing_players=payload["playingPlayers"],
                memory_used=payload["memory"]["used"],
                memory_free=payload["memory"]["free"],
                players=payload["players"],
                uptime=payload["uptime"]
            )

        elif payload["op"] == "playerUpdate":
            guild_id = int(payload["guildId"])
            node = await self.client.get_guild_node(guild_id)
            position = payload["state"].get("position")
            if node is None:
                return
            
            if node.queue:
                node.queue[0].position = position / 1000
                await self.client.set_guild_node(guild_id, node)
            data = PlayerUpdateEvent(
                guild_id=guild_id,
                time=payload["state"]["time"],
                position=position / 1000 if isinstance(position, int) else None,
                connected=payload["state"].get("connected", None),
            )
            self.emitter.emit("PlayerUpdateEvent", data)

        elif payload["op"] == "event" and payload.get("track") is not None:
            await self.event_dispatch(payload)
            
    async def event_dispatch(self, payload: dict):
        if payload.get("track"):
            track = await self.client.decodetrack(payload["track"])
        event = payload["type"]

        guild_id = int(payload["guildId"])

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
            self.emitter.emit("TrackExceptionEvent", TrackExceptionEvent(track, guild_id, payload.get("exception"), payload.get("message"), payload.get("severity"), payload.get("cause")))

        elif event == "TrackStuckEvent":
            self.emitter.emit("TrackStuckEvent", TrackStuckEvent(track, guild_id, payload.get("thresholdMs")))

        elif event == "WebSocketClosedEvent":
            self.emitter.emit("WebSocketClosedEvent", WebSocketClosedEvent(guild_id, payload.get("code"), payload.get("reason"), payload.get("byRemote")))
        
        else:
            _LOGGER.warning(f"Unknown event: {event}")

    @property
    def is_connected(self) -> bool:
        return self.is_connect and self.ws.closed is False

    async def send(self, payload):  # only dict
        if not self.is_connected:
            _LOGGER.error("Not connected to websocket")
            return
        try:
            await self.ws.send_json(payload)
        except ConnectionResetError:
            _LOGGER.error("ConnectionResetError: Cannot write to closing transport")
            await self.check_connection()
            return
