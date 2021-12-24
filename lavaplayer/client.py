from __future__ import annotations
import asyncio
from typing import Any
from .emitter import Emitter
from .websocket import WS
from .api import Api
from .objects import Info, Track
import asyncio


class LavalinkClient:
    def __init__(
        self,
        host: str,
        port: int,
        password: str,
        bot_id: int,
        num_shards: int = 1,
        is_ssl: bool = False,
        token: str = None,
        start_discord_gateway: bool = True
    ) -> None:
        try:
            self._loop = asyncio.get_event_loop()
        except:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self._headers = {
            "Authorization": password,
            "User-Id": str(bot_id),
            "Client-Name": "Lavaplay-py/0.0.1",
            "Num-Shards": str(num_shards)
        }
        self.event_manger = Emitter(self._loop)
        self._ws = WS(self, host, port, is_ssl)
        self.info: Info = None
        self.host = host
        self.port = port
        self.is_ssl = is_ssl
        self.password = password
        self._api = Api(self.host, self.port, self.password, self.is_ssl)

    def _prossing_tracks(self, tracks: list) -> list[Track]:
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

    async def search_youtube(self, query: str) -> list[Track] | None:
        result = await self._api.request("GET", "/loadtracks", data={"identifier": f"ytsearch:{query}"})
        if result["loadType"] == "NO_MATCHES":
            return []
        return self._prossing_tracks(result["tracks"])

    async def get_tracks(self, query: str) -> list[Track] | None:
        result = await self._api.request("GET", "/loadtracks", data={"identifier": query})
        if result["loadType"] == "NO_MATCHES":
            return []
        return self._prossing_tracks(result["tracks"])
    
    async def _decodetrack(self, track: str) -> Track:
        result = await self._api.request("GET", "/decodetrack", data={"track": track})
        return Track(track, **result)
    
    async def _decodetracks(self, tracks: list):
        result = await self._api.request("POST", "/decodetrack", json=tracks)
        return self._prossing_tracks(result)

    async def auto_search_tracks(self, query: str) -> list[Track] | None:
        if "http" in query:
            return await self.get_tracks(query)
        return await self.search_youtube(query)

    async def play(self, guild_id: int, /, track: Track) -> None:
        await self._ws.send({
            "op": "play",
            "guildId": str(guild_id),
            "track": track.track,
            "startTime": "0",
            "noReplace": False
        })

    async def stop(self, guild_id: int, /) -> None:
        await self._ws.send({
            "op": "stop",
            "guildId": str(guild_id)
        })
    
    async def pause(self, guild_id: int, /, stats: bool):
        await self._ws.send({
            "op": "pause",
            "guildId": str(guild_id),
            "pause": stats
        })

    async def seek(self, guild_id: int, /, position: int):
        await self._ws.send({
            "op": "seek",
            "guildId": str(guild_id),
            "position": position
        })

    async def volume(self, guild_id: int, /, volume: int):
        await self._ws.send({
            "op": "volume",
            "guildId": str(guild_id),
            "volume": volume
        })

    async def destroy(self, guild_id: int, /):
        await self._ws.send({
            "op": "destroy",
            "guildId": str(guild_id)
        })

    def listner(self, event: str | Any):
        def deco(func):
            self.event_manger.add_listner(event, func)
        return deco
        
    async def wait_for(self, event: str | Any, callback: function):
        self.event_manger.add_listner(event, callback, once=True)

    async def connect(self):
        self._loop.create_task(self._ws._connect())

