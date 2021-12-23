from dataclasses import dataclass


@dataclass
class Info:
    playingPlayers: int
    memory_used: int
    memory_free: int
    players: int
    uptime: int


@dataclass
class Track:
    track: str
    identifier: str
    isSeekable: bool
    author: str
    length: int
    isStream: bool
    position: int
    sourceName: str
    title: str
    uri: str

    def __repr__(self) -> str:
        return self.title

@dataclass
class TrackStartEvent:
    track: Track
    guild_id: int

@dataclass
class TrackEndEvent:
    track: Track
    guild_id: int
    reason: str

@dataclass
class TrackExceptionEvent:
    track: Track
    guild_id: int
    exception: str
    message: str
    severity: str
    cause: str


@dataclass
class TrackStuckEvent:
    track: Track
    guild_id: int
    thresholdMs: str


@dataclass
class WebSocketClosedEvent:
    track: Track
    guild_id: int
    code: int
    reason: str
    byRemote: bool


@dataclass
class PlayerUpdate:
    guild_id: int
    time: int
    position: int
    connected: bool



