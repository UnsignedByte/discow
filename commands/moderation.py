import asyncio
from discow.utils import *
from discow.handlers import *
from random import randint

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

add_message_handler(purge, "purge")
add_message_handler(purge, "clear")
