import asyncio
from discow.utils import *
from discow.handlers import message_handlers
from random import randint

@asyncio.coroutine
def test_message(Discow, msg):
    yield from Discow.send_message(msg.channel, format_response("Hi **{_name}**, I'm Discow! Here's a tag: {_mention}", _msg = msg))

@asyncio.coroutine
def rps(Discow, msg):

    try:
        mine = "rock"
        yours = parse_command(msg, 1)[1]
        tmp = yield from Discow.send_message(msg.channel, format_response("**{_mention}** chooses **%s**, while I choose **%s**." % (yours, mine), _msg = msg))
    except IndexError:
        tmp = yield from Discow.send_message(msg.channel, "Please provide an input.")

message_handlers["test"] = test_message
message_handlers["rps"] = rps
