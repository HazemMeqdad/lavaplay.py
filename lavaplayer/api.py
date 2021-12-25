import aiohttp


class Api:
    """
    The class make a request to the rest api for lavalink

    Parameters
    ---------
    host: :class:`str`
        ip address for lavalink server, default ip address for lavalink is ``127.0.0.1``
    port: :class:`int`
        The port to use for websocket and REST connections.
    password: :class:`str`
        The password used for authentication.
    is_ssl: :class:`bool`
        Is server using ssl
    """
    def __init__(self, *, host: str = "127.0.0.1", port: int, password: str, is_ssl: bool = False) -> None:
        self.rest_uri = f"{'https' if is_ssl else 'http'}://{host}:{port}"
        self.herders = {
            "Host": f"{host}:{port}",
            "Authorization": password
        }
    
    async def request(self, method: str, rout: str, data: dict = {}) -> dict:
        """
        This function make arequest to the rest api for lavalink

        Parameters
        ---------
        method: :class:`str`
            method for request like `GET` or `POST` etc.
        rout: :class:`str`
            rout from request like `/loadtracks`
        data: :class:`dict`
            data for request
        """
        async with aiohttp.ClientSession(headers=self.herders) as session:
            async with session.request(method, self.rest_uri+rout, data=data) as resp:
                return await resp.json()
        



