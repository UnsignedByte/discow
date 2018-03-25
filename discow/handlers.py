import asyncio

discow_prefix = "&"

@asyncio.coroutine
def test_schedule(Discow, msg):
    tmp = yield from Discow.send_message(msg.channel, "Fuck schedules")

@asyncio.coroutine
def test_heart(Discow, msg):
    tmp = yield from Discow.send_message(msg.channel, "I love you :heart:")

message_handlers = {
    # Format is (prefix,
    "schedule" : test_schedule,
    "ily" : test_heart
}

whitespace = [' ', '\t', '\n']

def get_prefix(cont):
    trim = cont[len(discow_prefix):]

    for i, c in enumerate(trim):
        if c in whitespace:
            return trim[:i]
    return trim


@asyncio.coroutine
def on_message(Discow, msg):
    if msg.content[:len(discow_prefix)] != discow_prefix:
        return

    yield from message_handlers[get_prefix(msg.content)](Discow, msg)