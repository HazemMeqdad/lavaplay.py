
class NotFindNode(Exception):
    def __init__(self, guild_id: int) -> None:
        self._message = f"i can't find node for `{guild_id}` guild"
        self._guild_id = guild_id

    @property
    def message(self):
        return self._message
    
    @property
    def guild_id(self):
        return self._guild_id
