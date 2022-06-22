import aiohttp
from . import routes
import logging


_LOGGER = logging.getLogger(__name__)


class LavalinkRest:
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
        return await self.request("GET", routes.LOADTRACKS.format(query=query))

    async def decode_track(self, track: str) -> dict:
        """
        Decode a single track into its real info

        Parameters
        ---------
        track: :class:`str`
            track base64 encoded text for request like `ytsearch:`
        """
        return await self.request("GET", routes.DECODETRACK, data={"track": track})

    async def decode_tracks(self, tracks: list) -> list:
        """
        Decode a multiple track into their real info.

        Parameters
        ---------
        tracks: :class:`list`
            list of tracks base64 encoded text for request like `ytsearch:`
        """
        return await self.request("POST", routes.DECODETRACKS, data={"tracks": tracks})

    async def route_planner_status(self) -> dict:
        """
        This function makes a request to the rest api for lavalink.
        """
        return await self.request("GET", routes.ROUTEPLANNER)
    
    async def route_planner_free_address(self, address: str) -> dict:
        """
        """
        return await self.request("GET", routes.UNMARK_FAILED_ADDRESS.format(address=address))
    
    async def route_planner_free_all(self) -> dict:
        """
        """
        return await self.request("GET", routes.UNMARK_ALL_FAILED_ADDRESS)
    

class Api(LavalinkRest):
    """
    Inherit from :class:`LavalinkRest`, ill remove it later.
    """
