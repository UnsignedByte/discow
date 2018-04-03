import asyncio
from discow.utils import *
from discow.handlers import add_message_handler, user_data
import time
from random import randint

@asyncio.coroutine
def daily(Discow, msg):
    addedmoney = randint(400, 600)
    if msg.author.id in user_data:
        if (round(time.time())-user_data[msg.author.id]["daily"]) > 86400:
            user_data[msg.author.id]["money"]+=addedmoney
            yield from Discow.send_message(msg.channel, "Added $"+str(addedmoney)+" to your balance, "+msg.author.mention+"!")
        else:
            seconds = 86400-(round(time.time())-user_data[msg.author.id]["daily"])
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            yield from Discow.send_message(msg.channel, "Not so fast! Please wait another %d hours, %02d minutes, and %02d seconds." % (h, m, s))
    else:
        user_data[msg.author.id] = {"daily": round(time.time()), "money": addedmoney}
        yield from Discow.send_message(msg.channel, "Added $"+str(addedmoney)+" to your balance, "+msg.author.mention+"!")

@asyncio.coroutine
def money(Discow, msg):
    if len(msg.mentions) == 0:
        if msg.author.id in user_data:
            yield from Discow.send_message(msg.channel, "You currently have $%s, %s." % (user_data[msg.author.id]["money"], msg.author.mention))
        else:
            yield from Discow.send_message(msg.channel, "You have no money. Do `cow daily` to recieve your daily reward!")
    else:
        if msg.mentions[0].id in user_data:
            yield from Discow.send_message(msg.channel, "%s currently has $%s." % (msg.mentions[0].mention, user_data[msg.mentions[0].id]["money"]))
        else:
            yield from Discow.send_message(msg.channel, "%s is new and currently has no money." % msg.mentions[0].mention)

@asyncio.coroutine
def slots(Discow, msg):
    bet = int(strip_command(msg.content))
    if bet > user_data[msg.author.id]["money"]:
        yield from Discow.send_message(msg.channel, "You don't have that much to bet, silly!")
    else:
        moneychange = randint(-1*bet, bet)
        if moneychange >= 0:
            yield from Discow.send_message(msg.channel, msg.author.mention+" won $"+str(moneychange)+". Nice job!")
        else:
            yield from Discow.send_message(msg.channel, msg.author.mention+" lost $"+str(-1*moneychange)+". Better luck next time!")
        if msg.author.id in user_data:
            user_data[msg.author.id]["money"]+=moneychange
        else:
            user_data[msg.author.id] = {"daily": -86400, "money": moneychange}

add_message_handler(daily, "daily")
add_message_handler(money, "money")
add_message_handler(slots, "slots")
add_message_handler(slots, "gamble")
