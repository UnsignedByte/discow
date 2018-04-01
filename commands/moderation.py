import asyncio
import pickle
from discow.utils import *
from discow.handlers import add_message_handler, begin_shutdown, command_settings
from discord import Embed

@asyncio.coroutine
def purge(Discow, msg):
    num = max(1,min(100,int(parse_command(msg.content, 1)[1])))
    msgs = yield from Discow.logs_from(msg.channel, limit=num)
    msgs = list(msgs)
    if num == 1:
        tmp = yield from Discow.delete_message(msgs[0])
    else:
        tmp = yield from Discow.delete_messages(msgs)
    tmp = yield from Discow.send_message(msg.channel, format_response("**{_mention}** has cleared the last **{_number}** messages!", _msg=msg, _number=num))

@asyncio.coroutine
def shutdown(Discow, msg):
    em = Embed(title="Shutting down...", description="Saving...", colour=0xd32323)
    msg = yield from Discow.send_message(msg.channel, embed=em)
    begin_shutdown()
    with open("discow/client/data/settings.txt", "wb") as f:
        pickle.dump(command_settings, f)
    yield from asyncio.sleep(1);
    em.description = "Complete!"
    msg = yield from Discow.edit_message(msg, embed=em)
    yield from Discow.logout()


add_message_handler(shutdown, "close")
add_message_handler(shutdown, "shutdown")
add_message_handler(purge, "purge")
add_message_handler(purge, "clear")
