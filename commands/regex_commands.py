# @Author: Edmund Lam <edl>
# @Date:   21:24:19, 06-Nov-2018
# @Filename: regex_commands.py
# @Last modified by:   edl
# @Last modified time: 20:36:45, 11-Nov-2018

#Special commands using regex rather than prefix


import asyncio
from discord import Embed
from utils import msgutils, strutils, datautils, userutils
from discow.handlers import add_regex_message_handler
import re
import pytz, datetime


async def echo(Bot, msg, reg):
    await Bot.send_message(msg.channel, "**"+msg.author.display_name+" says:** "+reg.group(1))

async def last_mention(Bot, msg, reg):
    mmsg = datautils.nested_get('user_data', msg.author.id, 'mentions')
    out = 'Jump to message may not work if message is deleted.\nType `clear ping` to clear mentions.\nMessage may be split up if length exceeds 1024 characters, and may be truncated if the total length exceeds 5120 characters.\n\n'
    if mmsg and len(mmsg) > 0:
        for mention in mmsg[::-1]:
            link = '(https://discordapp.com/channels/%s/%s/%s)' % (mention.server.id, mention.channel.id, mention.id)
            out += '[**Jump**]' + link + ' `' + msgutils.msg_loctime(mention.timestamp, mention, format='%d %b %y %H:%M %Z') +\
                   '` **' + mention.author.display_name + '**: ' + strutils.escape_markdown(mention.content)
            if mention.edited_timestamp:
                out += ' `(edited)`'
            out += '\n'
    else:
        out += 'No pings logged!'
    outl = strutils.split_str_chunks(out[:5120], 1023)
    em = Embed(title="Mentions for " + msg.author.display_name, colour=userutils.get_user_color(msg.author))
    if len(outl) == 1:
        em.description=outl[0]
    else:
        em.description=outl[0]+"\n"+outl[1]
        for i in outl[2:]:
            em.add_field(name="\u200D", value=i)
        em.set_footer(text=msg.author.display_name, icon_url=msg.author.avatar_url)
    await Bot.send_message(msg.channel, embed=em)
    return


async def clear_ping(Bot, msg, reg):
    datautils.nested_set([], 'user_data', msg.author.id, 'mentions')
    em = Embed(title="Mentions cleared", description='Type `who ping` to view mentions', colour=msg.author.colour)
    em.set_footer(text=msg.author.display_name, icon_url=msg.author.avatar_url)
    await Bot.send_message(msg.channel, embed=em)

add_regex_message_handler(echo, r'echo:(.*)')
add_regex_message_handler(last_mention, r'who\s*ping.*')
add_regex_message_handler(clear_ping, r'clear\s*ping.*')
