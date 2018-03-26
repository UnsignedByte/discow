message_handlers = {}

# Add modules here
import discow.test_functions
from discow.utils import *

import asyncio

@asyncio.coroutine
def on_message(Discow, msg):
    if msg.content[:len(discow_prefix)] != discow_prefix:
        return

    try:
        print(parse_command(msg)[0])
        yield from message_handlers[parse_command(msg)[0]](Discow, msg)
    except KeyError:
        tmp = yield from Discow.send_message(msg.channel, "Unknown command **%s**." % parse_command(msg)[0])
