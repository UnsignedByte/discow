# @Author: Edmund Lam <edl>
# @Date:   20:17:56, 04-Nov-2018
# @Filename: memberutils.py
# @Last modified by:   edl
# @Last modified time: 14:58:42, 11-Nov-2018

import asyncio
from utils import datautils
import discord

async def get_owner(Bot):
    return (await Bot.application_info()).owner

async def is_mod(Bot, user):
    return user == (await get_owner(Bot)) or user in datautils.nested_get('global_data', 'moderators', default=[])

def get_user_color(user):
    if isinstance(user, discord.Member):
        return user.colour
    else:
        return 0x3a71c1
