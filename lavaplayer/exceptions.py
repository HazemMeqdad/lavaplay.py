class NodeError(Exception):
    """
    A error for node.
    
    Parameters
    ----------
    message: :class:`str`
        the error message
    guild_id: :class:`int`
        the guild id
    """
    def __init__(self, message: str, guild_id: int) -> None:
        self._message = message
        self._guild_id = guild_id

    @property
    def message(self):
        """
        A error message.
        """
        return self._message
    
    @property
    def guild_id(self):
        """
        A guild id.
        """
        return self._guild_id


class FiltersError(Exception):
    """
    A error for all filters.

    Parameters
    ----------
    message: :class:`str`
        the error message
    """

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self):
        """
        A error message.
        """
        return self._message


class VolumeError(Exception):
    """
    A error for volume range if not in 0 to 1000.
    
    Parameters
    ----------
    message: :class:`str`
        the error message
    guild_id: :class:`int`
        the guild id
    """
    def __init__(self, message: str, guild_id) -> None:
        self._message = message
        self._guild_id = guild_id

    @property
    def message(self):
        """
        A error message.
        """
        return self._message

    @property
    def guild_id(self):
        """
        A guild id.
        """
        return self._guild_id


class NotConnectedError(Exception):
    """
    A error for not connected.
    
    Parameters
    ----------
    message: :class:`str`
        the error message
    """
    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self):
        """
        A error message.
        """
        return self._message


class ConnectedError(Exception):
    """
    A error for connected.
    """
    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self):
        """
        A error message.
        """
        return self._message


class TrackLoadFailed(Exception):
    """
    A error for track load failed.
    
    Parameters
    ----------
    message: :class:`str`
        the error message
    severity: :class:`str`
        gets the severity level of the track loading failure
    """
    def __init__(self, message: str, severity: str) -> None:
        self._message = message
        self._severity = severity

    @property
    def message(self):
        """
        A error message.
        """
        return self._message

    @property
    def severity(self):
        """
        A severity level. Can be one of: ``'CRITICAL'``, ``'ERROR'``, ``'WARNING'``, ``'INFO'``, ``'DEBUG'``. 
        """
        return self._severity
