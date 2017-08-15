import asyncio
import rocat

greeter_role = rocat.DictFieldRole("greeter", router="name")


@greeter_role.route("chongkong")
def greet_john(ctx, msg):
    ctx.sender.tell("hello, handsome chongkong!")


@greeter_role.default_route
def greet(ctx, msg):
    ctx.sender.tell(f'hello, {msg["name"]}')


executor = rocat.ActorExecutor()
executor.start()

async def test():
    greeter = greeter_role.create(executor=executor)
    print(await greeter.ask({'name': 'chongkong'}))
    print(await greeter.ask({'name': 'aiden'}))

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
