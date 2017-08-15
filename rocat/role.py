import uuid

import rocat
import rocat.actor
import rocat.finder
import rocat.globals

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

    def create(self, props=None, *, name=None, executor=None):
        if props is None:
            props = {}
        if name is None:
            name = str(uuid.uuid4())
        if executor is None:
            executor = rocat.globals.g.executor
        actor = rocat.actor.Actor(self.name, props, name=name, loop=executor.loop)
        return rocat.finder.register(self, actor)


class DictFieldRole(BaseActorRole):
    def __init__(self, name, *, router='type'):
        super().__init__(name)
        self.router = router
        self.routes = {}

    def route(self, field_value: str):
        def deco(f):
            self.routes[field_value] = f
            return f
        return deco

    def resolve_action(self, m):
        if isinstance(m, dict):
            if self.router in m:
                route = m[self.router]
                if route in self.routes:
                    return self.routes[route]
