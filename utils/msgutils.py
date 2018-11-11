# @Author: Edmund Lam <edl>
# @Date:   10:01:53, 03-Nov-2018
# @Filename: msgutils.py
# @Last modified by:   edl
# @Last modified time: 09:39:46, 11-Nov-2018

import asyncio
import datetime
from pytz import timezone
import pytz
from discord import ServerRegion, Forbidden
from utils import strutils

def getTimezone(msg):
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
    return zone

def convertTime(time, format='%Y-%m-%d at %H:%M:%S %Z', zone=timezone("Europe/London")):
    time_naive = time.replace(tzinfo=pytz.utc)
    loctime = time_naive.astimezone(zone)
    fmt = format
    return loctime.strftime(fmt)

def msg_loctime(time, msg, format='%Y-%m-%d at %H:%M:%S %Z'):
    return convertTime(time, format=format, zone=getTimezone(msg))

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
    txt = "Created by "+nickname(usr, msg.server)+" on "+msg_loctime(time, msg)+"."
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
    txt = "Edited by "+nickname(usr, msg.server)+" on "+msg_loctime(time, msg)+"."
    embed.set_footer(text=txt, icon_url=(usr.avatar_url if usr.avatar_url else usr.default_avatar_url))
    m = await Bot.edit_message(msg, embed=embed)
    return m

async def send_large_message(Bot, channel, content, prefix='', suffix=''):
    clist = strutils.split_str_chunks(content, 2000, prefix=prefix, suffix=suffix)
    for l in clist:
        await Bot.send_message(channel, l)
