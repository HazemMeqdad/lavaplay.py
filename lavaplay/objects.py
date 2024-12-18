from dataclasses import dataclass
from .exceptions import FiltersError
import typing as t
from inspect import signature

# https://stackoverflow.com/questions/55099243/python3-dataclass-with-kwargsasterisk
class BaseObject:
    @classmethod
    def from_kwargs(cls, **kwargs):
        # fetch the constructor's signature
        cls_fields = {field for field in signature(cls).parameters}

        # split the kwargs into native ones and new ones
        native_args, new_args = {}, {}
        for name, val in kwargs.items():
            if name in cls_fields:
                native_args[name] = val
            else:
                new_args[name] = val

        # use the native ones to create the class ...
        ret = cls(**native_args)

        # ... and add the new ones by hand
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)
        return ret

@dataclass
class Memory(BaseObject):
    free: int
    used: int
    allocated: int
    reservable: int

@dataclass
class Cpu(BaseObject):
    cores: int
    systemLoad: float
    lavalinkLoad: float

@dataclass
class FrameStats(BaseObject):
    sent: int
    nulled: int
    deficit: int

@dataclass
class Stats(BaseObject):
    """
    Info websocket for connection
    """
    players: int
    playingPlayers: int
    uptime: int
    memory: Memory
    cpu: Cpu
    frameStats: t.Optional[FrameStats] = None


@dataclass(repr=True)
class Track(BaseObject):
    """
    Info track object.
    """
    encoded: str
    identifier: str
    is_seekable: bool
    author: str
    length: int
    is_stream: bool
    position: int
    title: str
    uri: str
    artworkUrl: str
    isrc: str
    plugin_info: str
    load_type: str
    requester: t.Union[str, None] = None
    source_name: t.Optional[str] = None
    timestamp: t.Optional[t.Any] = None
    """
    optional option to save a requester for the track
    """

    def __repr__(self) -> str:
        return self.title

@dataclass
class ConnectionInfo(BaseObject):
    """
    A info for Connection just use to save the connection information.
    """
    guild_id: int
    session_id: str
    channel_id: t.Optional[int]


@dataclass
class PlayList(BaseObject):
    name: str
    selected_track: int
    tracks: t.List[Track]

@dataclass
class PlayerState(BaseObject):
    """
    Event on player update.
    """
    time: int
    connected: bool
    ping: int
    position: t.Optional[int] = None

@dataclass
class Version(BaseObject):
    """
    Version info
    """
    semver: str
    major: int
    minor: int
    patch: int
    preRelease: str = None
    build: str = None

@dataclass
class Git(BaseObject):
    """
    Git info
    """
    branch: str
    commit: str
    commitTime: int

@dataclass
class Plugin(BaseObject):
    """
    Plugin info
    """
    name: str
    version: str

@dataclass
class Info(BaseObject):
    """
    
    """
    version: Version
    buildTime: int
    git: Git
    jvm: str
    lavaplayer: str
    sourceManagers: t.List[str]
    filters: t.List[str]
    plugins: t.List[Plugin]

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
        self._payload: dict = {"op": "filters", "volume": volume}
    
    def equalizer(self, bands: t.List[t.Tuple[int, t.Union[float, int]]]):
        """
        There are 15 bands (0-14) that can be changed.

        "gain" is the multiplier for the given band. The default value is 0. Valid values range from -0.25 to 1.0,
        where -0.25 means the given band is completely muted, and 0.25 means it is doubled. Modifying the gain could
        also change the volume of the output.
        """
        update_list = []
        for v in bands:
            if not -1 < v[0] < 15:
                raise FiltersError("Invalid band, must be 0-14")
            gain = max(min(float(v[1]), 1.0), -0.25)
            band = v[1]
            update_list.append({'band': band, 'gain': gain})
        self._payload["equalizer"] = update_list
    
    def karaoke(self, level: t.Union[int, float], mono_level: t.Union[int, float], filter_band: t.Union[int, float], filter_width: t.Union[int, float]):
        """
        Uses equalization to eliminate part of a band, usually targeting vocals.
        """
        self._payload["karaoke"] = {"level": level, "monoLevel": mono_level, "filterBand": filter_band, "filterWidth": filter_width}
    
    def timescale(self, speed: t.Union[int, float], pitch: t.Union[int, float], rate: t.Union[int, float]):
        """
        Changes the speed, pitch, and rate. All default to 1.
        """
        self._payload["timescale"] = {"speed": speed, "pitch": pitch, "rate": rate}
    
    def tremolo(self, frequency: t.Union[int, float], depth: t.Union[int, float]):
        """
        Uses amplification to create a shuddering effect, where the volume quickly oscillates.
        Example: https://en.wikipedia.org/wiki/File:Fuse_Electronics_Tremolo_MK-III_Quick_Demo.ogv
        """
        self._payload["tremolo"] = {"frequency": frequency, "depth": depth}
    
    def vibrato(self, frequency: t.Union[int, float], depth: t.Union[int, float]):
        """
        Similar to tremolo. While tremolo oscillates the volume, vibrato oscillates the pitch.
        """
        self._payload["vibrato"] = {"frequency": frequency, "depth": depth}
    
    def rotation(self, rotation_hz: t.Union[int, float]):
        """
        Rotates the sound around the stereo channels/user headphones aka Audio Panning.
        It can produce an effect similar to: https://youtu.be/QB9EB8mTKcc (without the reverb)
        """
        self._payload["rotation"] = {"rotationHz": rotation_hz}

    def distortion(self, sin_offset: t.Union[int, float], sin_scale: t.Union[int, float], cos_offset: t.Union[int, float], cos_scale: t.Union[int, float], tan_offset: t.Union[int, float], tan_scale: t.Union[int, float], offset: t.Union[int, float], scale: t.Union[int, float]):
        """
        Distortion effect. It can generate some pretty unique audio effects.
        """
        self._payload["distortion"] = {"sinOffset": sin_offset, "sinScale": sin_scale, "cosOffset": cos_offset, "cosScale": cos_scale, "tanOffset": tan_offset, "tanScale": tan_scale, "offset": offset, "scale": scale}

    def channel_mix(self, left_to_left: t.Union[int, float], left_to_right: t.Union[int, float], right_to_left: t.Union[int, float], right_to_right: t.Union[int, float]):
        """
        Mixes both channels (left and right), with a configurable factor on how much each channel affects the other.

        With the defaults, both channels are kept independent from each other.

        Setting all factors to 0.5 means both channels get the same audio.
        """
        self._payload["channelMix"] = {"leftToLeft": left_to_left, "leftToRight": left_to_right, "rightToLeft": right_to_left, "rightToRight": right_to_right}

    def low_pass(self, smoothing: t.Union[int, float]):
        """
        Higher frequencies get suppressed, while lower frequencies pass through this filter, thus the name low pass.
        """
        self._payload["lowPass"] = {"smoothing": smoothing}

    def plugin_filters(self, map: dict):
        """
        Filter plugin configurations
        """
        self._payload["pluginFilters"] = map
