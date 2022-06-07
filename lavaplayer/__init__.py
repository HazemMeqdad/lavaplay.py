"""
Lavalink connecter
~~~~~~~~~~~~~~~
:copyright: (c) 2021 HazemMeqdad
:license: MIT, see LICENSE for more details.
"""

__title__ = "lavaplayer"
__author__ = "HazemMeqdad"
__license__ = "MIT"
__version__ = "1.0.9a"

from .client import LavalinkClient, Lavalink
from .objects import (
    Info, Track, Node, ConnectionInfo,
    PlayList, Event, TrackStartEvent, TrackEndEvent,
    TrackExceptionEvent, TrackStuckEvent, WebSocketClosedEvent,
    PlayerUpdateEvent, ErrorEvent, Filters
)
from .api import Api
from .exceptions import (
    NodeError, FiltersError, VolumeError,
    NotConnectedError, ConnectedError, TrackLoadFailed
)
