# rocat

<img src="https://github.com/chongkong/rocat/raw/master/docs/assets/rocat.jpg" width="128" style="float: left; margin-right: 10px;">

rocat is a simple asyncio coroutine based actor library. `rocat` is an anagram of `actor`.
Currently on extremely early development stage


## Usage

In rocat, you define _role_ of the actor, instead of defining actor itself.
_Role_ defines how you'd react to the incoming messages.
You can define role in Flask-like style.

```python
import rocat

greeter_role = rocat.DictFieldRole('greeter', field='name')

@greeter_role.default_route
def greet(ctx, msg):
    name = msg.get('name', 'stranger')
    ctx.sender.tell(f'Welcome, {name}')

@greeter_role.route('john')
def greet_john(ctx, msg):
    ctx.sender.tell('How dare you come here, John!')
```

By using `DictFieldRole`, you can route `dict`-type message based on the field value of the given field (`"name"` in this example).
You can create your own `Role` class if you want.
Messages are routed to _action_ functions, which take two arguments: `ActorContext` and message, and return nothing.
Message can have any type, as long as you can handle them properly.
You can also define _action_ function as a coroutine function (using `async def`.)
 
Once you have created a role, you need an event loop executor called `ActorExecutor` to run your actor.

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
    print(await greeter.ask({'name': 'chongkong'}))  # would print "Welcome, chongkong"
    print(await greeter.ask({}))                     # would print "Welcome, stranger"
    print(await greeter.ask({'name': 'john'}))       # would print "How dare you come here, John!"
```
