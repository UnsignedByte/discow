# @Author: Edmund Lam <edl>
# @Date:   18:59:11, 18-Apr-2018
# @Filename: economy.py
# @Last modified by:   edl
# @Last modified time: 18:18:03, 11-Nov-2018


import asyncio
from utils import msgutils, strutils, utils, objutils, datautils
from discow.handlers import add_message_handler, bot_data, add_bot_message_handler, add_private_message_handler
from discord import Embed
import time
from random import randint
from bs4 import BeautifulSoup
import requests as req
import re

print("\tInitializing Economy")

currency_rates = {"bcbw":100, "cb":200}
interest_rate = 0.01

#Desired Exchange Rate (1 Mooney = ??? Universal)
DESIRED_EXCHANGE_RATE = 5
#Highest Exchange Rate (1 Mooney = ??? Universal)
MAXIMUM_EXCHANGE_RATE = 500
#Point at which Desired Exchange Rate is reached
NORMALIZED_MONEY_AMOUNT = 100000

MOONEY_TOTAL = 0
UNIVERSAL_CONVERSION_RATE = 0

def updateworldsum():
    global MOONEY_TOTAL
    global UNIVERSAL_CONVERSION_RATE
    total = 0
    for a in bot_data['user_data']:
        total+=datautils.nested_get('user_data', a, 'money', default=0)+datautils.nested_get('user_data', a, 'bank', default=0)
    MOONEY_TOTAL = total/100
    UNIVERSAL_CONVERSION_RATE = 1/((1/MAXIMUM_EXCHANGE_RATE)+MOONEY_TOTAL/(DESIRED_EXCHANGE_RATE*NORMALIZED_MONEY_AMOUNT))
updateworldsum()

#used to add money
def give(amount, userid):
    increment(userid, "money", amount)

#increments element
def increment(userid, element, amount):
    if userid in bot_data['user_data'] and element in bot_data['user_data'][userid]:
        bot_data['user_data'][userid][element]+=amount
    else:
        if userid in bot_data['user_data']:
            bot_data['user_data'][userid][element]=amount
        else:
            bot_data['user_data'][userid] = {element:amount}

#sets element
def set_element(userid, element, amount):
    if userid in bot_data['user_data']:
        bot_data['user_data'][userid][element]=amount
    else:
        bot_data['user_data'][userid] = {element:amount}

async def transfer(Bot, msg):
    try:
        amt = int(float(strutils.strip_command(msg.content).split(' ', 1)[0])*100)
        if amt <= bot_data['user_data'][msg.author.id]["money"]:
            give(amt, msg.mentions[0].id)
            give(-1*amt, msg.author.id)
            em = Embed(title="Money Transfer", description='{0:.2f}'.format(amt/100)+" mooney given to "+msg.mentions[0].mention, colour=0xffd747)
            await msgutils.send_embed(Bot, msg, em)
        else:
            await Bot.send_message(msg.channel, "You don't have that much money to transfer!")
    except (ValueError, TypeError):
        em = Embed(title="Invalid Amount", description="Mooney to give must be a number.", colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)
    except IndexError:
        em = Embed(title="Missing User", description="You must specify the user to give mooney to.", colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)

async def addMooney(Bot, msg):
    if msg.author.id == "418827664304898048":
        try:
            amt = int(float(strutils.strip_command(msg.content).split(' ', 1)[0])*100)
            give(amt, msg.mentions[0].id)
            em = Embed(title="Money Added", description='{0:.2f}'.format(amt/100)+" mooney given to "+msg.mentions[0].mention, colour=0xffd747)
            await msgutils.send_embed(Bot, msg, em)
        except (ValueError, TypeError):
            em = Embed(title="Invalid Amount", description="Mooney to give must be a number.", colour=0xd32323)
            await msgutils.send_embed(Bot, msg, em)
        except IndexError:
            em = Embed(title="Missing User", description="You must specify the user to give mooney to.", colour=0xd32323)
            await msgutils.send_embed(Bot, msg, em)
    else:
        em = Embed(title="Insufficient Permissions", description=strutils.format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)

