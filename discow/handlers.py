message_handlers = {}
reaction_handlers = []
unreaction_handlers = []

# Add modules here
import discow.test_functions
import discow.gunn_schedule.calendar_
import discow.gunn_schedule.schedule
from discow.utils import *

import asyncio

whitespace = [' ', '\t', '\n']

@asyncio.coroutine
def on_message(Discow, msg):
    if msg.content[:len(discow_prefix)] != discow_prefix:
        return
    try:
        yield from message_handlers[parse_command(msg.content)[0]](Discow, msg)
    except IndexError:
        tmp = yield from Discow.send_message(msg.channel, "Not enough inputs provided for **%s**." % parse_command(msg.content)[0])
    except KeyError:
        yield from Discow.send_message(msg.channel, "Unknown command **%s**." % parse_command(msg.content)[0])
    except Exception as e:
        yield from Discow.send_message(msg.channel, "An unknown error occurred in command **%s**. Trace:\n%s" % (parse_command(msg)[0], e))

@asyncio.coroutine
def on_reaction(Discow, reaction, user):
    for handler in reaction_handlers:
        yield from handler(Discow, reaction, user)

@asyncio.coroutine
def on_unreaction(Discow, reaction, user):
    for handler in reaction_handlers:
        yield from handler(Discow, reaction, user)
