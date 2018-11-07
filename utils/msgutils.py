# @Author: Edmund Lam <edl>
# @Date:   10:01:53, 03-Nov-2018
# @Filename: msgutils.py
# @Last modified by:   edl
# @Last modified time: 15:36:12, 07-Nov-2018

import asyncio
import datetime
from pytz import timezone
import pytz
from discord import ServerRegion, Forbidden

def convertTime(time, msg):
    if msg.channel.is_private:
        zone = timezone("Europe/London")
    else:
        timezones = {
        ServerRegion.us_west:"America/Los_Angeles",
        ServerRegion.us_east:"America/New_York",
        ServerRegion.us_central:"US/Central",
        ServerRegion.eu_west:"Europe/Amsterdam",
        ServerRegion.eu_central:"Europe/Berlin",
        ServerRegion.singapore:"Singapore",
        ServerRegion.london:"Europe/London",
        ServerRegion.sydney:"Australia/Sydney",
        ServerRegion.amsterdam:"Europe/Amsterdam",
        ServerRegion.frankfurt:"Europe/Berlin",
        ServerRegion.brazil:"Brazil/Acre",
        ServerRegion.vip_us_east:"America/New_York",
        ServerRegion.vip_us_west:"America/Los_Angeles",
        ServerRegion.vip_amsterdam:"Europe/Amsterdam",
        'russia':'Europe/Russia'
        }
        zone = timezone(timezones[msg.server.region])
    time_naive = time.replace(tzinfo=pytz.utc)
    loctime = time_naive.astimezone(zone)
    fmt = '%Y-%m-%d at %H:%M:%S %Z'
    return loctime.strftime(fmt)

def nickname(usr, srv):
    if not srv:
        return usr.name
    n = srv.get_member(usr.id).nick
    if not n:
        return usr.name
    return n

async def send_embed(Bot, msg, embed, time=datetime.datetime.utcnow(), usr=None):
    if not usr:
        usr = Bot.user
    txt = "Created by "+nickname(usr, msg.server)+" on "+convertTime(time, msg)+"."
    embed.set_footer(text=txt, icon_url=(usr.avatar_url if usr.avatar_url else usr.default_avatar_url))
    try:
        m = await Bot.send_message(msg.channel, embed=embed)
        return m
    except Forbidden:
        await Bot.send_message(msg.channel,
                                       "**Missing Permissions**\nDiscow is missing permissions to send embeds.")
        return None


async def edit_embed(Bot, msg, embed, time=datetime.datetime.utcnow(), usr=None):
    if not usr:
        usr = Bot.user
    txt = "Edited by "+nickname(usr, msg.server)+" on "+convertTime(time, msg)+"."
    embed.set_footer(text=txt, icon_url=(usr.avatar_url if usr.avatar_url else usr.default_avatar_url))
    m = await Bot.edit_message(msg, embed=embed)
    return m

async def send_large_message(Bot, channel, content, prefix='', suffix=''):
    cchunk = ""
    for l in content.splitlines():
        if len(cchunk)+len(l)> 2000-len(prefix)-len(suffix):
            await Bot.send_message(channel, prefix+cchunk+suffix)
            cchunk = ""
        cchunk+=l+"\n"
    await Bot.send_message(channel, prefix+cchunk+suffix)
