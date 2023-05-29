from .objects import BaseObject, Stats, Track, PlayerState
from dataclasses import dataclass
import typing as t

class Event(BaseObject):
    """
    The class is a base event for websocket.
    """

@dataclass
class ReadyEvent(Event):
    """
    Event on ready. call when the websocket is ready.
    """
    resumed: bool
    sessionId: str

@dataclass
class StatsUpdateEvent(Event):
    """
    Event on stats update.
    """
    stats: Stats

@dataclass
class TrackStartEvent(Event):
    """
    Event on track start.
    """
    track: Track
    guild_id: int


@dataclass
class TrackEndEvent(Event):
    """
    Event on track end.
    """
    track: Track
    guild_id: int
    reason: str

@dataclass
class TrackException(Event):
    """
    Event on exception.
    """
    severity: t.Optional[str]
    cause: t.Optional[str]
    message: t.Optional[str] = None

@dataclass
class TrackExceptionEvent(Event):
    """
    Event on track exception.
    """
    track: Track
    guild_id: int
    exception: TrackException




@dataclass
class TrackStuckEvent(Event):
    """
    Event on track stuck.
    """
    track: Track
    guild_id: int
    thresholdMs: str


@dataclass
class WebSocketClosedEvent(Event):
    """
    Event on websocket closed.
    """
    guild_id: int
    code: int
    reason: str
    byRemote: bool

@dataclass
class PlayerUpdateEvent(Event):
    """
    Event on player update.
    """
    guildId: int
    state: PlayerState

@dataclass
class ErrorEvent(Event):
    """
    Event on error.
    """
    guild_id: int
    exception: Exception
