import asyncio
from discow.utils import *
from discow.handlers import add_message_handler, user_data
import time

@asyncio.coroutine
def daily(Discow, msg):
    if msg.author.id in user_data:
        if (round(time.time())-user_data[msg.author.id]["daily"]) > 86400:
            user_data[msg.author.id]["money"]+=500
            yield from Discow.send_message(msg.channel, "Added $500 to your balance, "+msg.author.mention+"!")
        else:
            seconds = 86400-(round(time.time())-user_data[msg.author.id]["daily"])
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            yield from Discow.send_message(msg.channel, "Not so fast! Please wait another %d hours, %02d minutes, and %02d seconds." % (h, m, s))
    else:
        user_data[msg.author.id] = {"daily": round(time.time()), "money": 500}
        yield from Discow.send_message(msg.channel, "Added $500 to your balance, "+msg.author.mention+"!")

@asyncio.coroutine
def money(Discow, msg):
    if msg.author.id in user_data:
        yield from Discow.send_message(msg.channel, "You currently have $%s, %s." % (user_data[msg.author.id]["money"], msg.author.mention))
    else:
        yield from Discow.send_message(msg.channel, "You have no money. Do `cow daily` to recieve your daily reward!")

add_message_handler(daily, "daily")
add_message_handler(money, "money")
