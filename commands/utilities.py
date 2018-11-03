# @Author: Edmund Lam <edl>
# @Date:   18:59:11, 18-Apr-2018
# @Filename: utilities.py
# @Last modified by:   edl
# @Last modified time: 19:39:55, 02-Nov-2018


import asyncio
import pickle
from discow.utils import *
from discow.handlers import add_message_handler, add_private_message_handler, flip_shutdown, get_data
from discord import Embed, NotFound, HTTPException
import requests as req
import re
import traceback
from bs4 import BeautifulSoup
import greenlet

async def info(Bot, msg):
    em = Embed(title="Who am I?", colour=0x9542f4)
    em.description = "Hi, I'm [discow](https://github.com/UnsignedByte/discow), a discord bot created by <@418827664304898048>.\nOn this server, I am known as "+nickname(Bot.user, msg.server)+'.'
    em.add_field(name="Features", value="For information about my features do `"+discow_prefix+"help` or take a look at [our readme](https://github.com/UnsignedByte/discow/blob/master/README.md)!")
    await send_embed(Bot, msg, em)

async def execute(Bot, msg):
    if msg.author.id == "418827664304898048":

        #From https://stackoverflow.com/a/46087477/5844752
        class GreenAwait:
            def __init__(self, child):
                self.current = greenlet.getcurrent()
                self.value = None
                self.child = child

            def __call__(self, future):
                self.value = future
                self.current.switch()

            def __iter__(self):
                while self.value is not None:
                    yield self.value
                    self.value = None
                    self.child.switch()

        def gexec(code):
            child = greenlet.greenlet(exec)
            gawait = GreenAwait(child)
            child.switch(code, {'gawait': gawait, 'Bot': Bot, 'msg': msg})
            yield from gawait

        async def aexec(code):
            green = greenlet.greenlet(gexec)
            gen = green.switch(code)
            for future in gen:
                await future

        try:
            out = await aexec('import asyncio\nasync def run_exec():\n\t'+'\t'.join(re.search(r'`(?P<in>``)?(?P<body>(.?\s?)*)(?(in)```|`)', msg.content).group("body").strip().splitlines(True))+'\ngawait(run_exec())')
        except Exception:
            await send_embed(Bot, msg, Embed(title="Output", description=traceback.format_exc(), colour=0xd32323))

async def quote(Bot, msg):
    try:
        m = await Bot.get_message((msg.channel if len(msg.channel_mentions) == 0 else msg.channel_mentions[0]), strip_command(msg.content).split(" ")[0])
        em = Embed(title="Message Quoted by "+msg.author.display_name+":", colour=0x3b7ce5)
        desc = m.content
        print(desc)
        log = reversed([a async for a in Bot.logs_from(m.channel, limit=20, after=m)])
        print(log)
        for a in log:
            if a.author == m.author:
                if a.content:
                    desc+="\n"+a.content
            else:
                break
        async for a in Bot.logs_from(m.channel, limit=20, before=m):
            if a.author == m.author:
                if a.content:
                    desc=a.content+"\n"+desc
            else:
                break
        em.description = desc
        print(desc)
        await Bot.delete_message(msg)
        await send_embed(Bot, msg, em, time=m.timestamp, usr=m.author)
    except NotFound:
        em = Embed(title="Unable to Find Message", description="Could not find a message with that id.", colour=0xd32323)
        await send_embed(Bot, msg, em)

