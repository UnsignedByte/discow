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
    addedmoney = randint(40000, 60000)
    if msg.author.id in user_data:
        if (round(time.time())-user_data[msg.author.id]["daily"]) > 86400:
            user_data[msg.author.id]["money"]+=addedmoney
            user_data[msg.author.id]["daily"]=round(time.time())
            yield from Discow.send_message(msg.channel, "Added $"+str(addedmoney/100)+" to your balance, "+msg.author.mention+"!")
        else:
            seconds = 86400-(round(time.time())-user_data[msg.author.id]["daily"])
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            yield from Discow.send_message(msg.channel, "Not so fast! Please wait another %d hours, %02d minutes, and %02d seconds." % (h, m, s))
    else:
        user_data[msg.author.id] = {"daily": round(time.time()), "money": addedmoney}
        yield from Discow.send_message(msg.channel, "Added $"+str(addedmoney/100)+" to your balance, "+msg.author.mention+"!")

@asyncio.coroutine
def money(Discow, msg):
    em = Embed(title=msg.author.display_name+"'s money",colour=0xffd747)
    if len(msg.mentions) == 0:
        user = msg.author
    else:
        user = msg.mentions[0]
    if user.id in user_data:
        em.description = "%s currently has $%s." % (user.mention, user_data[user.id]["money"]/100)
        if "stock" in user_data[user.id]:
            name = msg.author.display_name+"'s owned stocks"
            desc = ""
            for k,v in user_data[user.id]["stock"].items():
                if v > 0:
                    desc+="**Stock name:** "+k+"\t**Number of shares owned:** "+str(v)+".\n"
            if desc:
                em.add_field(name=name, value=desc)
    else:
        em.description = "%s is new and currently has no money." % user.mention

    yield from send_embed(Discow, msg, em)

@asyncio.coroutine
def slots(Discow, msg):
    bet = int(float(strip_command(msg.content))*100)
    if msg.author.id in user_data:
        if bet > user_data[msg.author.id]["money"]:
            yield from Discow.send_message(msg.channel, "You don't have that much to bet, silly!")
        else:
            moneychange = randint(-1*bet, bet)
            if moneychange >= 0:
                yield from Discow.send_message(msg.channel, msg.author.mention+" won $"+str(moneychange/100)+". Nice job!")
            else:
                yield from Discow.send_message(msg.channel, msg.author.mention+" lost $"+str(-1*moneychange/100)+". Better luck next time!")
            if msg.author.id in user_data:
                user_data[msg.author.id]["money"]+=moneychange
            else:
                user_data[msg.author.id] = {"daily": -86400, "money": moneychange}
    else:
        yield from Discow.send_message(msg.channel, "You have no money yet! Do `cow daily` to recieve your daily reward.")

