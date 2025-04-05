
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
    def __init__(self, message: str, severity: str, cause:str) -> None:
        self._message = message
        self._severity = severity
        self._cause = cause

    @property
    def message(self):
        """
        A error message.
        """
        return self._message

    @property
    def severity(self):
        """
        A severity level. Can be one of: ```COMMON```, ```SUSPICIOUS``` , ```FAULT```.
        """
        return self._severity

class requestFailed(Exception):
    """
    A error for request failed.
    
    Parameters
    ----------
    timestamp: :class:`int`
        The timestamp of the error in milliseconds since the Unix epoch
    status: :class:`int`
        The HTTP status code
    error: :class:`str`
        The HTTP status code message
    message: :class:`str`
        The error message
    path: :class:`str`
        The request path
    trace: :class:`bool`
        The stack trace of the error when trace=true as query param has been sent
    """
    def __init__(self, timestamp: int, status: int, error: str, message: str, path: str, trace: bool = None) -> None:
        self._timestamp = timestamp
        self._status = status
        self._error = error
        self._message = message
        self._path = path
        self._trace = trace

    @property
    def timestamp(self):
        """
        The timestamp of the error in milliseconds since the Unix epoch
        """
        return self._timestamp
    
    @property
    def status(self):
        """
        The HTTP status code
        """
        return self._status
    
    @property
    def error(self):
        """
        The HTTP status code message
        """
        return self._error
    
    @property
    def message(self):
        """
        The error message
        """
        return self._message
    
    @property
    def path(self):
        """
        The request path
        """
        return self._path
    
    @property
    def trace(self):
        """
        The stack trace of the error when trace=true as query param has been sent
        """
        return self._trace
    
    def __str__(self):
        return f"{self._timestamp} {self._status} {self._error} {self._message} {self._path} {self._trace}"