#interest

async def interest():
    for a in bot_data['user_data']:
        bbal = datautils.nested_get('user_data', a, 'bank', default=0)
        bbal += round(bbal*interest_rate)


async def economy(Bot, msg):
    updateworldsum()
    em = Embed(title='Mooney Economy Information', description='**'+'{0:.2f}'.format(MOONEY_TOTAL)+"** Total Mooney", colour=0xffd747)
    em.add_field(name="Current Conversion rate to Universal", value="**1** Mooney to **"+str(UNIVERSAL_CONVERSION_RATE)+"** Universal Currency")
    em.add_field(name="Default Conversion rate to Universal", value="**1** Mooney to **"+str(DESIRED_EXCHANGE_RATE)+"** Universal Currency")
    await msgutils.send_embed(Bot, msg, embed=em)


async def daily(Bot, msg):
    if msg.author.id in bot_data['user_data']:
        if (round(time.time())-datautils.nested_get('user_data', msg.author.id, 'daily', default=-86400)) > 86400:
            if (round(time.time())-bot_data['user_data'][msg.author.id]["daily"]) < 172800:
                datautils.nested_addition(1, 'user_data', msg.author.id, 'streak', default=0)
            else:
                bot_data['user_data'][msg.author.id]["streak"] = 1
            addedmoney = randint(10000*bot_data['user_data'][msg.author.id]["streak"], 40000+10000*bot_data['user_data'][msg.author.id]["streak"])
            bot_data['user_data'][msg.author.id]["money"]+=addedmoney
            bot_data['user_data'][msg.author.id]["daily"]=round(time.time())
            await Bot.send_message(msg.channel, "Added "+'{0:.2f}'.format(addedmoney/100)+" Mooney to your balance, "+msg.author.mention+"!\nYour daily streak is `"+str(bot_data['user_data'][msg.author.id]["streak"])+"`")
        else:
            seconds = 86400-(round(time.time())-bot_data['user_data'][msg.author.id]["daily"])
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            await Bot.send_message(msg.channel, "Not so fast! Please wait another %d hours, %02d minutes, and %02d seconds." % (h, m, s))
    else:
        addedmoney = randint(0, 40000)
        bot_data['user_data'][msg.author.id] = {"usr": msg.author, "streak": 1, "daily": round(time.time()), "work":0, "money": addedmoney}
        await Bot.send_message(msg.channel, "Added "+'{0:.2f}'.format(addedmoney/100)+" Mooney to your balance, "+msg.author.mention+"!\nYour daily streak is `1`.")


async def work(Bot, msg):
    addedmoney = randint(1000, 7500)
    if msg.author.id in bot_data['user_data']:
        if (round(time.time())-datautils.nested_get('user_data', msg.author.id, 'work', default=0)) > 3600:
            bot_data['user_data'][msg.author.id]["money"]+=addedmoney
            bot_data['user_data'][msg.author.id]["work"]=round(time.time())
            await Bot.send_message(msg.channel, "You were paid "+'{0:.2f}'.format(addedmoney/100)+" Mooney for working, "+msg.author.mention+"!")
        else:
            seconds = 3600-(round(time.time())-bot_data['user_data'][msg.author.id]["work"])
            m, s = divmod(seconds, 60)
            await Bot.send_message(msg.channel, "You're too tired from working! Please wait another %02d minutes, and %02d seconds." % (m, s))
    else:
        bot_data['user_data'][msg.author.id] = {"usr": msg.author, "streak": 0, "daily": 0, "work": round(time.time()), "money": addedmoney}
        await Bot.send_message(msg.channel, "You were paid "+'{0:.2f}'.format(addedmoney/100)+" Mooney for working, "+msg.author.mention+"!")


