from lavaplayer.emitter import Emitter
import asyncio

emitter = Emitter(asyncio.get_event_loop())


def test_add_listener():
    emitter.add_listener("test", lambda: None)
    assert emitter.listeners is not None

def test_remove_listener():
    func = lambda: None
    emitter.add_listener("test", func)
    emitter.remove_listener("test", func)
    assert emitter.listeners is None

def test_emit():
    emitter.add_listener("test", lambda: None)
    emitter.emit("test", None)
