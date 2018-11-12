# @Author: Edmund Lam <edl>
# @Date:   18:59:11, 18-Apr-2018
# @Filename: utilities.py
# @Last modified by:   edl
# @Last modified time: 18:18:55, 11-Nov-2018

from pprint import pformat
import asyncio
import pickle
from utils import msgutils, strutils, datautils, userutils, objutils
from discow.handlers import add_message_handler, add_private_message_handler, flip_shutdown, add_regex_message_handler, bot_data
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
    await msgutils.send_embed(Bot, msg, em)

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
            await msgutils.send_embed(Bot, msg, Embed(title="Output", description=traceback.format_exc(), colour=0xd32323))

async def quote(Bot, msg):
    try:
        m = await Bot.get_message((msg.channel if len(msg.channel_mentions) == 0 else msg.channel_mentions[0]), strutils.strutils.strip_command(msg.content).split(" ")[0])
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
        await msgutils.send_embed(Bot, msg, em, time=m.timestamp, usr=m.author)
    except NotFound:
        em = Embed(title="Unable to Find Message", description="Could not find a message with that id.", colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)

async def dictionary(Bot, msg):
    link="https://www.merriam-webster.com/dictionary/"
    x = strutils.strutils.strip_command(msg.content).replace(' ', '%20')
    em = Embed(title="Definition for "+x+".", description="Retrieving Definition...", colour=0x4e91fc)
    dictm = await msgutils.send_embed(Bot, msg, em)

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
            dictm = await msgutils.send_embed(Bot, dictm, em)
            while True:
                vm = await Bot.wait_for_message(timeout=600, author=msg.author, channel=msg.channel)
                if not vm:
                    return
                v = vm.content
                if v == 'cancel':
                    em.description = "*Operation Cancelled*"
                    await Bot.delete_message(vm)
                    dictm = await msgutils.send_embed(Bot, dictm, em)
                    return
                elif objutils.integer(v):
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
            dictm = await msgutils.send_embed(Bot, dictm, em)
        except AttributeError:
            em.description = "Could not find "+x+" in the dictionary."
            dictm = await msgutils.send_embed(Bot, dictm, em)
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
                if objutils.integer(v1[0]):
                    st+="\n**__"+v1[0]+"__**"
                    v1 = v1[1:]
                for n in v1:
                    if objutils.integer(n.strip("()")):
                        st+="\n\t\t***"+n+"***"
                    elif len(n)==1:
                        st+="\n\t**"+n+"**"
                    else:
                        st+=" *"+n+"*"

        em.description+= '\n'+st
    em.description+="\n\nDefinitions retrieved from [The Merriam-Webster Dictionary](https://www.merriam-webster.com/) using [Dictionary](https://github.com/UnsignedByte/Dictionary) by [UnsignedByte](https://github.com/UnsignedByte)."
    dictm = await msgutils.send_embed(Bot, dictm, em)


async def purge(Bot, msg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_messages or msg.author.id == "418827664304898048":
        num = int(strutils.parse_command(msg.content, 1)[1].split(' ')[0])+1
        if num < 2:
            await Bot.send_message("There is no reason to delete 0 messages!")
        deletechunks = []
        def check(message):
            return not msg.mentions or msg.mentions[0].id == message.author.id
        try:
            await Bot.purge_from(msg.channel, limit=num, check=check)
            m = await Bot.send_message(msg.channel, strutils.format_response("**{_mention}** has cleared the last **{_number}** messages!", _msg=msg, _number=num-1))
        except HTTPException:
            m = await Bot.send_message(msg.channel, strutils.format_response("You cannot bulk delete messages that are over 14 days old!!"))

        await asyncio.sleep(2)
        await Bot.delete_message(m)
    else:
        em = Embed(title="Insufficient Permissions", description=strutils.format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)

async def save(Bot, msg, overrideperms = False):
    if overrideperms or userutils.is_mod(msg.author):
        if not overrideperms:
            em = Embed(title="Saving Data...", description="Saving...", colour=0xd32323)
            msg = await msgutils.send_embed(Bot, msg, em)
            await asyncio.sleep(1)
        data = datautils.get_data()
        for k, v in data.items():
            with open('Data/%s.txt' % k, 'wb') as f:
                pickle.dump(v, f)
        if not overrideperms:
            em.description = "Complete!"
            msg = await msgutils.edit_embed(Bot, msg, embed=em)
            await asyncio.sleep(0.5)
            await Bot.delete_message(msg)
        return True
    else:
        em = Embed(title="Insufficient Permissions", description=strutils.format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await msgutils.send_embed(Bot, msg, em)
        return False

async def getData(Bot, msg, reg):
    if (await userutils.is_mod(Bot, msg.author)):
        msgutils.send_large_message(Bot, msg.channel, pformat(datautils.get_data()), prefix='```xml\n',suffix='```')

async def find(Bot, msg, reg):
    if (await userutils.is_mod(Bot, msg.author)):
        if reg.group('key') == '*':
            await Bot.send_message(msg.channel, '`' + str(list(bot_data.keys())) + '`')
            return
        await msgutils.send_large_message(Bot, msg.channel, pformat(bot_data[reg.group('key')]), prefix='```xml\n',suffix='```')
    else:
        await Bot.send_message(msg.channel, 'You are not mod!')

async def delete_data(Bot, msg, reg):
    if (await userutils.is_mod(Bot, msg.author)):
        keys = reg.group('path').split()
        if isinstance(datautils.nested_get(*keys[:-1]), dict):
            datautils.nested_pop(*keys)
        elif isinstance(datautils.nested_get(*keys[:-1]), list):
            datautils.nested_remove(keys[-1], *keys[:-1])

async def makeMod(Bot, msg, reg):
    if msg.author == (await userutils.get_owner(Bot)):
        if msg.mentions[0] not in datautils.nested_get('global_data', 'moderators', default=[]):
            datautils.nested_append(msg.mentions[0], 'global_data', 'moderators')
    else:
        await Bot.send_message(msg.channel, 'You are not owner!')
async def removeMod(Bot, msg, reg):
    if msg.author == (await userutils.get_owner(Bot)):
        datautils.nested_remove(msg.mentions[0], 'global_data', 'moderators')
    else:
        await Bot.send_message(msg.channel, 'You are not owner!')

add_message_handler(info, "hi")
add_message_handler(info, "info")
add_message_handler(save, "save")
add_message_handler(purge, "purge")
add_message_handler(purge, "clear")
add_message_handler(quote, "quote")
add_message_handler(dictionary, "define")
add_message_handler(dictionary, "dictionary")
add_message_handler(execute, "exec")
add_private_message_handler(execute, "exec")

add_regex_message_handler(getData, r'getdata\Z')
add_regex_message_handler(delete_data, r'(?:remove|delete)\s+(?P<path>.*)\Z')
add_regex_message_handler(find, r'sub\s+(?P<key>.*)\Z')
add_regex_message_handler(makeMod, r'make (?P<user><@!?(?P<userid>[0-9]+)>) mod\Z')
add_regex_message_handler(removeMod, r'del (?P<user><@!?(?P<userid>[0-9]+)>) mod\Z')
