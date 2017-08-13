import rocat.finder

_roles = {}


def find_role(role_name):
    return _roles.get(role_name)


class BaseActorRole(object):
    def __init__(self, name, *, ptype=dict):
        assert name not in _roles, f'Role name "{name}" is already used'
        _roles[name] = self
        self.name = name
        self.ptype = ptype

    def resolve_action(self, m):
        raise NotImplementedError

    def create(self, name=None, loop=None):
        return rocat.finder.create(self, name=name, loop=loop)


class DictFieldRole(BaseActorRole):
    def __init__(self, name, *, router='type', ptype=dict):
        super().__init__(name, ptype=ptype)
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
