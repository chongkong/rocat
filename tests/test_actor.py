import asyncio
import rocat

greeter_role = rocat.DictFieldRole('greeter', field='name')


@greeter_role.default_route
def greet(ctx, msg):
    name = msg.get('name', 'stranger')
    ctx.sender.tell(f'Welcome, {name}')


@greeter_role.route('john')
def greet_john(ctx, msg):
    ctx.sender.tell('How dare you come here, John!')


executor = rocat.ActorExecutor()
executor.start()

async def test():
    greeter = greeter_role.create(executor=executor)
    print(await greeter.ask({'name': 'chongkong'}))
    print(await greeter.ask({}))
    print(await greeter.ask({'name': 'john'}))

asyncio.get_event_loop().run_until_complete(test())