async def deposit(Bot, msg):
    if msg.author.id in bot_data['user_data']:
        try:
            amount = round(float(strutils.strip_command(msg.content))*100)
        except ValueError:
            if strutils.strip_command(msg.content) == 'all':
                amount = bot_data['user_data'][msg.author.id]["money"]
            else:
                await Bot.send_message(msg.channel, "Your input was invalid! Please input a number.")
                return
        if amount <= bot_data['user_data'][msg.author.id]["money"]:
            datautils.nested_addition(amount, 'user_data', msg.author.id, 'bank', default=0)
            bot_data['user_data'][msg.author.id]["money"]-=amount
            await Bot.send_message(msg.channel, "Deposited `"+'{0:.2f}'.format(amount/100)+"` Mooney to your Bovine Bank account.\nYour new bank balance is `"+'{0:.2f}'.format(bot_data['user_data'][msg.author.id]["bank"]/100)+"` Mooney.")
        else:
            await Bot.send_message(msg.channel, "You can't deposit that much money, you only have `"+'{0:.2f}'.format(bot_data['user_data'][msg.author.id]["money"]/100)+'`!')
    else:
        await Bot.send_message(msg.channel, "You have no Mooney to deposit! Try using `cow work` or `cow daily` first.")


async def withdraw(Bot, msg):
    if msg.author.id in bot_data['user_data'] and "bank" in bot_data['user_data'][msg.author.id]:
        try:
            amount = round(float(strutils.strip_command(msg.content))*100)
        except ValueError:
            if strutils.strip_command(msg.content) == 'all':
                amount = bot_data['user_data'][msg.author.id]["bank"]
            else:
                await Bot.send_message(msg.channel, "Your input was invalid! Please input a number.")
                return
        if amount <= bot_data['user_data'][msg.author.id]["bank"]:
            bot_data['user_data'][msg.author.id]["bank"] -= amount
            bot_data['user_data'][msg.author.id]["money"] += amount
            await Bot.send_message(msg.channel, "Withdrew "+'{0:.2f}'.format(amount/100)+" from your Bovine Bank account.\nYour new bank balance is "+'{0:.2f}'.format(bot_data['user_data'][msg.author.id]["bank"]/100)+".")
        else:
            await Bot.send_message(msg.channel, "You can't withdraw that much money, you only have `"+'{0:.2f}'.format(bot_data['user_data'][msg.author.id]["bank"]/100)+'` in your bank!')
    else:
        await Bot.send_message(msg.channel, "You have no Mooney to withdraw! Try depositing mooney first")


async def convert(Bot, msg):
    updateworldsum()
    try:
        info = strutils.parse_command(msg.content, 2)[1:]
    except IndexError:
        await Bot.send_message(msg.channel, "Available currencies:\n"+', '.join(currency_rates.keys()))
        return
    convertm = round(float(info[0])*100)
    if msg.author.id not in bot_data['user_data']:
        await Bot.send_message(msg.channel, "You have no mooney to convert! Try doing `cow daily` or `cow work` for mooney.")
        return
    elif bot_data['user_data'][msg.author.id]["money"] < convertm:
        await Bot.send_message(msg.channel, "You don't have that much mooney to convert! Try doing `cow daily` or `cow work` for mooney.\nYou currently have "+'{0:.2f}'.format(bot_data['user_data'][msg.author.id]["money"]/100)+" Mooney.")
        return

    info[0] = str(float(info[0])*UNIVERSAL_CONVERSION_RATE)
    if info[1] in ["bcbw", "bitcoin but worse", "bitcoin", "bc"]:
        usr = await Bot.get_user_info("393248490739859458")
        info[1] = "bcbw"
    elif info[1] in ["cb", "cowbit"]:
        usr = await Bot.get_user_info("427890474708238339")
        info[1] = "cb"
    else:
        await Bot.send_message(msg.channel, "Not a valid currency!")
        return
    await Bot.send_message(msg.channel, "Converting "+'{0:.2f}'.format(convertm/100)+" Mooney to "+info[1]+"...")
    em = Embed(title="convert", description = msg.author.mention+' '+info[0], colour=0xffd747)
    await Bot.send_message(Bot.get_channel("433441820102361110"), content=usr.mention, embed=em)
    success = await Bot.wait_for_reaction(emoji="👌", user=usr, timeout=15)
    if not success:
        await Bot.send_message(msg.channel, "Currency could not be converted. Either "+usr.mention+" is offline or is lagging.\nTry again later.")
    else:
        await Bot.send_message(msg.channel, "Convert successful! "+'{0:.2f}'.format(convertm/100)+" Mooney has been converted to "+info[1]+".")
        bot_data['user_data'][msg.author.id]["money"]-=convertm


