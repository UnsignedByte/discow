import discord
import asyncio


class Discow(discord.Client):

    @asyncio.coroutine
    def on_message(self, message):
        yield from self.send_message(message.channel, 'Hello World!')


discow = Discow()
discow.login('4Ez-Qx2oBWHIRlUvgVtjXYCd9AadouE1')
discow.start()
