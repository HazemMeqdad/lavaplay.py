import asyncio
import typing as t
from collections import deque
import logging
from .objects import Event

_LOGGER = logging.getLogger("lavaplayer.event_manger")

class Emitter:
    """
    The class is a manger event from websocket.

    Parameters
    ---------
    loop: :class:`AbstractEventLoop`
        a loop event from asyncio
    """
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self.listeners = deque()
    
    def add_listener(self, event: t.Union[str, Event], func: t.Callable):
        """
        Add listener for listeners list.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        func: :class:`function`
            the function to callback event
        """
        _LOGGER.debug(f"add listener {event}")
        event = event if isinstance(event, str) else event.__name__
        self.listeners.append({"event": event, "func": func})

    def remove_listener(self, event: t.Union[str, Event], func: t.Callable):
        """
        Remove listener for listeners list.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        func: :class:`function`
            the function to callback event
        """
        _LOGGER.debug(f"remove listener {event}")
        event = event if isinstance(event, str) else event.__name__
        self.listeners.remove([i for i in self.listeners if i["event"] == event and i["func"] == func])

    def emit(self, event: t.Union[str, t.Any], data: t.Any):
        """
        Emit for event dont use this.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        data: :class:`function`
            the data is revers to function callback
        """
        event = event if isinstance(event, str) else event.__name__
        events = [i for i in self.listeners if i["event"] == event]
        for event in events:
            _LOGGER.debug(f"dispatch {event} for {len(events)} listeners")
            if asyncio.iscoroutinefunction(event["func"]):
                self._loop.create_task(event["func"](data))
            else:
                _LOGGER.error("Events only async function")
