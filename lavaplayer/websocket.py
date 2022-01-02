import aiohttp
import logging
from lavaplayer.exceptions import NodeError, WebsocketConnectionError
from .objects import (
    Info, 
    PlayerUpdate,
    TrackStartEvent, 
    TrackEndEvent, 
    TrackExceptionEvent, 
    TrackStuckEvent,
    WebSocketClosedEvent,
)
from .emitter import Emitter
import typing

if typing.TYPE_CHECKING:
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
        self.ws_url = f"{'wss' if is_ssl else 'ws'}://{host}:{port}"
        """ The websocket url. """

        self.client = client
        """ The client instance. """

        self._headers = client._headers
        """ The headers to be sent with the websocket. """
        
        self._loop = client._loop
        """ The event loop. """

        self.emitter: "Emitter" = client.event_manger
        """ The event emitter. """

        self.is_connect: bool = False
        """ Whether the websocket is connected. """

        self.session: aiohttp.ClientSession = aiohttp.ClientSession
        """ The aiohttp session. """

        self.__handlers = {
            "stats": self.stats_handler,
            "playerUpdate": self.player_update_handler,
            "event": self.event_handler,
        }
        """ The message handlers. """

    async def _connect(self):
        """
            |coro|
            This coroutine connects to the websocket and make the websocket alive.

            Raises
            ------
            WebsocketConnectionError
                If the websocket connection fails.
        """
        try:
            self.ws = await self.session.ws_connect(self.ws_url, headers=self._headers)
        except:
            _LOGGER.error("Failed to connect to websocket")
            raise WebsocketConnectionError("Failed to connect to websocket")
        
        self.is_connect = True

        if self.is_connect:
            await self.message_handler()

    async def message_handler(self):
        """
            |coro|
            This is the response handler for the websocket.

            Raises
            ------
            WebsocketConnectionError
                If the websocket connection fails.
        """
        
        async for message in self.ws:
            if message.type == aiohttp.WSMsgType.TEXT:
                handler = self.__handlers.get(message.json()["op"])
                if handler:
                    await handler(message.json())
                else:
                    _LOGGER.warn(f'Unknown OPCode {message.json()["op"]}')
            elif message.type == aiohttp.WSMsgType.CLOSED:
                _LOGGER.error("close")
                break
            
            elif message.type == aiohttp.WSMsgType.ERROR:
                _LOGGER.error(message.data)
                break

    async def stats_handler(self, payload: typing.Dict[str, str]) -> None:
        """
            |coro|
            This is the stats handler for the op code `stats`.

            Parameters
            ----------
            payload: `typing.Dict[str, str]`
                The payload of the stats event.
        """

        self.client.info = Info(
            playing_players=payload["playingPlayers"],
            memory_used=payload["memory"]["used"],
            memory_free=payload["memory"]["free"],
            players=payload["players"],
            uptime=payload["uptime"]
        )

    async def player_update_handler(self, payload: typing.Dict[str, str]) -> None:
        """
            |coro|
            This is the player update handler for the op code `playerUpdate`.

            Parameters
            ----------
            payload: `typing.Dict[str, str]`
                The payload of the player update event.
        """

        self.emitter.emit(
            PlayerUpdate(
                guild_id=payload["guildId"],
                player_id=payload["playerId"],
                track=payload["track"],
                position=payload["position"],
                volume=payload["volume"],
                paused=payload["paused"],
                repeat_mode=payload["repeatMode"],
                shuffle=payload["shuffle"],
                timestamp=payload["timestamp"],
            )
        )

    async def event_handler(self, payload: typing.Dict[str, str]) -> None:
        """
            |coro|
            This is the event handler for the op code `event`.

            Parameters
            ----------
            event_type: `str`
                The event type.
            payload: `typing.Dict[str, str]`
                The payload of the event.
        """

        if 'track' in payload.keys():
            return

        track = await self.client._decodetrack(payload["track"])
        """ The track object. """

        guild_id = int(payload["guildId"])
        """ The guild id. """

        try:
            node = await self.client.get_guild_node(guild_id)
        except KeyError:
            node = None

        if payload["type"] == "TrackStartEvent":
            self.emitter.emit("TrackStartEvent", 
                TrackStartEvent(track, guild_id))

        elif payload["type"] == "TrackEndEvent":
            self.emitter.emit("TrackEndEvent", 
                TrackEndEvent(track, guild_id, payload["reason"]))
                
            if not node or node.queue:
                return

            if node.repeat:
                return await self.client.play(guild_id, track, node.queue[0].requester, True)
            
            del node.queue[0]

            await self.client.set_guild_node(guild_id, node)

            if len(node.queue) != 0:
                await self.client.play(guild_id, node.queue[0], node.queue[0].requester, True)

        elif payload["type"] == "TrackExceptionEvent":
            self.emitter.emit("TrackExceptionEvent", 
                TrackExceptionEvent(
                    track, guild_id, payload["exception"], payload["message"], payload["severity"], payload["cause"]))

        elif payload["type"] == "TrackStuckEvent":
            self.emitter.emit("TrackStuckEvent", 
                TrackStuckEvent(
                    track, guild_id, payload["thresholdMs"]))

        elif payload["type"] == "WebSocketClosedEvent":
            self.emitter.emit("WebSocketClosedEvent", 
                    WebSocketClosedEvent(
                        track, guild_id, payload["code"], payload["reason"], payload["byRemote"]))

    @property
    def is_connected(self) -> bool:
        """
            Whether the websocket is connected.
        """
        return self.is_connect and self.ws.closed is False

    async def send(self, payload: typing.Dict):  # only dict
        """
            |coro|
            This coroutine sends a message to the websocket.

            Parameters
            ----------

        """
        if self.is_connected == False:
            return _LOGGER.error("Not connected to websocket")

        if isinstance(payload, dict):
            await self.ws.send_json(payload)
        else:
            raise TypeError("payload must be a dict")