async def recieveconvert(Bot, msg):
    info = msg.embeds[0]["description"].split(' ')
    findusr = re.compile(r'<@!?([0-9]+)>')
    usr = await Bot.get_user_info(findusr.search(info[0]).group(1))
    if msg.mentions[0] == Bot.user:
        if len(info) == 3:
            rate = currency_rates[info[2]]
        else:
            rate = UNIVERSAL_CONVERSION_RATE
        if usr.id in bot_data['user_data']:
            bot_data['user_data'][usr.id]["money"]+=round(float(info[1])/rate*100)
        else:
            bot_data['user_data'][usr.id] = {"usr": usr, "bank": 0, "streak": 0, "work": 0, "money":round(float(info[1])/rate*100), "daily":0}
        await Bot.add_reaction(msg, "👌")


async def leaderboard(Bot, msg):
    em = Embed(title="10 Richest Users", description="",colour=0xffd747)
    for a in sorted(bot_data['user_data'], key=lambda x:bot_data['user_data'][x]["money"]+(bot_data['user_data'][x]["bank"] if "bank" in bot_data['user_data'][x] else 0), reverse=True)[:10]:
        if "usr" not in bot_data['user_data'][a]:
            bot_data['user_data'][a]["usr"] = await Bot.get_user_info(a)
        em.description+="**"+bot_data['user_data'][a]["usr"].name+"**: "+'{0:.2f}'.format((bot_data['user_data'][a]["money"]+(bot_data['user_data'][a]["bank"] if "bank" in bot_data['user_data'][a] else 0))/100)+' total Mooney\n'
    await msgutils.send_embed(Bot, msg, em)


async def money(Bot, msg):
    if len(msg.mentions) == 0:
        user = msg.author
    else:
        user = msg.mentions[0]
    em = Embed(title=user.display_name+"'s mooney",colour=0xffd747)
    if user.id in bot_data['user_data']:
        bot_data['user_data'][user.id]["money"] = int(bot_data['user_data'][user.id]["money"])
        em.description = "%s currently has %s Mooney." % (user.mention, '{0:.2f}'.format(bot_data['user_data'][user.id]["money"]/100))
        if "stock" in bot_data['user_data'][user.id]:
            name = user.display_name+"'s owned stocks"
            desc = ""
            for k,v in bot_data['user_data'][user.id]["stock"].items():
                if v > 0:
                    desc+="**Stock name:** "+k+"\t**Number of shares owned:** "+str(v)+".\n"
            if desc:
                em.add_field(name=name, value=desc)
    else:
        em.description = "%s is new and currently has no money." % user.mention

    await msgutils.send_embed(Bot, msg, em)


async def bank(Bot, msg):
    if len(msg.mentions) > 0:
        await Bot.send_message(msg.channel, "Bovine Bank accounts are private! You can't check others' account values!")
        return

    em = Embed(title=msg.author.display_name+"'s Bovine Bank account",colour=0xffd747)
    if msg.author.id in bot_data['user_data'] and "bank" in bot_data['user_data'][msg.author.id]:
        em.description = "%s currently has %s Mooney protected by Bovine Bank." % (msg.author.mention, '{0:.2f}'.format(bot_data['user_data'][msg.author.id]["bank"]/100))
    else:
        em.description = "%s has no Bovine Bank account." % msg.author.mention
    await msgutils.send_embed(Bot, msg, em)


