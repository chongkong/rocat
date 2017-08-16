import rocat.role
import rocat.actor
import rocat.ref


# role_name -> actor_name -> actor_ref
_actors_refs = {}


def register(role, actor):
    _actors_refs.setdefault(role.name, {})
    assert actor.name not in _actors_refs[role.name], f'Actor name {actor.name} exists'
    ref = _actors_refs[role.name][actor.name] = actor.create_ref()
    return ref


def find(role, *, name=None) -> rocat.ref.BaseActorRef:
    """ Find actor_ref of given role and actor name """
    if isinstance(role, rocat.role.BaseActorRole):
        role = role.name
    if role in _actors_refs:
        actors_of_role = _actors_refs[role]
        if name is None and len(actors_of_role) == 1:
            return next(iter(actors_of_role.values()))
        elif name is not None and name in actors_of_role:
            return actors_of_role[name]
