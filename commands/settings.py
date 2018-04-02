import asyncio
from discow.utils import *
from discow.handlers import enable_command, disable_command, add_message_handler, is_command, message_handlers
from discord import Embed

settings_handlers = {}

@asyncio.coroutine
def settings(Discow, msg):
    newmsg = strip_command(msg.content).split(" ")
    try:
        yield from settings_handlers[newmsg[0]](Discow, msg, newmsg)
    except KeyError:
        em = Embed(title="ERROR", description="Unknown subcommand **%s**." % newmsg[0], colour=0xd32323)
        yield from Discow.send_message(msg.channel, embed=em)


#SUBCOMMANDS DEFINED HERE
@asyncio.coroutine
def disable(Discow, msg, newmsg):
    if is_command(newmsg[1]):
        cmdname = message_handlers[newmsg[1]].__name__
        disable_command(cmdname, msg.channel_mentions)
        em = Embed(title="Command Disabled", colour=0x12AA24)
        em.description = cmdname+" has now been disabled in "+','.join(map(lambda x:x.mention, msg.channel_mentions))+"."
        yield from Discow.send_message(msg.channel, embed=em)
    else:
        em = Embed(title="ERROR", description="%s is not a command. View all commands using `cow commands`" % newmsg[1], colour=0xd32323)
        yield from Discow.send_message(msg.channel, embed=em)

@asyncio.coroutine
def enable(Discow, msg, newmsg):
    if is_command(newmsg[1]):
        cmdname = message_handlers[newmsg[1]].__name__
        enable_command(cmdname, msg.channel_mentions)
        em = Embed(title="Command Enabled", colour=0x12AA24)
        em.description = cmdname+" has now been enabled in "+','.join(map(lambda x:x.mention, msg.channel_mentions))+"."
        yield from Discow.send_message(msg.channel, embed=em)
    else:
        em = Embed(title="ERROR", description="%s is not a command. View all commands using `cow commands`" % newmsg[1], colour=0xd32323)
        yield from Discow.send_message(msg.channel, embed=em)

settings_handlers["disable"] = disable
settings_handlers["enable"] = enable
add_message_handler(settings, "settings")
