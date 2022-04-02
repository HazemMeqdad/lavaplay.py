import asyncio
import aiohttp
import logging
from lavaplayer.exceptions import NodeError
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

if t.TYPE_CHECKING:
    from .client import LavalinkClient


_LOGGER = logging.getLogger("lavaplayer.ws")


class WS:
    def __init__(
        self,
        client: "LavalinkClient",
        host: str,
        port: int,
        is_ssl: bool = False,
    ) -> None:
        self.ws = None
        self.ws_url = f"{'wss' if is_ssl else 'ws'}://{host}:{port}"
        self.client = client
        self._headers = client._headers
        self._loop = client._loop
        self.emitter: Emitter = client.event_manager
        self.is_connect: bool = False
    
    async def _connect(self):
        async with aiohttp.ClientSession(headers=self._headers, loop=self._loop) as session:
            self.session = session
            try:
                self.ws = await self.session.ws_connect(self.ws_url)
                if session is None:
                    await self.check_connection()
            except (aiohttp.ClientConnectorError, aiohttp.WSServerHandshakeError, aiohttp.ServerDisconnectedError) as error:
                
                if isinstance(error, aiohttp.ClientConnectorError):
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
                elif isinstance(error, aiohttp.ServerDisconnectedError):
                    _LOGGER.error(f"Could not connect to websocket: {error}")
                    _LOGGER.warning("Reconnecting to websocket after 10 seconds")
                    await asyncio.sleep(10)
                    await self._connect()
                    return

            _LOGGER.info("Connected to websocket")
            self.is_connect = True
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.callback(msg.json())
                elif msg.type == aiohttp.WSMsgType.CLOSED:
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
            self.emitter.emit("playerUpdateEvent", data)

        elif payload["op"] == "event":

            if not payload.get("track"):
                return
            track = await self.client._decodetrack(payload["track"])
            guild_id = int(payload["guildId"])
            try:
                node = await self.client.get_guild_node(guild_id)
            except NodeError:
                node = None

            if payload["type"] == "TrackStartEvent":
                self.emitter.emit("TrackStartEvent", TrackStartEvent(track, guild_id))

            elif payload["type"] == "TrackEndEvent":
                self.emitter.emit("TrackEndEvent", TrackEndEvent(track, guild_id, payload["reason"]))
                if not node:
                    return
                if not node.queue:
                    return
                if node.repeat:
                    await self.client.play(guild_id, track, node.queue[0].requester, True)
                    return
                del node.queue[0]
                await self.client.set_guild_node(guild_id, node)
                if len(node.queue) != 0:
                    await self.client.play(guild_id, node.queue[0], node.queue[0].requester, True)

            elif payload["type"] == "TrackExceptionEvent":
                self.emitter.emit("TrackExceptionEvent", TrackExceptionEvent(track, guild_id, payload["exception"], payload.get("message"), payload.get("severity"), payload.get("cause")))

            elif payload["type"] == "TrackStuckEvent":
                self.emitter.emit("TrackStuckEvent", TrackStuckEvent(track, guild_id, payload["thresholdMs"]))

            elif payload["type"] == "WebSocketClosedEvent":
                self.emitter.emit("WebSocketClosedEvent", WebSocketClosedEvent(track, guild_id, payload["code"], payload["reason"], payload["byRemote"]))

    @property
    def is_connected(self) -> bool:
        return self.is_connect and self.ws.closed is False

    async def send(self, payload):  # only dict
        if not self.is_connected:
            _LOGGER.error("Not connected to websocket")
            await self.check_connection()
            return
        try:
            await self.ws.send_json(payload)
        except ConnectionResetError:
            _LOGGER.error("ConnectionResetError: Cannot write to closing transport")
            await self.check_connection()
            return
