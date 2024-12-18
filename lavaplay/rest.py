import aiohttp
from . import routes
import logging
import typing as t
from .exceptions import requestFailed

_LOG = logging.getLogger("lavaplay.rest")

class RestApi:
    """
    The class make a request to the rest api for lavalink.

    Parameters
    ---------
    host: :class:`str`
        ip address for lavalink server, default ip address for lavalink is ``
    port: :class:`int`
        The port to use for websocket and REST connections.
    password: :class:`str`
        The password used for authentication.
    is_ssl: :class:`bool`
        Is server using ssl.
    version: :class:`str`
        The version for lavalink server, default version is `v4`, newer version and recommend.
    """
    def __init__(self, *, host: str = "127.0.0.1", port: int, password: str, ssl: bool = False, version: t.Literal["v3", "v4"] = "v4") -> None:
        self.rest_uri = f"{'https' if ssl else 'http'}://{host}:{port}"
        self.api_version = version
        self.headers = {
            "Authorization": password
        }

    async def request(self, method: str, rout: str, data: dict = {}, without_version: bool = False) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        method: :class:`str`
            method for request like `GET` or `POST` etc.
        rout: :class:`str`
            The route for request.
        data: :class:`dict`
            The data for request.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        rout = rout if without_version else f"/{self.api_version}{rout}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.rest_uri + rout, headers=self.headers, json=data) as response:
                _LOG.debug(f"{method} {self.rest_uri + rout}")
                if method == "DELETE":
                    return
                response = await response.json()
                print(response)
                if response.get("error") is not None:
                    _LOG.error(f"Request failed: {response}")
                    raise requestFailed(**response)
                return response
    
    async def load_tracks(self, identifier: str) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        identifier: :class:`str`
            The identifier for search tracks.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.TRACK_LOADING.format(identifier=identifier))
        return res
    
    async def decode_track(self, track: str) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        track: :class:`str`
            The track for decode.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.TRACK_DECODEING.format(encodedTrack=track))
        return res
    
    async def decode_tracks(self, tracks: list) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        tracks: :class:`list`
            The tracks for decode.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("POST", routes.TRACKS_DECODEING, data=tracks)
        return res
    
    async def info(self) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.INFO)
        return res
    
    async def stats(self) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.STATS)
        return res
    
    async def router_planner(self) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.ROUTEPLANNER)
        return res
    
    async def unmark_failed_address(self, address: str) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        address: :class:`str`
            The address for unmark.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("POST", routes.UNMARK_FAILED_ADDRESS, data={"address": address})
        return res
    
    async def unmark_all_failed_address(self) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("POST", routes.UNMARK_ALL_FAILED_ADDRESS)
        return res
    
    async def get_players(self, session_id: str) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        session_id: :class:`str`
            The session id for get players.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.GET_PLAYERS.format(sessionId=session_id))
        return res
    
    async def get_player(self, session_id: str, guild_id: str) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        session_id: :class:`str`
            The session id for get player.
        guild_id: :class:`str`
            The guild id for get player.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.GET_PLAYER.format(sessionId=session_id, guildId=guild_id))
        return res
    
    async def update_player(self, session_id: str, guild_id: int, noReplace: bool = False, data: dict = {}) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        session_id: :class:`str`
            The session id for update player.
        guild_id: :class:`int`
            The guild id for update player.
        noReplace: :class:`bool`
            The noReplace for update player.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("PATCH", routes.UPDATE_PLAYER.format(sessionId=session_id, guildId=guild_id, noReplace="true" if noReplace else "false"), data=data)
        return res
    
    async def destroy_player(self, session_id: str, guild_id: int) -> None:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        session_id: :class:`str`
            The session id for destroy player.
        guild_id: :class:`str`
            The guild id for destroy player.
        """
        await self.request("DELETE", routes.DESTROY_PLAYER.format(sessionId=session_id, guildId=guild_id))
        
    async def update_session(self, session_id: str, data: dict) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        session_id: :class:`str`
            The session id for update session.
        data: :class:`dict`
            The data for update session.

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("PATCH", routes.UPDATE_SESSION.format(sessionId=session_id), data=data)
        return res

    async def version(self) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Returns
        -------
        :class:`dict`
            The response from the request.
        """
        res = await self.request("GET", routes.VERSION, without_version=True)
        return res

