import asyncio
from discow.format import format_response
from discow.handlers import message_handlers

@asyncio.coroutine
def test_message(Discow, msg):
    yield from Discow.send_message(msg.channel, format_response("Hi **{_name}**, I'm Discow! Here's a tag: {_mention}", _msg = msg))

@asyncio.coroutine
def rps(Discow, msg):
    mine = "rock"
    try:
        tmp = yield from Discow.send_message(msg.channel, format_response("**{_mention}** chooses **%s**, while I choose **%s**." % (msg.content.split(" ")[1], mine)))
    except IndexError:
        tmp = yield from Discow.send_message(msg.channel, "Please provide an input.")

message_handlers["test"] = test_message
message_handlers["rps"] = test_heart