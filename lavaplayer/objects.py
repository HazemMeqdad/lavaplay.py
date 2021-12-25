from __future__ import annotations
from dataclasses import dataclass
from typing import Any

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
    requester: int | None = None

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
    position: int | None
    connected: bool


@dataclass
class Node:
    guild_id: int
    queue: list[Track]
    volume: int
    is_pasue: bool = False
    repeat: bool = False


@dataclass(init=True)
class Filters:
    def __init__(self, volume: int | float = 1.0) -> None:
        self._pyload: dict = {"op": "filters","volume": volume}
    
    def equalizer(self, band: int | float, gain: int | float):
        self._pyload["equalizer"] = [{"band": band, "gain": gain}]
    
    def karaoke(self, level: int | float, mono_level: int | float, filter_band: int | float, filter_width: int | float):
        self._pyload["karaoke"] = {"level": level, "monoLevel": mono_level, "filterBand": filter_band, "filterWidth": filter_width}
    
    def timescale(self, speed: int | float, pitch: int | float, rate: int | float):
        self._pyload["timescale"] = {"speed": speed, "pitch": pitch, "rate": rate}
    
    def tremolo(self, frequency: int | float, depth: int | float):
        self._pyload["tremolo"] = {"frequency": frequency, "depth": depth}
    
    def vibrato(self, frequency: int | float, depth: int | float):
        self._pyload["vibrato"] = {"frequency": frequency, "depth": depth}
    
    def rotation(self, rotation_hz: int | float):
        self._pyload["rotation"] = {"rotationHz": rotation_hz}

    def distortion(self, sin_offset: int | float, sin_scale: int | float, cos_offset: int | float,cos_scale: int | float, tan_offset: int | float, tan_scale: int | float,  offset: int | float, scale: int | float):
        self._pyload["distortion"] = {"sinOffset": sin_offset, "sinScale": sin_scale, "cosOffset": cos_offset, "cosScale": cos_scale, "tanOffset": tan_offset, "tanScale": tan_scale, "offset": offset, "scale": scale}

    def channel_mix(self, left_to_left: int | float, left_to_right: int | float, right_to_left: int | float, right_to_right: int | float):
        self._pyload["channelMix"] = {"leftToLeft": left_to_left, "leftToRight": left_to_right, "rightToLeft": right_to_left,"rightToRight": right_to_right}

    def lowPass(self, smoothing: int | float):
        self._pyload["lowPass"] = {"smoothing": smoothing}

