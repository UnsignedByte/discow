import discord
import asyncio
import logging
import re

import discow.client.getkey as _getkey
import discow.handlers
from discow.handlers import britsub, special_emojis

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discow/client/data/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class DiscowClientClass(discord.Client):
    @asyncio.coroutine
    def on_ready(self):
        yield from self.change_presence(game=discord.Game(name='cow help', url='https://github.com/UnsignedByte/discow', type=2))
        mod_server_emotes = Discow.get_server("433441820102361108").emojis
        for a in mod_server_emotes:
            if a.name in ["thumbsup", "thumbsdown", "empty"]:
                if a.name in special_emojis:
                    special_emojis[a.name].append(a)
                else:
                    special_emojis[a.name] = [a]
        for a in Discow.get_all_members():
            if a.nick:
                newnick = britsub(a.nick)
                if newnick != a.nick:
                    try:
                        yield from self.change_nickname(a, newnick)
                    except discord.Forbidden:
                        pass
        yield from discow.handlers.timed_msg(self)
    @asyncio.coroutine
    def on_message(self, message):
        yield from discow.handlers.on_message(self, message)
    def on_message_edit(self, before, after):
        yield from discow.handlers.on_message(self, after)
    @asyncio.coroutine
    def on_reaction_add(self, reaction, user):
        yield from discow.handlers.on_reaction(self, reaction, user)
    @asyncio.coroutine
    def on_reaction_remove(self, reaction, user):
        yield from discow.handlers.on_unreaction(self, reaction, user)
    def on_member_update(self, before, after):
        if after.nick and before.nick != after.nick:
            newnick = britsub(after.nick)
            if newnick != after.nick:
                try:
                    yield from self.change_nickname(after, newnick)
                except (discord.Forbidden, TypeError):
                    pass
Discow = DiscowClientClass()

def runDiscow():
    Discow.run(_getkey.key())

if __name__ == "__main__":
    print("Auth key is %s" % _getkey.key())
