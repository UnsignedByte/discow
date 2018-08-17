# @Author: Edmund Lam <edl>
# @Date:   11:04:49, 05-Apr-2018
# @Filename: settings.py
# @Last modified by:   edl
# @Last modified time: 19:09:41, 16-Aug-2018


import asyncio
from discow.utils import *
from discow.handlers import enable_command, disable_command, add_message_handler, is_command, message_handlers
from discord import Embed, ChannelType

settings_handlers = {}

async def settings(Discow, msg):
    newmsg = strip_command(msg.content).split(" ")
    try:
        await settings_handlers[newmsg[0]](Discow, msg, newmsg)
    except KeyError:
        em = Embed(title="ERROR", description="Unknown subcommand **%s**." % newmsg[0], colour=0xd32323)
        await Discow.send_message(msg.channel, embed=em)


#SUBCOMMANDS DEFINED HERE
async def disable(Discow, msg, newmsg):
    if is_command(newmsg[1]):
        todisable = msg.channel_mentions
        if newmsg[2] == 'all':
            todisable = list(n for n in msg.server.channels if n.type == ChannelType.text)
        cmdname = message_handlers[newmsg[1]].__name__
        disable_command(cmdname, todisable)
        em = Embed(title="Command Disabled", colour=0x12AA24)
        em.description = cmdname+" has now been disabled in "+','.join(map(lambda x:x.mention, todisable))+"."
        await send_embed(Discow, msg, em)
    else:
        em = Embed(title="ERROR", description="%s is not a command. View all commands using `cow commands`" % newmsg[1], colour=0xd32323)
        await send_embed(Discow, msg, em)

async def enable(Discow, msg, newmsg):
    if is_command(newmsg[1]):
        toenable = msg.channel_mentions
        if newmsg[2] == 'all':
            toenable = list(n for n in msg.server.channels if n.type == ChannelType.text)
        cmdname = message_handlers[newmsg[1]].__name__
        enable_command(cmdname, toenable)
        em = Embed(title="Command Enabled", colour=0x12AA24)
        em.description = cmdname+" has now been enabled in "+','.join(map(lambda x:x.mention, toenable))+"."
        await send_embed(Discow, msg, em)
    else:
        em = Embed(title="ERROR", description="%s is not a command. View all commands using `cow commands`" % newmsg[1], colour=0xd32323)
        await send_embed(Discow, msg, em)

settings_handlers["disable"] = disable
settings_handlers["enable"] = enable
add_message_handler(settings, "settings")
