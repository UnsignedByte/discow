# @Author: Edmund Lam <edl>
# @Date:   21:24:19, 06-Nov-2018
# @Filename: regex_commands.py
# @Last modified by:   edl
# @Last modified time: 22:47:28, 06-Nov-2018

#Special commands using regex rather than prefix


import asyncio
from discord import Embed
from utils import msgutils, strutils, datautils
from discow.handlers import add_regex_message_handler
import re


async def echo(Bot, msg, reg):
    await Bot.send_message(msg.channel, reg.group(1))

async def last_mention(Bot, msg, reg):
    mmsg = datautils.nested_get('user_data', msg.author.id, 'last_mention')
    if not mmsg:
        await Bot.send_message(msg.channel, "No mentions logged!")
        return
    em = Embed(title="Last mention for "+msg.author.display_name, description='%s\n\n\n[Jump to Message](https://discordapp.com/channels/%s/%s/%s)\nNote: Message may have been deleted' % (mmsg.content, mmsg.server.id, mmsg.channel.id, mmsg.id), colour=mmsg.author.colour)
    em.set_footer(text=mmsg.author.display_name, icon_url=mmsg.author.avatar_url)
    await Bot.send_message(msg.channel, embed=em)
    return

add_regex_message_handler(echo, r'echo:(.*)')
add_regex_message_handler(last_mention, r'who\s*ping.*')
