import asyncio

import rocat.message
import rocat.actor
import rocat.globals


class BaseActorRef(object):
    def tell(self, m, *, sender=None):
        raise NotImplementedError

    def ask(self, m, *, sender=None):
        raise NotImplementedError


class LocalActorRef(BaseActorRef):
    def __init__(self, q, loop):
        self.q = q
        self.loop = loop

    def tell(self, m, *, sender=None):
        if sender is None:
            sender = _guess_current_sender()
        envel = rocat.message.Envelope(m, sender=sender)
        self.loop.call_soon_threadsafe(self.q.put_nowait, envel)

    async def ask(self, m, *, sender=None):
        fut = asyncio.get_event_loop().create_future()
        if sender is None:
            sender = FunctionRef(fut, asyncio.get_event_loop())
        self.tell(m, sender=sender)
        envel = await fut
        return envel.msg


class FunctionRef(BaseActorRef):
    def __init__(self, fut, loop):
        self.fut = fut
        self.loop = loop

    def tell(self, m, *, sender=None):
        if sender is None:
            sender = _guess_current_sender()
        envel = rocat.message.Envelope(m, sender=sender)
        self.loop.call_soon_threadsafe(self.fut.set_result, envel)

    def ask(self, m, *, sender=None):
        raise NotImplementedError


def _guess_current_sender():
    current_ctx = rocat.actor.ActorContext.current()
    if current_ctx is not None:
        return current_ctx.sender
