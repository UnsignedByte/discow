import asyncio
from discow.utils import *
from discow.handlers import add_message_handler, user_data, add_bot_message_handler
from discord import Embed
import time
from random import randint
from bs4 import BeautifulSoup
import urllib.request as req
import urllib.error as err
from commands.utilities import save
import re

currency_rates = {"bcbw":100, "cb":200, "mn":1}
interest_rate = 0.01

#used to add money
def give(amount, userid):
    if userid in user_data:
        user_data[userid]["money"]+=amount
    else:
        user_data[userid]["money"]=amount

#interest
def interest():
    for a in user_data:
        if "bank" in a:
            a["bank"]+=round(a["bank"]*interest_rate)

@asyncio.coroutine
def daily(Discow, msg):
    if msg.author.id in user_data:
        if (round(time.time())-user_data[msg.author.id]["daily"]) > 86400:
            if not "streak" in user_data[msg.author.id]:
                strk = 0
                user_data[msg.author.id]["streak"] = 1
            else:
                strk = 1
                user_data[msg.author.id]["streak"] += 1
            addedmoney = randint(10000*strk, 40000+10000*strk)
            user_data[msg.author.id]["money"]+=addedmoney
            user_data[msg.author.id]["daily"]=round(time.time())
            yield from Discow.send_message(msg.channel, "Added "+'{0:.2f}'.format(addedmoney/100)+" Mooney to your balance, "+msg.author.mention+"!\nYour daily streak is `"+str(user_data[msg.author.id]["streak"])+"`")
            yield from save(Discow, msg, overrideperms=True)
        else:
            seconds = 86400-(round(time.time())-user_data[msg.author.id]["daily"])
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            yield from Discow.send_message(msg.channel, "Not so fast! Please wait another %d hours, %02d minutes, and %02d seconds." % (h, m, s))
    else:
        addedmoney = randint(0, 40000)
        user_data[msg.author.id] = {"usr": msg.author, "streak": 1, "daily": round(time.time()), "work":0, "money": addedmoney}
        yield from Discow.send_message(msg.channel, "Added "+'{0:.2f}'.format(addedmoney/100)+" Mooney to your balance, "+msg.author.mention+"!\nYour daily streak is `1`.")

@asyncio.coroutine
def work(Discow, msg):
    addedmoney = randint(1000, 7500)
    if msg.author.id in user_data:
        if not "work" in user_data[msg.author.id]:
            user_data[msg.author.id]["work"] = 0
        if (round(time.time())-user_data[msg.author.id]["work"]) > 3600:
            user_data[msg.author.id]["money"]+=addedmoney
            user_data[msg.author.id]["work"]=round(time.time())
            yield from Discow.send_message(msg.channel, "You were paid "+'{0:.2f}'.format(addedmoney/100)+" Mooney for working, "+msg.author.mention+"!")
            yield from save(Discow, msg, overrideperms=True)
        else:
            seconds = 3600-(round(time.time())-user_data[msg.author.id]["work"])
            m, s = divmod(seconds, 60)
            yield from Discow.send_message(msg.channel, "You're too tired from working! Please wait another %02d minutes, and %02d seconds." % (m, s))
    else:
        user_data[msg.author.id] = {"usr": msg.author, "streak": 0, "daily": 0, "work": round(time.time()), "money": addedmoney}
        yield from Discow.send_message(msg.channel, "You were paid "+'{0:.2f}'.format(addedmoney/100)+" Mooney for working, "+msg.author.mention+"!")

@asyncio.coroutine
def deposit(Discow, msg):
    if msg.author.id in user_data:
        try:
            amount = round(float(strip_command(msg.content))*100)
        except ValueError:
            if strip_command(msg.content) == 'all':
                amount = user_data[msg.author.id]["money"]
            else:
                yield from Discow.send_message(msg.channel, "Your input was invalid! Please input a number.")
                return
        if amount <= user_data[msg.author.id]["money"]:
            if "bank" in user_data[msg.author.id]:
                user_data[msg.author.id]["bank"] += amount
            else:
                user_data[msg.author.id]["bank"] = amount
            user_data[msg.author.id]["money"]-=amount
            yield from Discow.send_message(msg.channel, "Deposited `"+'{0:.2f}'.format(amount/100)+"` Mooney to your Bovine Bank account.\nYour new bank balance is `"+'{0:.2f}'.format(user_data[msg.author.id]["bank"]/100)+"` Mooney.")
            yield from save(Discow, msg, overrideperms=True)
        else:
            yield from Discow.send_message(msg.channel, "You can't deposit that much money, you only have `"+'{0:.2f}'.format(user_data[msg.author.id]["money"]/100)+'`!')
    else:
        yield from Discow.send_message(msg.channel, "You have no Mooney to deposit! Try using `cow work` or `cow daily` first.")

