from lavaplayer.objects import Info, Track, Node, ConnectionInfo
import pytest

@pytest.mark.parametrize("info", [Info(1, 2, 3, 4, 5)])
def test_info(info: Info):
    assert info.playing_players == 1
    assert info.memory_used == 2
    assert info.memory_free == 3
    assert info.players == 4
    assert info.uptime == 5

@pytest.mark.parametrize("track", [Track("track", "identifier", True, "author", 1, True, 2, "title", "uri")])
def test_track(track: Track):
    assert track.track == "track"
    assert track.identifier == "identifier"
    assert track.is_seekable == True
    assert track.author == "author"
    assert track.length == 1
    assert track.is_stream == True
    assert track.position == 2
    assert track.title == "title"
    assert track.uri == "uri"