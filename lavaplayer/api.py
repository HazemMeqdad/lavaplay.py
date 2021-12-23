from typing import Any
import aiohttp


class Api:
    def __init__(self,host: str, port: int, password: str, is_ssl: bool = False) -> None:
        self.rest_uri = f"{'https' if is_ssl else 'http'}://{host}:{port}"
        self.herders = {
            "Host": f"{host}:{port}",
            "Authorization": password
        }
    
    async def request(self, method: str, rout: str, data: dict = {}) -> dict:
        async with aiohttp.ClientSession(headers=self.herders) as session:
            async with session.request(method, self.rest_uri+rout, data=data) as resp:
                return await resp.json()
        



