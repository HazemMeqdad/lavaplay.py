from __future__ import annotations
import asyncio
from typing import Any
from collections import deque
import logging

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
    
    def add_listner(self, event: str | Any, func: function):
        """
        Add listner for listeners list.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        func: :class:`function`
            the function to callback event
        """
        event = event if isinstance(event, str) else event.__name__
        self.listeners.append({"event": event, "func": func})

    def remove_listner(self, event: str | Any, func: function):
        """
        Remove listner for listeners list.

        Parameters
        ---------
        event: :class:`str` | :class:`Any`
            event name or class for event
        func: :class:`function`
            the function to callback event
        """
        event = event if isinstance(event, str) else event.__name__
        self.listeners.remove([i for i in self.listeners if i["event"] == event and i["func"] == func])

    def emit(self, event: str | Any, data: Any):
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
            if asyncio.iscoroutinefunction(event["func"]):
                self._loop.create_task(event["func"](data))
            else:
                logging.error("events only async func, you can't use sync -_-")

