import asyncio

import rocat.message
import rocat.actor
import rocat.globals


class BaseActorRef(object):
    def tell(self, m, *, sender=None):
        raise NotImplementedError

    def ask(self, m, *, timeout=None):
        raise NotImplementedError

    def error(self, e):
        raise NotImplementedError


class LocalActorRef(BaseActorRef):
    def __init__(self, q, loop):
        self._q = q
        self._loop = loop

    def _send(self, envel):
        self._loop.call_soon_threadsafe(self._q.put_nowait, envel)

    def tell(self, m, *, sender=None):
        if sender is None:
            sender = _guess_current_sender()
        self._send(rocat.message.Envelope.for_tell(m, sender=sender))

    async def ask(self, m, *, timeout=None):
        fut = asyncio.get_event_loop().create_future()
        sender = FunctionRef(fut, asyncio.get_event_loop())

        self._send(rocat.message.Envelope.for_ask(m, sender=sender))

        if timeout is None:
            timeout = _guess_default_timeout()
        if timeout > 0:
            reply = await asyncio.wait_for(fut, timeout)
        else:
            reply = await fut

        if reply.is_error:
            raise reply.msg
        return reply.msg

    def error(self, e):
        raise NotImplementedError('You can tell error only when you reply')


class FunctionRef(BaseActorRef):
    def __init__(self, fut, loop):
        self._fut = fut
        self._loop = loop

    def _send(self, envel):
        self._loop.call_soon_threadsafe(self._try_set_future, envel)

    def _try_set_future(self, result):
        if not self._fut.done():
            self._fut.set_result(result)

    def tell(self, m, *, sender=None):
        if sender is None:
            sender = _guess_current_sender()
        self._send(rocat.message.Envelope.for_ask(m, sender=sender))

    def ask(self, m, *, sender=None, timeout=None):
        raise NotImplementedError('You cannot ask back to ask request')

    def error(self, e):
        self._send(rocat.message.Envelope.for_error(e))


def _guess_current_sender():
    current_ctx = rocat.actor.ActorContext.current()
    if current_ctx is not None:
        return current_ctx.sender


def _guess_default_timeout():
    current_ctx = rocat.actor.ActorContext.current()
    if current_ctx is not None:
        return current_ctx.default_timeout or -1
    return -1
