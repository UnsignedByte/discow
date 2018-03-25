import asyncio

@asyncio.coroutine
def test_message(Discow, msg):
    tmp = yield from Discow.send_message(msg.channel, "Hi **%s**! I'm Discow." % msg.author.name)

@asyncio.coroutine
def test_heart(Discow, msg):
    tmp = yield from Discow.send_message(msg.channel, "I love you too, **%s**! :heart:" % msg.author.name)

message_handlers = {
    # Format is (command, function)
    "test": test_message,
    "ily" : test_heart
}

discow_prefix = "&"


whitespace = [' ', '\t', '\n']

def get_command(cont):
    trim = cont[len(discow_prefix):]

    for i, c in enumerate(trim):
        if c in whitespace:
            return trim[:i]
    return trim


@asyncio.coroutine
def on_message(Discow, msg):
    if msg.content[:len(discow_prefix)] != discow_prefix:
        return

    try:
        yield from message_handlers[get_command(msg.content)](Discow, msg)
    except KeyError:
        tmp = yield from Discow.send_message(msg.channel, "Unknown command **%s**." % get_command(msg.content))