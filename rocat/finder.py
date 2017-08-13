import asyncio
import uuid

import rocat.role
import rocat.actor


# role_name -> actor_name -> actor_ref
_actors_refs = {}


def find(role, *, name=None):
    """ Find actor_ref of given role and actor name """
    if isinstance(role, rocat.role.BaseActorRole):
        role = role.name
    if role in _actors_refs:
        actors_of_role = _actors_refs[role]
        if name is None and len(actors_of_role) == 1:
            return next(iter(actors_of_role.values()))
        elif name is not None and name in actors_of_role:
            return actors_of_role[name]


def create(role, *, name=None, loop=None):
    if isinstance(role, str):
        role = rocat.role.find_role(role)
        assert role is not None
    if loop is None:
        loop = asyncio.get_event_loop()
    if name is None:
        name = str(uuid.uuid4())

    def factory(*args, **kwargs):
        props = role.ptype(*args, **kwargs)
        actor = rocat.actor.Actor(role, loop=loop, p=props, name=name)
        _actors_refs.setdefault(role.name, {})
        _actors_refs[role.name][actor.name] = actor.create_ref()

    return factory
