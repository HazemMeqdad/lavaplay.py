import aiohttp
from . import routes
import logging


_LOGGER = logging.getLogger(__name__)

# TODO: add docstring
class LavalinkRest:
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
    """
    def __init__(self, *, host: str = "127.0.0.1", port: int, password: str, is_ssl: bool = False) -> None:
        self.rest_uri = f"{'https' if is_ssl else 'http'}://{host}:{port}"
        self.headers = {
            "Host": f"{host}:{port}",
            "Authorization": password
        }

    async def request(self, method: str, rout: str, data: dict = {}) -> dict:
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
        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.rest_uri + rout, headers=self.headers, json=data) as response:
                _LOGGER.debug(f"{method} {self.rest_uri + rout}")
                return await response.json()

class LavalinkRestOld:
    """
    The class make a request to the rest api for lavalink.

    Parameters
    ---------
    host: :class:`str`
        ip address for lavalink server, default ip address for lavalink is ``127.0.0.1`.
    port: :class:`int`
        The port to use for websocket and REST connections.
    password: :class:`str`
        The password used for authentication.
    is_ssl: :class:`bool`
        Is server using ssl.
    """
    def __init__(self, *, host: str = "127.0.0.1", port: int, password: str, is_ssl: bool = False) -> None:
        self.rest_uri = f"{'https' if is_ssl else 'http'}://{host}:{port}"
        self.headers = {
            "Host": f"{host}:{port}",
            "Authorization": password
        }
    
    async def request(self, method: str, rout: str, data: dict = {}) -> dict:
        """
        This function makes a request to the rest api for lavalink

        Parameters
        ---------
        method: :class:`str`
            method for request like `GET` or `POST` etc.
        rout: :class:`str`
            rout from request like `/loadtracks`
        data: :class:`dict`
            data for request
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.request(method, self.rest_uri + rout, data=data) as resp:
                _LOGGER.debug(f"{method} {self.rest_uri + rout}")
                return await resp.json()

    async def load_tracks(self, query: str) -> list:
        """
        The REST api is used to resolve audio tracks for use with the play function :meth:`lavaplayer.Lavalink.play`.

        Parameters
        ---------
        query: :class:`str`
            query for request like `ytsearch:{query}`
        """
        return await self.request("GET", routes.OldRoutes.LOADTRACKS.format(query=query))

    async def decode_track(self, track: str) -> dict:
        """
        Decode a single track into its real info

        Parameters
        ---------
        track: :class:`str`
            track base64 encoded text for request like `ytsearch:`
        """
        return await self.request("GET", routes.OldRoutes.DECODETRACK, data={"track": track})

    async def decode_tracks(self, tracks: list) -> list:
        """
        Decode a multiple track into their real info.

        Parameters
        ---------
        tracks: :class:`list`
            list of tracks base64 encoded text for request like `ytsearch:`
        """
        return await self.request("POST", routes.OldRoutes.DECODETRACKS, data={"tracks": tracks})

    async def route_planner_status(self) -> dict:
        """
        This function makes a request to the rest api for lavalink.
        """
        return await self.request("GET", routes.OldRoutes.ROUTEPLANNER)
    
    async def route_planner_free_address(self, address: str) -> dict:
        """
        """
        return await self.request("GET", routes.OldRoutes.UNMARK_FAILED_ADDRESS.format(address=address))
    
    async def route_planner_free_all(self) -> dict:
        """
        """
        return await self.request("GET", routes.OldRoutes.UNMARK_ALL_FAILED_ADDRESS)
    
    async def plugins(self) -> dict:
        """
        """
        return await self.request("GET", routes.OldRoutes.PLUGINS)

class Api(LavalinkRest):
    """
    Inherit from :class:`LavalinkRest`, ill remove it later.
    """
