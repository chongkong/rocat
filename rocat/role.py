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
    """ActorRole is a blueprint of actor.
    You can define a lifecycle hook of the actor, and how you'd react to the
    incoming messages by implementing resolve_action"""

    def __init__(self, name, default_timeout=None):
        assert name not in _roles, f'Role name "{name}" is already used'
        _roles[name] = self
        self._name = name
        self._default_timeout = default_timeout
        self._hooks = {}

    @property
    def name(self):
        """Unique name of this actor role"""
        return self._name

    @property
    def default_timeout(self):
        """Default timeout seconds when asking to other actors.
        None means no timeout is used and wait forever"""
        return self._default_timeout

    @property
    def hooks(self):
        """Return registered hooks"""
        return self._hooks

    def _hook_decorator(self, name):
        def deco(f):
            self._hooks[name] = f
            return f
        return deco

    def on_created(self):
        """Register on_created lifecycle hook"""
        return self._hook_decorator('on_created')

    def on_exception(self):
        """Register on_exception lifecycle hook"""
        return self._hook_decorator('on_exception')

    def before_die(self):
        """Register before_die lifecycle hook"""
        return self._hook_decorator('before_die')

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
    def __init__(self, name, field='type', **kwargs):
        super().__init__(name, **kwargs)
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