@asyncio.coroutine
def withdraw(Discow, msg):
    if msg.author.id in user_data and "bank" in user_data[msg.author.id]:
        try:
            amount = round(float(strip_command(msg.content))*100)
        except ValueError:
            if strip_command(msg.content) == 'all':
                amount = user_data[msg.author.id]["bank"]
            else:
                yield from Discow.send_message(msg.channel, "Your input was invalid! Please input a number.")
                return
        if amount <= user_data[msg.author.id]["bank"]:
            user_data[msg.author.id]["bank"] -= amount
            user_data[msg.author.id]["money"] += amount
            yield from Discow.send_message(msg.channel, "Withdrew "+'{0:.2f}'.format(amount/100)+" from your Bovine Bank account.\nYour new bank balance is "+'{0:.2f}'.format(user_data[msg.author.id]["bank"]/100)+".")
            yield from save(Discow, msg, overrideperms=True)
        else:
            yield from Discow.send_message(msg.channel, "You can't withdraw that much money, you only have `"+'{0:.2f}'.format(user_data[msg.author.id]["bank"]/100)+'` in your bank!')
    else:
        yield from Discow.send_message(msg.channel, "You have no Mooney to withdraw! Try depositing mooney first")

@asyncio.coroutine
def convert(Discow, msg):
    try:
        info = parse_command(msg.content, 2)[1:]
    except IndexError:
        yield from Discow.send_message(msg.channel, "Available currencies:\n"+', '.join(currency_rates.keys()))
        return
    convertm = round(float(info[0])*100)
    if msg.author.id not in user_data:
        yield from Discow.send_message(msg.channel, "You have no mooney to convert! Try doing `cow daily` or `cow work` for mooney.")
        return
    elif user_data[msg.author.id]["money"] < convertm:
        yield from Discow.send_message(msg.channel, "You don't have that much mooney to convert! Try doing `cow daily` or `cow work` for mooney.\nYou currently have "+str(user_data[msg.author.id]["money"])+" Mooney.")
        return

    if info[1] in ["bcbw", "bitcoin but worse", "bitcoin", "bc"]:
        usr = yield from Discow.get_user_info("393248490739859458")
        info[1] = "bcbw"
        info[0] = str(int(info[0])*currency_rates["bcbw"])
    elif info[1] in ["cb", "cowbit"]:
        usr = yield from Discow.get_user_info("427890474708238339")
        info[1] = "cb"
        info[0] = str(int(info[0])*currency_rates["cb"])
    else:
        yield from Discow.send_message(msg.channel, "Not a valid currency!")
        return
    yield from Discow.send_message(msg.channel, "Converting "+'{0:.2f}'.format(convertm/100)+" Mooney to "+info[1]+"...")
    em = Embed(title="convert", description = ' '.join([msg.author.mention]+info))
    yield from Discow.send_message(Discow.get_channel("433441820102361110"), content=usr.mention, embed=em)
    success = yield from Discow.wait_for_reaction(emoji="👌", user=usr, timeout=15)
    if not success:
        yield from Discow.send_message(msg.channel, "Currency could not be converted. Either "+usr.mention+" is offline or is lagging.\nTry again later.")
    else:
        yield from Discow.send_message(msg.channel, "Convert successful! "+'{0:.2f}'.format(convertm/100)+" Mooney has been removed from your account.")
        user_data[msg.author.id]["money"]-=convertm
        yield from save(Discow, msg, overrideperms=True)

@asyncio.coroutine
def recieveconvert(Discow, msg):
    info = msg.embeds[0]["description"].split(' ')
    findusr = re.compile(r'<@([0-9]+)>')
    usr = yield from Discow.get_user_info(findusr.search(info[0]).group(1))
    if msg.mentions[0] == Discow.user:
        try:
            rate = currency_rates[info[2]]
        except KeyError:
            return
        if usr.id in user_data:
            user_data[usr.id]["money"]+=int(info[1])/rate*100
        else:
            user_data[usr.id] = {"usr": usr, "bank": 0, "streak": 0, "work": 0, "money":int(info[1])/rate*100, "daily":0}
        yield from save(Discow, msg, overrideperms=True)
        yield from Discow.add_reaction(msg, "👌")

