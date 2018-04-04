import asyncio
import pickle
from discow.utils import *
from discow.handlers import add_message_handler, flip_shutdown, get_data
from discord import Embed

@asyncio.coroutine
def info(Discow, msg):
    myinfo = yield from Discow.application_info()
    me = yield from Discow.get_user_info(myinfo.id)
    em = Embed(title="Who am I?", colour=0x9542f4)
    em.description = "Hi, I'm [discow](https://github.com/UnsignedByte/discow), a discord bot created by <@418827664304898048> and <@418667403396775936>."
    em.add_field(name="Features", value="For information about my features do `cow help` or take a look at [our readme](https://github.com/UnsignedByte/discow/blob/master/README.md)!")
    txt = "Created by "+me.display_name+" on "+get_localized_time(msg.server)+"."
    em.set_footer(text=txt, icon_url=myinfo.icon_url)
    yield from Discow.send_message(msg.channel, embed=em)

@asyncio.coroutine
def quote(Discow, msg):
    m = yield from Discow.get_message((msg.channel if len(msg.channel_mentions) == 0 else msg.channel_mentions[0]), strip_command(msg.content).split(" ")[0])
    em = Embed(colour=0x3b7ce5)
    em.title = "Message Quoted by "+msg.author.display_name+":"
    desc = m.content
    log = yield from Discow.logs_from(m.channel, limit=20, after=m)
    log = reversed(list(log))
    for a in log:
        if a.author == m.author:
            if a.content:
                desc+="\n"+a.content
        else:
            break
    log = yield from Discow.logs_from(m.channel, limit=10, before=m)
    log = list(log)
    for a in log:
        if a.author == m.author:
            if a.content:
                desc=a.content+"\n"+desc
        else:
            break
    em.description = desc
    txt = "Written by "+m.author.display_name+" on "+convertTime(m.timestamp, m.server)
    avatarurl = m.author.avatar_url
    if not avatarurl:
        avatarurl = m.author.default_avatar_url
    em.set_footer(text=txt, icon_url=avatarurl)
    yield from Discow.delete_message(msg)
    yield from Discow.send_message(msg.channel, embed=em)

@asyncio.coroutine
def purge(Discow, msg):
    num = max(1,min(100,int(parse_command(msg.content, 1)[1])))+1
    msgs = yield from Discow.logs_from(msg.channel, limit=num)
    msgs = list(msgs)
    if num == 1:
        yield from Discow.delete_message(msgs[0])
    else:
        yield from Discow.delete_messages(msgs)
    m = yield from Discow.send_message(msg.channel, format_response("**{_mention}** has cleared the last **{_number}** messages!", _msg=msg, _number=num-1))
    yield from asyncio.sleep(2)
    yield from Discow.delete_message(m)

@asyncio.coroutine
def save(Discow, msg):
    perms = msg.channel.permissions_for(msg.author)
    yield from Discow.delete_message(msg)
    if perms.manage_server:
        em = Embed(title="Saving Data...", description="Saving...", colour=0xd32323)
        msg = yield from Discow.send_message(msg.channel, embed=em)
        flip_shutdown()
        yield from asyncio.sleep(1)
        data = get_data()
        with open("discow/client/data/settings.txt", "wb") as f:
            pickle.dump(data[0], f)
        with open("discow/client/data/user_data.txt", "wb") as f:
            pickle.dump(data[1], f)
        em.description = "Complete!"
        flip_shutdown()
        msg = yield from Discow.edit_message(msg, embed=em)
    else:
        em = Embed(title="Insufficient Permissions", description=format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        yield from Discow.send_message(msg.channel, embed=em)

@asyncio.coroutine
def shutdown(Discow, msg):
    yield from save(Discow, msg)
    yield from Discow.logout()


add_message_handler(info, "hi")
add_message_handler(info, "info")
add_message_handler(shutdown, "close")
add_message_handler(shutdown, "shutdown")
add_message_handler(save, "save")
add_message_handler(purge, "purge")
add_message_handler(purge, "clear")
add_message_handler(quote, "quote")
