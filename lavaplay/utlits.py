import random
import asyncio
import logging
import typing as t
from .objects import Track

_LOG = logging.getLogger("lavaplay.utils")

def generate_resume_key():
    "For lavalink V3"
    return "".join(random.choice("0123456789abcdef") for _ in range(16))


def get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def prossing_tracks(tracks: list, result: str) -> t.List[Track]:
    list_tracks = []
    for track in tracks:
        info = track["info"]
        encoded = track.get("encoded")

        list_tracks.append(
            Track(
                encoded=encoded,
                identifier=info["identifier"],
                is_seekable=info["isSeekable"],
                author=info["author"],
                length=info["length"],
                is_stream=info["isStream"],
                position=info["position"],
                title=info["title"],
                uri=info["uri"],
                artworkUrl=info.get("artworkUrl", None),
                isrc=info.get("isrc", None),
                plugin_info=track["pluginInfo"],
                load_type=result.get("loadType", None)
            )
        )
    return list_tracks


def prossing_single_track(track: dict, result: str) -> t.List[Track]:
    """
    To process one track from payload to Track object.

    Parameters
    ----------
    track: :class:`list`
        The track.
    """
    info = track["info"]
    return [Track(
        encoded=track["encoded"],
        identifier=info["identifier"],
        is_seekable=info["isSeekable"],
        author=info["author"],
        length=info["length"],
        is_stream=info["isStream"],
        position=info["position"],
        source_name=info.get("sourceName", None),
        title=info.get("title", None),
        uri=info["uri"],
        artworkUrl=info.get("artworkUrl", None),
        isrc=info.get("isrc", None),
        plugin_info=track["pluginInfo"],
        load_type=result.get("loadType", None)
    )]


def event_track(track: dict):
    """
    To process one track from payload to Track object.

    Parameters
    ----------
    track: :class:`list`
        The track.
    """
    info = track["info"]
    return [Track(
        encoded=track["encoded"],
        identifier=info["identifier"],
        is_seekable=info["isSeekable"],
        author=info["author"],
        length=info["length"],
        is_stream=info["isStream"],
        position=info["position"],
        source_name=info.get("sourceName", None),
        title=info.get("title", None),
        uri=info["uri"],
        artworkUrl=info.get("artworkUrl", None),
        isrc=info.get("isrc", None),
        plugin_info=track["pluginInfo"],
        load_type=track.get("loadType", None)
    )]

