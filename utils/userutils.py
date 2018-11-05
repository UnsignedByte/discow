# @Author: Edmund Lam <edl>
# @Date:   20:17:56, 04-Nov-2018
# @Filename: memberutils.py
# @Last modified by:   edl
# @Last modified time: 20:19:40, 04-Nov-2018

import asyncio

async def get_owner(Bot):
    return (await Bot.application_info()).owner

async def is_mod(Bot, user):
    return user == (await get_owner(Bot)) or user in nested_get('global_data', 'moderators')
