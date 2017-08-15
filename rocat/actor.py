import asyncio
import logging
import weakref

import rocat.message
import rocat.role
import rocat.ref
import rocat.finder


class ActorContext(object):
    contexts = {}

    @classmethod
    def current(cls):
        return cls.contexts.get(asyncio.Task.current_task())

    def __init__(self, actor, envel):
        self._actor = actor
        self._envel = envel
        self._task = None

    def __enter__(self):
        self._task = asyncio.Task.current_task()
        self.contexts[self._task] = self
        self._actor.contexts[self._task] = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.contexts.pop(self._task)
        self._actor.contexts.pop(self._task)

    @property
    def sender(self):
        return self._envel.sender

    @property
    def p(self):
        return self._actor.props

    @property
    def name(self):
        return self._actor.name

    @property
    def ref(self):
        return self._actor.ref


class Actor(object):
    def __init__(self, role, props, *, name, loop):
        self._role = role
        self._props = props
        self._name = name
        self._loop = loop
        self._q = asyncio.Queue(loop=loop)
        self._contexts = {}
        self._logger = logging.Logger(repr(self))

    def __repr__(self):
        return f'{self._role.name}/{self.name}'

    @property
    def props(self):
        return self._props

    @property
    def contexts(self):
        return self._contexts

    @property
    def name(self):
        return self._name

    @property
    def ref(self):
        return rocat.finder.find(self._role, name=self._name)

    def start(self):
        asyncio.ensure_future(self._main(), loop=self._loop)

    async def _main(self):
        while True:
            try:
                envel = await self._q.get()
                assert isinstance(envel, rocat.message.Envelope)
                if envel.type == rocat.message.MsgType.TERMINAL:
                    break
                asyncio.ensure_future(self._handle_envel(envel), loop=self._loop)
            except Exception as e:
                self._logger.exception(e)

    async def _handle_envel(self, envel):
        with ActorContext(self, envel) as ctx:
            action = self._role.resolve_action(envel.msg)
            if action is not None:
                ret = action(ctx, envel.msg)
                if asyncio.iscoroutine(ret):
                    await ret
            else:
                self._logger.error(f'No handler for {repr(envel.msg)}')

    def create_ref(self):
        return rocat.ref.LocalActorRef(self._q, self._loop)
