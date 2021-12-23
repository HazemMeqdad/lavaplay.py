from __future__ import annotations
import asyncio
from typing import Any
from collections import deque
import logging

class Emitter:
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self.listeners = deque()
    
    def add_listner(self, event: str | Any, func: function, once: bool = False):
        event = event if isinstance(event, str) else event.__name__
        self.listeners.append({"event": event, "func": func, "once": once})

    def remove_listner(self, event: str | Any, func: function):
        event = event if isinstance(event, str) else event.__name__
        self.listeners.remove([i for i in self.listeners if i["event"] == event and i["func"] == func])

    def emit(self, event: str | Any, data: Any):
        event = event if isinstance(event, str) else event.__name__
        events = [i for i in self.listeners if i["event"] == event]
        for event in events:
            if event["once"]:
                self.listeners.remove([event])
            if asyncio.iscoroutinefunction(event["func"]):
                self._loop.create_task(event["func"](data))
            else:
                logging.error("events only async func, you can't use sync -_-")

