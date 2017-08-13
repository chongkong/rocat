import asyncio

import rocat.message


class BaseActorRef(object):
    def tell(self, m, *, sender):
        raise NotImplementedError

    def ask(self, m, *, sender):
        raise NotImplementedError


class LocalActorRef(BaseActorRef):
    def __init__(self, q, loop):
        self.q = q
        self.loop = loop

    def tell(self, m, *, sender):
        envel = rocat.message.Envelope(m, sender=sender)
        self.loop.call_soon_threadsafe(self.q.put_nowait, envel)

    async def ask(self, m, *, sender):
        fut = asyncio.get_event_loop().create_future()
        self.tell(m, sender=FunctionRef(fut, asyncio.get_event_loop()))
        envel = await fut
        return envel.msg


class FunctionRef(BaseActorRef):
    def __init__(self, fut, loop):
        self.fut = fut
        self.loop = loop

    def tell(self, m, *, sender):
        envel = rocat.message.Envelope(m, sender=sender)
        self.loop.call_soon_threadsafe(self.fut.set_result, envel)

    def ask(self, m, *, sender):
        raise NotImplementedError
