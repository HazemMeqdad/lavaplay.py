from dataclasses import dataclass
import typing as t

@dataclass
class Info:
    """
    Info websocket for connection
    """
    playing_players: int
    memory_used: int
    memory_free: int
    players: int
    uptime: int


@dataclass
class Track:
    """
    Info track
    """
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
    requester: t.Union[str, None] = None

    def __repr__(self) -> str:
        return self.title

@dataclass
class TrackStartEvent:
    """
    None
    """
    track: Track
    guild_id: int

@dataclass
class TrackEndEvent:
    """
    None
    """
    track: Track
    guild_id: int
    reason: str

@dataclass
class TrackExceptionEvent:
    """
    None
    """
    track: Track
    guild_id: int
    exception: str
    message: str
    severity: str
    cause: str


@dataclass
class TrackStuckEvent:
    """
    None
    """
    track: Track
    guild_id: int
    thresholdMs: str


@dataclass
class WebSocketClosedEvent:
    """
    None
    """
    track: Track
    guild_id: int
    code: int
    reason: str
    byRemote: bool


@dataclass
class PlayerUpdate:
    """
    None
    """
    guild_id: int
    time: int
    position: t.Union[int, None]
    connected: bool


@dataclass
class Node:
    """
    The node is saved the queue guild list and volume and etc information.
    """
    guild_id: int
    queue: t.List[Track]
    volume: int
    is_pasue: bool = False
    repeat: bool = False


@dataclass(init=True)
class Filters:
    """
    All the filters are optional, and leaving them out of this message will disable them.

    Adding a filter can have adverse effects on performance. These filters force Lavaplayer to decode all audio to PCM, even if the input was already in the Opus format that Discord uses. This means decoding and encoding audio that would normally require very little processing. This is often the case with YouTube videos.
    
    Parameters
    ---------
    volume: :class:`int` | :class:`float`
        Float value where 1.0 is 100%. Values >1.0 may cause clipping
    """
    def __init__(self, volume: t.Union[int, float] = 1.0) -> None:
        self._pyload: dict = {"op": "filters","volume": volume}
    
    def equalizer(self, band: t.Union[int, float], gain: t.Union[int, float]):
        """
        There are 15 bands (0-14) that can be changed.

        "gain" is the multiplier for the given band. The default value is 0. Valid values range from -0.25 to 1.0,
        where -0.25 means the given band is completely muted, and 0.25 means it is doubled. Modifying the gain could
        also change the volume of the output.
        """
        self._pyload["equalizer"] = [{"band": band, "gain": gain}]
    
    def karaoke(self, level: t.Union[int, float], mono_level: t.Union[int, float], filter_band: t.Union[int, float], filter_width: t.Union[int, float]):
        """
        Uses equalization to eliminate part of a band, usually targeting vocals.
        """
        self._pyload["karaoke"] = {"level": level, "monoLevel": mono_level, "filterBand": filter_band, "filterWidth": filter_width}
    
    def timescale(self, speed: t.Union[int, float], pitch: t.Union[int, float], rate: t.Union[int, float]):
        """
        Changes the speed, pitch, and rate. All default to 1.
        """
        self._pyload["timescale"] = {"speed": speed, "pitch": pitch, "rate": rate}
    
    def tremolo(self, frequency: t.Union[int, float], depth: t.Union[int, float]):
        """
        Uses amplification to create a shuddering effect, where the volume quickly oscillates.
        Example: https://en.wikipedia.org/wiki/File:Fuse_Electronics_Tremolo_MK-III_Quick_Demo.ogv
        """
        self._pyload["tremolo"] = {"frequency": frequency, "depth": depth}
    
    def vibrato(self, frequency: t.Union[int, float], depth: t.Union[int, float]):
        """
        Similar to tremolo. While tremolo oscillates the volume, vibrato oscillates the pitch.
        """
        self._pyload["vibrato"] = {"frequency": frequency, "depth": depth}
    
    def rotation(self, rotation_hz: t.Union[int, float]):
        """
        Rotates the sound around the stereo channels/user headphones aka Audio Panning. 
        It can produce an effect similar to: https://youtu.be/QB9EB8mTKcc (without the reverb)
        """
        self._pyload["rotation"] = {"rotationHz": rotation_hz}

    def distortion(self, sin_offset: t.Union[int, float], sin_scale: t.Union[int, float], cos_offset: t.Union[int, float],cos_scale: t.Union[int, float], tan_offset: t.Union[int, float], tan_scale: t.Union[int, float],  offset: t.Union[int, float], scale: t.Union[int, float]):
        """
        Distortion effect. It can generate some pretty unique audio effects.
        """
        self._pyload["distortion"] = {"sinOffset": sin_offset, "sinScale": sin_scale, "cosOffset": cos_offset, "cosScale": cos_scale, "tanOffset": tan_offset, "tanScale": tan_scale, "offset": offset, "scale": scale}

    def channel_mix(self, left_to_left: t.Union[int, float], left_to_right: t.Union[int, float], right_to_left: t.Union[int, float], right_to_right: t.Union[int, float]):
        """
        Mixes both channels (left and right), with a configurable factor on how much each channel affects the other.

        With the defaults, both channels are kept independent from each other.

        Setting all factors to 0.5 means both channels get the same audio.
        """
        self._pyload["channelMix"] = {"leftToLeft": left_to_left, "leftToRight": left_to_right, "rightToLeft": right_to_left,"rightToRight": right_to_right}

    def low_pass(self, smoothing: t.Union[int, float]):
        """
        Higher frequencies get suppressed, while lower frequencies pass through this filter, thus the name low pass.
        """
        self._pyload["lowPass"] = {"smoothing": smoothing}

