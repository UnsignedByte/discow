import asyncio
from discow.utils import *
from discow.handlers import add_message_handler, user_data
from discord import Embed
import time
from random import randint
from bs4 import BeautifulSoup
import urllib.request as req
import urllib.error as err

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

@asyncio.coroutine
def stock(Discow, msg):
    em = Embed(title="Stock information", description="Retrieving data...", colour=0xffd747)
    stockmsg = yield from send_embed(Discow, msg, em)
    cont = strip_command(msg.content)
    if ' ' in cont:
        em = Embed(title="Invalid Input", description="Input cannot contain whitespace", colour=0xd32323)
        stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
    else:
        link="https://www.nasdaq.com/symbol/?Load=true&Search="+cont
        try:
            html_doc = req.urlopen(link)
            soup = BeautifulSoup(html_doc, 'html.parser')
            tabl = 0
            el = []
            for x in soup.find("div", {"id": "two_column_main_content_pnlData"}).findChildren():
                if x.name == 'table':
                    for a in x.findChildren():
                        if a.name == 'td':
                            try:
                                el.append(a.findChildren()[0].decode_contents(formatter="html"))
                            except IndexError:
                                el.append(a.decode_contents(formatter="html"))
            el = group(el, 3)
            if len(el) > 1:
                em = Embed(title="Multiple results found. Choose one:", description="", colour=0xffd747)
                for a in range(0, len(el)):
                    em.description+='\n'+str(a+1)+': '+' '.join(el[a])
                stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                def check(s):
                    s = s.content
                    return isInteger(s) and int(s) <= len(el) and int(s) > 0
                stock = yield from Discow.wait_for_message(author=msg.author, check=check)
                stock = el[int(stock.content)-1]
            elif len(el) == 1:
                stock = el[0]
            else:
                em = Embed(title="No Results", description="Could not find results matching your input.", colour=0xffd747)
                stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                return
            link = "https://www.nasdaq.com/symbol/"+stock[0]
            html_doc = req.urlopen(link)
            soup = BeautifulSoup(html_doc, 'html.parser')
            arr = " \u2b06 "
            if 'arrow-red' in soup.find("div", {"id": "qwidget-arrow"}).findChildren()[0].get("class"):
                arr = " \u2b07 "
            name = soup.find("div", {"id": "qwidget_pageheader"}).get_text()
            data = (soup.find("div", {"id": "qwidget_lastsale"}).get_text(), soup.find("div", {"id": "qwidget_netchange"}).get_text(), soup.find("div", {"id": "qwidget_percent"}).get_text())
            em = Embed(title=name, description="**"+data[0]+"**• "+data[1]+arr+data[2]+'\nFor more information go to [the nasdaq website]('+link+").\n\nThis was taken from [Stock-Viewer](https://github.com/UnsignedByte/Stock-Viewer) by [UnsignedByte](https://github.com/UnsignedByte).", colour=0xffd747)
            stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
        except err.HTTPError:
            em = Embed(title="Invalid Input", description="Your input was invalid", colour=0xd32323)
            stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)

add_message_handler(stock, "stock")
add_message_handler(daily, "daily")
add_message_handler(money, "money")
add_message_handler(slots, "slots")
add_message_handler(slots, "gamble")
