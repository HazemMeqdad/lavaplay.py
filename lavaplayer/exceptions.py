
class NodeError(Exception):
    def __init__(self, message: str, guild_id: int) -> None:
        self._message = message
        self._guild_id = guild_id

    @property
    def message(self):
        return self._message
    
    @property
    def guild_id(self):
        return self._guild_id


class VolumeError(Exception):
    def __init__(self, message: str, guild_id) -> None:
        self._message = message
        self._guild_id = guild_id

    @property
    def message(self):
        return self._message

    @property
    def guild_id(self):
        return self._guild_id


class NotConnectedError(Exception):
    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self):
        return self._message


class ConnectedError(Exception):
    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self):
        return self._message