async def dictionary(Bot, msg):
    link="https://www.merriam-webster.com/dictionary/"
    x = strip_command(msg.content).replace(' ', '%20')
    em = Embed(title="Definition for "+x+".", description="Retrieving Definition...", colour=0x4e91fc)
    dictm = await send_embed(Bot, msg, em)

    try:
        response = req.get(link+x)
        response.raise_for_status()
        html_doc = response.text
        soup = BeautifulSoup(html_doc, 'html.parser')
    except req.exceptions.HTTPError as err:
        e = err.response.text
        try:
            em.description = "Could not find "+x+" in the dictionary. Choose one of the words below, or type 'cancel' to cancel."
            soup = BeautifulSoup(e.read(), 'html.parser')
            words = soup.find("ol", {"class":"definition-list"}).get_text().split()
            for i in range(0, len(words)):
                em.description+='\n**'+str(i+1)+":** *"+words[i]+'*'
            dictm = await edit_embed(Bot, dictm, em)
            while True:
                vm = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
                if not vm:
                    return
                v = vm.content
                if v == 'cancel':
                    em.description = "*Operation Cancelled*"
                    await Bot.delete_message(vm)
                    dictm = await edit_embed(Bot, dictm, em)
                    return
                elif isInteger(v):
                    if int(v)>=1 and int(v) <=len(words):
                        x = words[int(v)-1].replace(' ', "%20")
                        await Bot.delete_message(vm)
                        break
                else:
                    if v in words:
                        x = v.replace(' ', "%20")
                        await Bot.delete_message(vm)
                        break
            html_doc = req.get(link+x).text
            soup = BeautifulSoup(html_doc, 'html.parser')
            em.title = "Definition for "+x+"."
            em.description = "Retrieving Definition..."
            dictm = await edit_embed(Bot, dictm, em)
        except AttributeError:
            em.description = "Could not find "+x+" in the dictionary."
            dictm = await edit_embed(Bot, dictm, em)
            return

    em.description = ""
    txts = soup.find("div", {"id" : "entry-1"}).find("div", {"class":"vg"}).findAll("div", {"class":["sb", "has-sn"]}, recursive=False)
    for x in txts:
        l = list(filter(None,map(lambda x:x.strip(), x.get_text().split("\n"))))
        st = ""
        for a in l:
            if a.startswith(":"):
                st+=' '.join(a.strip().split())
            else:
                v1 = a.split()
                if isInteger(v1[0]):
                    st+="\n**__"+v1[0]+"__**"
                    v1 = v1[1:]
                for n in v1:
                    if isInteger(n.strip("()")):
                        st+="\n\t\t***"+n+"***"
                    elif len(n)==1:
                        st+="\n\t**"+n+"**"
                    else:
                        st+=" *"+n+"*"

        em.description+= '\n'+st
    em.description+="\n\nDefinitions retrieved from [The Merriam-Webster Dictionary](https://www.merriam-webster.com/) using [Dictionary](https://github.com/UnsignedByte/Dictionary) by [UnsignedByte](https://github.com/UnsignedByte)."
    dictm = await edit_embed(Bot, dictm, em)


async def purge(Bot, msg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_messages or msg.author.id == "418827664304898048":
        num = int(parse_command(msg.content, 1)[1].split(' ')[0])+1
        if num < 2:
            await Bot.send_message("There is no reason to delete 0 messages!")
        deletechunks = []
        def check(message):
            return not msg.mentions or msg.mentions[0].id == message.author.id
        try:
            await Bot.purge_from(msg.channel, limit=num, check=check)
            m = await Bot.send_message(msg.channel, format_response("**{_mention}** has cleared the last **{_number}** messages!", _msg=msg, _number=num-1))
        except discord.HTTPException:
            m = await Bot.send_message(msg.channel, format_response("You cannot bulk delete messages that are over 14 days old!!"))

        await asyncio.sleep(2)
        await Bot.delete_message(m)
    else:
        em = Embed(title="Insufficient Permissions", description=format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await send_embed(Bot, msg, em)

async def save(Bot, msg, overrideperms = False):
    if overrideperms or msg.author.id == "418827664304898048":
        if not overrideperms:
            em = Embed(title="Saving Data...", description="Saving...", colour=0xd32323)
            msg = await send_embed(Bot, msg, em)
            await asyncio.sleep(1)
        data = get_data()
        with open("Data/settings.txt", "wb") as f:
            pickle.dump(data[0], f)
        with open("Data/user_data.txt", "wb") as f:
            pickle.dump(data[1], f)
        with open("Data/quiz_data.txt", "wb") as f:
            pickle.dump(data[2], f)
        with open("Data/global_data.txt", "wb") as f:
            pickle.dump(data[3], f)
        with open("Data/world.txt", "wb") as f:
            pickle.dump(data[4], f)
        if not overrideperms:
            em.description = "Complete!"
            msg = await edit_embed(Bot, msg, embed=em)
            await asyncio.sleep(0.5)
            await Bot.delete_message(msg)
        return True
    else:
        em = Embed(title="Insufficient Permissions", description=format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await send_embed(Bot, msg, em)
        return False

async def shutdown(Bot, msg):
    flip_shutdown()
    istrue = await save(Bot, msg)
    if istrue:
        await Bot.logout()


add_message_handler(info, "hi")
add_message_handler(info, "info")
add_message_handler(shutdown, "close")
add_message_handler(shutdown, "shutdown")
add_message_handler(save, "save")
add_message_handler(purge, "purge")
add_message_handler(purge, "clear")
add_message_handler(quote, "quote")
add_message_handler(dictionary, "define")
add_message_handler(dictionary, "dictionary")
add_message_handler(execute, "exec")
add_private_message_handler(execute, "exec")