@asyncio.coroutine
def leaderboard(Discow, msg):
    em = Embed(title="10 Richest Users", description="",colour=0xffd747)
    for a in sorted(user_data, key=lambda x:user_data[x]["money"]+(user_data[x]["bank"] if "bank" in user_data[x] else 0), reverse=True)[:10]:
        if "usr" not in user_data[a]:
            user_data[a]["usr"] = yield from Discow.get_user_info(a)
        em.description+="**"+user_data[a]["usr"].display_name+"**: "+'{0:.2f}'.format((user_data[a]["money"]+(user_data[a]["bank"] if "bank" in user_data[a] else 0))/100)+' total Mooney\n'
    yield from send_embed(Discow, msg, em)
    yield from save(Discow, msg, overrideperms=True)

@asyncio.coroutine
def money(Discow, msg):
    if len(msg.mentions) == 0:
        user = msg.author
    else:
        user = msg.mentions[0]
    em = Embed(title=user.display_name+"'s mooney",colour=0xffd747)
    if user.id in user_data:
        em.description = "%s currently has %s Mooney." % (user.mention, '{0:.2f}'.format(user_data[user.id]["money"]/100))
        if "stock" in user_data[user.id]:
            name = user.display_name+"'s owned stocks"
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
def bank(Discow, msg):
    if len(msg.mentions) > 0:
        yield from Discow.send_message(msg.channel, "Bovine Bank accounts are private! You can't check others' account values!")
        return

    em = Embed(title=msg.author.display_name+"'s Bovine Bank account",colour=0xffd747)
    if msg.author.id in user_data and "bank" in user_data[msg.author.id]:
        em.description = "%s currently has %s Mooney protected by Bovine Bank." % (msg.author.mention, '{0:.2f}'.format(user_data[msg.author.id]["bank"]/100))
    else:
        em.description = "%s has no Bovine Bank account." % msg.author.mention
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
                yield from Discow.send_message(msg.channel, msg.author.mention+" won "+'{0:.2f}'.format(moneychange/100)+" Mooney. Nice job!")
            else:
                yield from Discow.send_message(msg.channel, msg.author.mention+" lost "+'{0:.2f}'.format(-1*moneychange/100)+" Mooney. Better luck next time!")
            if msg.author.id in user_data:
                user_data[msg.author.id]["money"]+=moneychange
            else:
                user_data[msg.author.id] = {"usr": msg.author, "work": 0, "bank": 0, "daily": -86400, "money": moneychange}
    else:
        yield from Discow.send_message(msg.channel, "You have no mooney yet! Do `cow daily` to recieve your daily reward.")

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
            stock = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
            if not stock:
                return
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
                    num = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                    if not num:
                        return
                    yield from Discow.delete_message(num)
                    if num.content == 'cancel':
                        em = Embed(title="Stock Information", description="*Operation Cancelled*", colour=0xffd747)
                        stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
                        return
                    num = int(num.content)
                    if num*float(data[0][1:])*100 > user_data[msg.author.id]["money"]:
                        em.description = "How many shares would you like to buy? Input an integer.\n\nCannot buy "+str(num)+" shares, you do not have enough mooney!"
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
                em.description = "You bought "+str(num)+" shares for "+str(num*float(data[0][1:]))+" Mooney!"
                stockmsg = yield from edit_embed(Discow, stockmsg, em)
            else:
                em = Embed(title="No Mooney", description="You cannot buy stocks, as you have no mooney yet! Do `cow daily` to recieve your daily reward.", colour=0xd32323)
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
                    num = yield from Discow.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                    if not num:
                        return
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
                em.description = "You sold "+str(num)+" shares for "+str(num*float(data[0][1:]))+" Mooney!"
                stockmsg = yield from edit_embed(Discow, stockmsg, em)
            else:
                em = Embed(title="No Stocks", description="You have no stocks to sell.", colour=0xd32323)
                stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
    except err.HTTPError:
        em = Embed(title="Invalid Input", description="Your input was invalid", colour=0xd32323)
        stockmsg = yield from edit_embed(Discow, stockmsg, embed=em)
        return
    yield from save(Discow, msg, overrideperms=True)

add_message_handler(stock, "stocks")
add_message_handler(stock, "stock")
add_message_handler(daily, "daily")
add_message_handler(money, "money")
add_message_handler(money, "wealth")
add_message_handler(slots, "slots")
add_message_handler(slots, "gamble")
add_message_handler(work, "work")
add_message_handler(convert, "convert")
add_message_handler(deposit, "deposit")
add_message_handler(deposit, "dep")
add_message_handler(withdraw, "with")
add_message_handler(withdraw, "withdraw")
add_message_handler(leaderboard, "leader")
add_message_handler(leaderboard, "leaderboard")
add_message_handler(bank, "bank")

add_bot_message_handler(recieveconvert, "convert")
