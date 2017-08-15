# rocat

<img src="https://github.com/chongkong/rocat/raw/master/docs/assets/rocat.jpg" width="128" style="float: left; margin-right: 10px;">

rocat is a simple asyncio coroutine based actor library. `rocat` is an anagram of `actor`.
Currently on extremely early development stage


## Usage

In rocat, you define _role_ of the actor, instead of defining actor itself.
_Role_ defines how you'd react to the incoming messages.
Your code style would be more Flask-like in this way.

```python
import rocat

greeter_role = rocat.DictFieldRole('greeter', router='name')

@greeter_role.route('chongkong')
def greet_chongkong(ctx, msg):
    ctx.sender.tell('hello, handsome chongkong')
```

Once you have created a role, you need on event loop executor called `ActorExecutor` to run your actor.

```python
executor = rocat.ActorExecutor()
executor.start()  # This fires a new thread
```

If you're creating actor outside of actor context, (i.e. not from the functions registered to `ActorRole`)
you have to manually specify executor in which the actor would run.

```python
greeter = greeter_role.create(executor=executor)
```

After creating an actor, you can freely communicate with your actor.
The basic communication method is to _ask_ an actor some message and wait for the reply.
You have to `await` the reply from the actor. 

```python
async def test():
    resp = await greeter.ask({'name': 'chongkong'})
    print(resp)
```

This would print `"hello, handsome chongkong"`
