import asyncio
from discow.format import format_response
from discow.handlers import message_handlers

@asyncio.coroutine
def test_message(Discow, msg):
    yield from Discow.send_message(msg.channel, format_response("Hi **{_name}**, I'm Discow! Here's a tag: {_mention}", _msg = msg))

@asyncio.coroutine
def test_heart(Discow, msg):
    yield from Discow.send_message(msg.channel, "I love you too, **%s**! :heart:" % msg.author.name)

message_handlers["test"] = test_message
message_handlers["ily"] = test_heart