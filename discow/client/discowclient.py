import discord
import asyncio
import logging
import re

import discow.client.getkey as _getkey
import discow.handlers
from discow.handlers import special_emojis

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class BotClientClass(discord.Client):
    async def on_ready(self):
        await self.change_presence(game=discord.Game(name='cow help', url='https://github.com/UnsignedByte/discow', type=2))
        mod_server_emotes = Bot.get_server("433441820102361108").emojis
        for a in mod_server_emotes:
            if a.name in ["thumbsup", "thumbsdown", "empty", "pack"]:
                if a.name in special_emojis:
                    special_emojis[a.name].append(a)
                else:
                    special_emojis[a.name] = [a]
        await asyncio.gather(discow.handlers.timed_msg(self), discow.handlers.timed_save(self))
    async def on_message(self, message):
        await discow.handlers.on_message(self, message)
    async def on_message_edit(self, before, after):
        await discow.handlers.on_message(self, after)
Bot = BotClientClass()

def runBot():
    Bot.run(_getkey.key())

if __name__ == "__main__":
    print("Auth key is %s" % _getkey.key())
