import random
import asyncio
import typing as t
from .objects import Track

def generate_resume_key():
    return "".join(random.choice("0123456789abcdef") for _ in range(16))


def get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def prossing_tracks(tracks: list) -> t.List[Track]:
    """
    To process list of tracks from payload to Track object.

    Parameters
    ----------
    tracks: :class:`list`
        List of tracks.
    """
    list_tracks = []
    for track in tracks:
        info = track["info"]
        list_tracks.append(
            Track(
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
                artworkUrl=info["artworkUrl"],
                isrc=info["isrc"]
            )
        )
    return list_tracks


def prossing_single_track(track: dict) -> t.List[Track]:
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
        artworkUrl=info["artworkUrl"],
        isrc=info["isrc"]
    )]
