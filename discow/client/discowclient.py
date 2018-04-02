import discord
import asyncio
import logging

import discow.client.getkey as _getkey
import discow.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discow/client/data/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class DiscowClientClass(discord.Client):
    @asyncio.coroutine
    def on_message(self, message):
        yield from discow.handlers.on_message(self, message)
    @asyncio.coroutine
    def on_reaction_add(self, reaction, user):
        yield from discow.handlers.on_reaction(self, reaction, user)

    @asyncio.coroutine
    def on_reaction_remove(self, reaction, user):
        yield from discow.handlers.on_unreaction(self, reaction, user)
Discow = DiscowClientClass()

def runDiscow():
    Discow.run(_getkey.key())

if __name__ == "__main__":
    print("Auth key is %s" % _getkey.key())
