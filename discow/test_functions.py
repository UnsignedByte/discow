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
        valid = ["rock", "paper", "scissors"]
        mine = valid[randint(0, 2)]
        yours = parse_command(msg, 1)[1]
        if yours in valid:
            tmp = yield from Discow.send_message(msg.channel, format_response("**{_mention}** chooses **{yours}**, while I choose **{mine}**.", yours=yours, mine=mine, _msg = msg))
        else:
            tmp = yield from Discow.send_message(msg.channel, "Your input was invalid. Please choose **rock**, **paper**, or **scissors.**")
    except IndexError:
        tmp = yield from Discow.send_message(msg.channel, "Please provide an input.")

message_handlers["test"] = test_message
message_handlers["rps"] = rps