@asyncio.coroutine
def stock(Discow, msg):
    subcomms = {
    "get":"get",
    "info":"get",
    "sell":"sell",
    "invest":"buy",
    "buy":"buy"
    }

    em = Embed(title="Stock information", description="Retrieving data...", colour=0xffd747)
    stockmsg = yield from send_embed(Discow, msg, em)
    try:
        cont = strip_command(msg.content)
    except IndexError:
        em = Embed(title="Missing Inputs", description="Not enough inputs provided for **stock**.", colour=0xd32323)
        yield from edit_embed(Discow, stockmsg, em)
        return
    minfo = cont.split(' ')
    if len(minfo) > 2:
        em = Embed(title="Invalid Input", description="Stock Name cannot contain whitespace", colour=0xd32323)
        stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
        return
    if len(minfo) == 1:
        cont = minfo[0]
        commtype="get"
    elif len(minfo) == 2:
        try:
            commtype = subcomms[minfo[0]]
        except KeyError:
            em = Embed(title="Invalid Command", description="Could not find subcommand **"+minfo[0]+"**.\nValid subcommands are **get**, **sell**, and **buy**.", colour=0xd32323)
            yield from edit_embed(Discow, stockmsg, em)
            return
        cont=minfo[1]

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
            em = Embed(title="Multiple results found. Choose one. Type `cancel` to cancel", description="", colour=0xffd747)
            for a in range(0, len(el)):
                em.description+='\n'+str(a+1)+': '+' '.join(el[a])
            stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
            def check(s):
                s = s.content
                if s == 'cancel':
                    return True
                return isInteger(s) and int(s) <= len(el) and int(s) > 0
            stock = yield from Discow.wait_for_message(author=msg.author, channel=msg.channel, check=check)
            yield from Discow.delete_message(stock)
            if stock.content == 'cancel':
                em = Embed(title="Stock Information", description="*Operation Cancelled*", colour=0xffd747)
                stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                return
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
        info = "**"+data[0]+"**• "+data[1]+arr+data[2]+'\nFor more information go to [the nasdaq website]('+link+").\n\nThis was taken from [Stock-Viewer](https://github.com/UnsignedByte/Stock-Viewer) by [UnsignedByte](https://github.com/UnsignedByte)."
        if commtype == "get":
            em = Embed(title=name, description=info, colour=0xffd747)
            stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
        if commtype == "buy":
            if msg.author.id in user_data:
                def check(s):
                    s = s.content
                    if s == 'cancel':
                        return True
                    return isInteger(s) and int(s) > 0
                em = Embed(title="Buying Shares...", description="How many shares would you like to buy? Input an integer.", colour=0xffd747)
                em.add_field(name=name, value=info)
                while True:
                    stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                    num = yield from Discow.wait_for_message(author=msg.author, channel=msg.channel, check=check)
                    yield from Discow.delete_message(num)
                    if num.content == 'cancel':
                        em = Embed(title="Stock Information", description="*Operation Cancelled*", colour=0xffd747)
                        stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                        return
                    num = int(num.content)
                    if num*float(data[0][1:])*100 > user_data[msg.author.id]["money"]:
                        em.description = "How many shares would you like to buy? Input an integer.\n\nCannot buy "+str(num)+" shares, you do not have enough money!"
                    else:
                        break

                user_data[msg.author.id]["money"]-=num*float(data[0][1:])*100
                if "stock" in user_data[msg.author.id]:
                    if stock[0] in user_data[msg.author.id]["stock"]:
                        user_data[msg.author.id]["stock"][stock[0]] += num
                    else:
                        user_data[msg.author.id]["stock"][stock[0]] = num
                else:
                    user_data[msg.author.id]["stock"] = {}
                    user_data[msg.author.id]["stock"][stock[0]] = num
                em.title = "Shares Bought."
                em.description = "You bought "+str(num)+" shares for $"+str(num*float(data[0][1:]))+"!"
                stockmsg = yield from edit_embed(Discow, stockmsg, em)
            else:
                em = Embed(title="No Money", description="You cannot buy stocks, as you have no money yet! Do `cow daily` to recieve your daily reward.", colour=0xd32323)
                stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
        elif commtype == "sell":
            if msg.author.id in user_data and "stock" in user_data[msg.author.id] and stock[0] in user_data[msg.author.id]["stock"]:
                def check(s):
                    s = s.content
                    if s == 'cancel':
                        return True
                    return isInteger(s) and int(s) > 0
                em = Embed(title="Selling Shares...", description="How many shares would you like to sell? Input an integer.", colour=0xffd747)
                em.add_field(name=name, value=info)
                while True:
                    stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                    num = yield from Discow.wait_for_message(author=msg.author, channel=msg.channel, check=check)
                    yield from Discow.delete_message(num)
                    if num.content == 'cancel':
                        em = Embed(title="Stock Information", description="*Operation Cancelled*", colour=0xffd747)
                        stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                        return
                    num = int(num.content)
                    if num > user_data[msg.author.id]["stock"][stock[0]]:
                        em.description = "How many shares would you like to sell? Input an integer.\n\nCannot sell "+str(num)+" shares, you do not own that many!"
                    else:
                        break
                user_data[msg.author.id]["money"]+=num*float(data[0][1:])*100
                user_data[msg.author.id]["stock"][stock[0]]-=num
                em.title = "Shares sold."
                em.description = "You sold "+str(num)+" shares for $"+str(num*float(data[0][1:]))+"!"
                stockmsg = yield from edit_embed(Discow, stockmsg, em)
            else:
                em = Embed(title="No Stocks", description="You have no stocks to sell.", colour=0xd32323)
                stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
    except err.HTTPError:
        em = Embed(title="Invalid Input", description="Your input was invalid", colour=0xd32323)
        stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)

add_message_handler(stock, "stock")
add_message_handler(daily, "daily")
add_message_handler(money, "money")
add_message_handler(money, "wealth")
add_message_handler(slots, "slots")
add_message_handler(slots, "gamble")
