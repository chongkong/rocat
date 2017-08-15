import uuid

import rocat
import rocat.actor
import rocat.finder
import rocat.globals
import rocat.ref

_roles = {}


def find_role(role_name):
    return _roles.get(role_name)


class BaseActorRole(object):
    def __init__(self, name):
        assert name not in _roles, f'Role name "{name}" is already used'
        _roles[name] = self
        self.name = name

    def resolve_action(self, m):
        raise NotImplementedError

    def create(self, props=None, *, name=None, executor=None) -> rocat.ref.BaseActorRef:
        if props is None:
            props = {}
        if name is None:
            name = str(uuid.uuid4())
        if executor is None:
            executor = rocat.globals.g.executor
        actor = rocat.actor.Actor(self, props, name=name, loop=executor.loop)
        actor.start()
        return rocat.finder.register(self, actor)


class DictFieldRole(BaseActorRole):
    def __init__(self, name, *, field='type'):
        super().__init__(name)
        self._field = field
        self._routes = {}
        self._default_route = None

    def route(self, field_value: str):
        def deco(f):
            self._routes[field_value] = f
            return f
        return deco

    def default_route(self, f):
        self._default_route = f
        return f

    def resolve_action(self, m):
        if isinstance(m, dict):
            if self._field in m:
                route = m[self._field]
                if route in self._routes:
                    return self._routes[route]
            return self._default_route
