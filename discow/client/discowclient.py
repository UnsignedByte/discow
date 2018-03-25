import discord
import asyncio

import discow.client.getkey as _getkey
import discow.handlers

class DiscowClientClass(discord.Client):
    @asyncio.coroutine
    def on_message(self, message):
        yield from discow.handlers.on_message(self, message)

Discow = DiscowClientClass()
Discow.run(_getkey.key())

if __name__ == "__main__":
    print("Auth key is %s" % _getkey.key())