async def slots(Bot, msg):
    bet = int(float(strutils.strip_command(msg.content))*100)
    if msg.author.id in bot_data['user_data']:
        if bet > bot_data['user_data'][msg.author.id]["money"]:
            await Bot.send_message(msg.channel, "You don't have that much to bet, silly!")
        else:
            moneychange = randint(-1*bet, bet)
            if moneychange >= 0:
                await Bot.send_message(msg.channel, msg.author.mention+" won "+'{0:.2f}'.format(moneychange/100)+" Mooney. Nice job!")
            else:
                await Bot.send_message(msg.channel, msg.author.mention+" lost "+'{0:.2f}'.format(-1*moneychange/100)+" Mooney. Better luck next time!")
            datautils.nested_addition(moneychange, 'user_data', msg.author.id, 'money', default=0)
    else:
        await Bot.send_message(msg.channel, "You have no mooney yet! Do `cow daily` to recieve your daily reward.")


async def stock(Bot, msg):
    subcomms = {
    "get":"get",
    "info":"get",
    "sell":"sell",
    "invest":"buy",
    "buy":"buy"
    }

    em = Embed(title="Stock information", description="Retrieving data...", colour=0xffd747)
    stockmsg = await msgutils.send_embed(Bot, msg, em)
    try:
        cont = strutils.strip_command(msg.content)
    except IndexError:
        em = Embed(title="Missing Inputs", description="Not enough inputs provided for **stock**.", colour=0xd32323)
        await msgutils.edit_embed(Bot, stockmsg, em)
        return
    minfo = cont.split(' ')
    if len(minfo) > 2:
        em = Embed(title="Invalid Input", description="Stock Name cannot contain whitespace", colour=0xd32323)
        stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
        return
    if len(minfo) == 1:
        cont = minfo[0]
        commtype="get"
    elif len(minfo) == 2:
        try:
            commtype = subcomms[minfo[0]]
        except KeyError:
            em = Embed(title="Invalid Command", description="Could not find subcommand **"+minfo[0]+"**.\nValid subcommands are **get**, **sell**, and **buy**.", colour=0xd32323)
            await msgutils.edit_embed(Bot, stockmsg, em)
            return
        cont=minfo[1]

    link="https://www.nasdaq.com/symbol/?Load=true&Search="+cont
    try:
        response = req.get(link)
        response.raise_for_status()
        html_doc = response.text
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
        el = utils.group(el, 3)
        if len(el) > 1:
            em = Embed(title="Multiple results found. Choose one. Type `cancel` to cancel", description="", colour=0xffd747)
            for a in range(0, len(el)):
                em.description+='\n'+str(a+1)+': '+' '.join(el[a])
            stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
            def check(s):
                s = s.content
                if s == 'cancel':
                    return True
                return objutils.integer(s) and int(s) <= len(el) and int(s) > 0

            stock = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
            if not stock:
                return
            await Bot.delete_message(stock)
            if stock.content == 'cancel':
                em = Embed(title="Stock Information", description="*Operation Cancelled*", colour=0xffd747)
                stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
                return
            stock = el[int(stock.content)-1]
        elif len(el) == 1:
            stock = el[0]
        else:
            em = Embed(title="No Results", description="Could not find results matching your input.", colour=0xffd747)
            stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
            return
        link = "https://www.nasdaq.com/symbol/"+stock[0]
        response = req.get(link)
        response.raise_for_status()
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
        arr = " \u2b06 "
        if 'arrow-red' in soup.find("div", {"id": "qwidget-arrow"}).findChildren()[0].get("class"):
            arr = " \u2b07 "
        name = soup.find("div", {"id": "qwidget_pageheader"}).get_text()
        data = (soup.find("div", {"id": "qwidget_lastsale"}).get_text(), soup.find("div", {"id": "qwidget_netchange"}).get_text(), soup.find("div", {"id": "qwidget_percent"}).get_text())
        info = "**"+data[0]+"**• "+data[1]+arr+data[2]+'\nFor more information go to [the nasdaq website]('+link+").\n\nThis was taken from [Stock-Viewer](https://github.com/UnsignedByte/Stock-Viewer) by [UnsignedByte](https://github.com/UnsignedByte)."
        if commtype == "get":
            em = Embed(title=name, description=info, colour=0xffd747)
            stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
        if commtype == "buy":
            if msg.author.id in bot_data['user_data']:
                def check(s):
                    s = s.content
                    if s == 'cancel':
                        return True
                    return objutils.integer(s) and int(s) > 0
                em = Embed(title="Buying Shares...", description="How many shares would you like to buy? Input an integer.", colour=0xffd747)
                em.add_field(name=name, value=info)
                while True:
                    stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
                    num = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                    if not num:
                        return
                    await Bot.delete_message(num)
                    if num.content == 'cancel':
                        em = Embed(title="Stock Information", description="*Operation Cancelled*", colour=0xffd747)
                        stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
                        return
                    num = int(num.content)
                    if num*float(data[0][1:])*100 > bot_data['user_data'][msg.author.id]["money"]:
                        em.description = "How many shares would you like to buy? Input an integer.\n\nCannot buy "+str(num)+" shares, you do not have enough mooney!"
                    else:
                        break
                bot_data['user_data'][msg.author.id]["money"]-=num*float(data[0][1:])*100
                if "stock" in bot_data['user_data'][msg.author.id]:
                    if stock[0] in bot_data['user_data'][msg.author.id]["stock"]:
                        bot_data['user_data'][msg.author.id]["stock"][stock[0]] += num
                    else:
                        bot_data['user_data'][msg.author.id]["stock"][stock[0]] = num
                else:
                    bot_data['user_data'][msg.author.id]["stock"] = {}
                    bot_data['user_data'][msg.author.id]["stock"][stock[0]] = num
                em.title = "Shares Bought."
                em.description = "You bought "+str(num)+" shares for "+str(num*float(data[0][1:]))+" Mooney!"
                stockmsg = await msgutils.edit_embed(Bot, stockmsg, em)
            else:
                em = Embed(title="No Mooney", description="You cannot buy stocks, as you have no mooney yet! Do `cow daily` to recieve your daily reward.", colour=0xd32323)
                stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
        elif commtype == "sell":
            if msg.author.id in bot_data['user_data'] and "stock" in bot_data['user_data'][msg.author.id] and stock[0] in bot_data['user_data'][msg.author.id]["stock"]:
                def check(s):
                    s = s.content
                    if s == 'cancel':
                        return True
                    return objutils.integer(s) and int(s) > 0
                em = Embed(title="Selling Shares...", description="How many shares would you like to sell? Input an integer.", colour=0xffd747)
                em.add_field(name=name, value=info)
                while True:
                    stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
                    num = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel, check=check)
                    if not num:
                        return
                    await Bot.delete_message(num)
                    if num.content == 'cancel':
                        em = Embed(title="Stock Information", description="*Operation Cancelled*", colour=0xffd747)
                        stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
                        return
                    num = int(num.content)
                    if num > bot_data['user_data'][msg.author.id]["stock"][stock[0]]:
                        em.description = "How many shares would you like to sell? Input an integer.\n\nCannot sell "+str(num)+" shares, you do not own that many!"
                    else:
                        break
                bot_data['user_data'][msg.author.id]["money"]+=num*float(data[0][1:])*100
                bot_data['user_data'][msg.author.id]["stock"][stock[0]]-=num
                em.title = "Shares sold."
                em.description = "You sold "+str(num)+" shares for "+str(num*float(data[0][1:]))+" Mooney!"
                stockmsg = await msgutils.edit_embed(Bot, stockmsg, em)
            else:
                em = Embed(title="No Stocks", description="You have no stocks to sell.", colour=0xd32323)
                stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
    except req.exceptions.HTTPError:
        em = Embed(title="Invalid Input", description="Your input was invalid", colour=0xd32323)
        stockmsg = await msgutils.edit_embed(Bot, stockmsg, embed=em)
        return

add_message_handler(stock, "stocks")
add_message_handler(stock, "stock")
add_message_handler(daily, "daily")
add_message_handler(money, "money")
add_message_handler(money, "mooney")
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
add_message_handler(economy, "economy")
add_message_handler(addMooney, "add")
add_message_handler(transfer, "give")
add_message_handler(transfer, "transfer")
add_private_message_handler(addMooney, "add")

add_bot_message_handler(recieveconvert, "convert")
print("\tEconomy Initialized")
