import asyncio
import logging

import rocat.message
import rocat.role
import rocat.ref


class ActorContext(object):
    def __init__(self, actor, envel):
        self._actor = actor
        self._envel = envel
        self._task = None

    def __enter__(self):
        self._task = asyncio.Task.current_task()
        self._actor.contexts[self._task] = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._actor.contexts.pop(self._task)

    @property
    def sender(self):
        return self._envel.sender

    @property
    def p(self):
        return self._actor.p


class Actor(object):
    def __init__(self, role, *, loop, p, name):
        self._role = role
        self._loop = loop
        self.p = p
        self.name = name
        self._q = asyncio.Queue(loop=loop)
        self.contexts = {}
        self._logger = logging.Logger(f'{role.name}/{name}')

    def start(self):
        self._loop.call_soon_threadsafe(self._main)

    async def _main(self):
        while True:
            try:
                envel = await self._q.get()
                assert isinstance(envel, rocat.message.Envelope)
                if envel.type == rocat.message.MsgType.TERMINAL:
                    break
                self._loop.call_soon(self._handle_envel, envel)
            except Exception as e:
                self._logger.exception(e)

    async def _handle_envel(self, envel: rocat.message.Envelope):
        with ActorContext(self, envel) as ctx:
            action = self._role.resolve_action(envel.msg)
            if action is not None:
                action(ctx)

    def create_ref(self):
        return rocat.ref.LocalActorRef(self._q, self._loop)
