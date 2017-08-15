import asyncio
import threading

import rocat.globals


def _executor_loop(executor):
    rocat.globals.g.executor = executor
    rocat.globals.g.loop = executor.loop
    asyncio.set_event_loop(executor.loop)
    executor.loop.run_forever()


class ActorExecutor(object):
    def __init__(self):
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=_executor_loop, args=[self])

    @property
    def loop(self):
        return self._loop

    @property
    def thread(self):
        return self._thread

    def start(self):
        self._thread.start()
