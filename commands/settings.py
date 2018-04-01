import asyncio
from discow.utils import *
from discow.handlers import *

settings_handlers = {}

@asyncio.coroutine
def settings(Discow, msg):
    yield from Discow.send_message(msg.channel, strip_command(msg.content))
    print(strip_command(msg.content))


add_message_handler(settings, "settings")
