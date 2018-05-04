from random import randint
import os
import pickle
from discow.utils import *
from datetime import date
from shutil import copyfile
from commands.map.maputils import World

print("Begin Handler Initialization")

message_handlers = {}
private_message_handlers = {}
bot_message_handlers = {}
reaction_handlers = []
unreaction_handlers = []
special_emojis = {}
map_messages = {}

print("\tBegin Loading Files")
closing = False

print("\t\tLoading World Map")
if os.path.isfile('discow/client/data/world.txt'):
    with open('discow/client/data/world.txt', 'rb') as f:
        world = pickle.load(f)
else:
    world = World()
    with open('discow/client/data/world.txt', 'wb') as f:
        pickle.dump(world, f)
    copyfile("discow/client/data/world.txt", "discow/client/data/data_backup/world.txt")
print("\t\tWorld Map Loaded")

if not os.path.exists("discow/client/data/data_backup/"):
    os.makedirs("discow/client/data/data_backup/")

command_settings = {}
if os.path.isfile("discow/client/data/settings.txt"):
    with open("discow/client/data/settings.txt", "rb") as f:
        command_settings = pickle.load(f)
    copyfile("discow/client/data/settings.txt", "discow/client/data/data_backup/settings.txt")

user_data = {}
if os.path.isfile("discow/client/data/user_data.txt"):
    with open("discow/client/data/user_data.txt", "rb") as f:
        user_data = pickle.load(f)
    copyfile("discow/client/data/user_data.txt", "discow/client/data/data_backup/user_data.txt")

quiz_data = {}
if os.path.isfile("discow/client/data/quiz_data.txt"):
    with open("discow/client/data/quiz_data.txt", "rb") as f:
        quiz_data = pickle.load(f)
    copyfile("discow/client/data/quiz_data.txt", "discow/client/data/data_backup/quiz_data.txt")

global_data = {}
if os.path.isfile("discow/client/data/global_data.txt"):
    with open("discow/client/data/global_data.txt", "rb") as f:
        global_data = pickle.load(f)
    copyfile("discow/client/data/global_data.txt", "discow/client/data/data_backup/global_data.txt")

print("\tLoaded files")

persistent_variables = {}

def flip_shutdown():
    global closing
    closing = not closing
def get_data():
    return [command_settings, user_data, quiz_data, global_data, world]
def disable_command(cmd, channels):
    global command_settings
    if cmd in command_settings:
        command_settings[cmd].extend(channels)
    else:
        command_settings[cmd] = channels
def enable_command(cmd, channels):
    global command_settings
    if cmd in command_settings:
        command_settings[cmd] = list(x for x in command_settings[cmd] if x not in channels)
def is_command(cmd):
    return cmd in message_handlers
def allowed_command(cmd, channel):
    if cmd not in command_settings:
        return True
    else:
        return channel not in command_settings[cmd]
def add_message_handler(handler, keyword):
    message_handlers[keyword] = handler

def add_private_message_handler(handler, keyword):
    private_message_handlers[keyword] = handler

def add_bot_message_handler(handler, keyword):
    bot_message_handlers[keyword] = handler

def add_settings_handler(handler, keyword):
    command_settings[keyword] = handler

def add_reaction_handler(handler, name):
    name += "$reaction_handler"
    if name not in persistent_variables:
        reaction_handlers.append(handler)
        persistent_variables[name] = True

def add_unreaction_handler(handler, name):
    name += "$unreaction_handler"
    if name not in persistent_variables:
        unreaction_handlers.append(handler)
        persistent_variables[name] = True


print("Handler initialized")
print("Begin Command Initialization")
# Add modules here
from commands import *
import commands.map.map
import commands.gunn_schedule.schedule
import discord
print("Command Initialization Finished")
import re

import asyncio

EXTREMEBRITISHREGEX = {
re.compile(r'\b(?P<START>(?:(?:(?:[l1]\W*)+(?:[il!1]\W*)+|(?:m\W*)+(?:[e3]\W*)+|(?:c\W*)+(?:[e3]\W*)+(?:n\W*)+)(?:t\W*)+|(?:t\W*)+(?:h\W*)+(?:[e3]\W*)+(?:a\W*)+(?:t\W*)+|(?:m\W*)+(?:a\W*)+(?:n\W*)+(?:[e3]\W*)+(?:u\W*)+(?:v\W*)+))(?P<MID>(?:[e3]\W*)+)(?P<MID2>r+)(?P<END>(?:[e3]?s?\W*)+)\b', re.I) : r'\g<START>\g<MID2>\g<MID>\g<END>',
re.compile(r'\b(?P<START>(?:(?P<r>(?:c\W*)+(?:[o0]\W*)+(?:[l1]\W*)+|(?:[l1]\W*)+(?:a\W*)+(?:b\W*)+|(?:f\W*)+(?:[l1]\W*)+(?:a\W*)+(?:v\W*)+|(?:[o0]\W*)+(?:d\W*)+|(?:v\W*)+(?:a\W*)+(?:(?:p\W*)+|(?:[l1]\W*)+)|(?:p\W*)+(?:a\W*)+(?:r\W*)+(?:[l1]\W*)+|(?:t\W*)+(?:u\W*)+(?:m\W*)+|(?:a\W*)+(?:r\W*)+(?:m\W*)+)|(?P<rite>(?:f\W*)+(?:a\W*)+(?:v\W*)+)))(?P<MID>(?:[o0]\W*)+)(?P<END>(?(r)(?:r\W*)+|(?(rite)(?:r\W*)+(?:[il1!]\W*)+(?:t\W*)+(?:[e3]\W*)+)))\b', re.I) : r'\g<START>\g<MID>u\g<END>',
re.compile(r'\b(?P<START>(?:(?P<maneuvre>(?:m\W*)+(?:a\W*)+(?:n\W*)+)|(?P<ameba>(?:a\W*)+(?:m\W*)+)))(?P<MID>(?:[e3]\W*)+)(?P<END>\W*(?(maneuvre)(?:u\W*)+(?:v\W*)+(?:r\W*)+(?:[e3]\W*)+|(?(ameba)(?:b\W*)+(?:a\W*)+)))\b', re.I) : r'\g<START>o\g<MID>\g<END>',
re.compile(r'\b((?:(?:b\W*)+(?:[e3]\W*)?)?(?:c\W*)+(?:u\W*)+(?:\W*z)+)\b', re.I) : r'because',
}
def britsub(s):
    for k, v in EXTREMEBRITISHREGEX.items():
        s = k.sub(v, s)
    return s

async def on_message(Discow, msg):
    notbritish = britsub(msg.content)
    if notbritish != msg.content:
        await Discow.delete_message(msg)
        await Discow.send_message(msg.channel, "Hey "+msg.author.mention+"! You are using the wrong version of english. Here, I have fixed it for you:\n\n"+notbritish)
        return
    if not msg.author.bot:
        if msg.content[:len(discow_prefix)].lower() != discow_prefix:
            hatingRegex = re.compile(r'\b(\*|_|~)*hat(?P<ending>(e(d|rs*|s|ful(ness)?)?|ing|red))(\*|_|~)*\b', re.I)
            newHatingRe = hatingRegex.sub(r'**dislik\g<ending>**', msg.content)
            countbad=0
            async for a in Discow.logs_from(msg.channel, limit=5, before=msg):
                if a.author.id == msg.author.id and a.content == msg.content:
                        countbad+=1


            if countbad >= 3:
                await Discow.delete_message(msg)
                nospammsg = await Discow.send_message(msg.channel, "Hey "+msg.author.mention+"! Stop spamming the same message over and over again!")
                await asyncio.sleep(1)
                await Discow.delete_message(nospammsg)
                return
            if msg.content.startswith("echo:") and msg.content.strip() != 'echo:':
                await Discow.send_message(msg.channel, newHatingRe.split(':', 1)[1])
                return
            if newHatingRe != msg.content and (Discow.user in msg.mentions or any(x in list(re.sub(r'[^\w\s]','',n).lower() for n in msg.content.split()) for x in [Discow.user.name.lower(), nickname(Discow.user, msg.server).lower()])):
                randms = ["Did I just hear "+Discow.user.mention+" and **HATE** in the **SAME MESSAGE???**", "Woah there! You better have a 'don't' in front of the hate!", "Hey! I don't like being hated! \nIf you have a problem with me, report it on our issues page on github!", "Don't hate me, okay? Bots have feelings too", "Stop with the hate! I don't like it!", "I **slightly dislike** you as well, "+msg.author.mention+"!:rage:"]
                await Discow.send_message(msg.channel, randms[randint(0,len(randms)-1)])
                await Discow.add_reaction(msg, "👎")
                return
            if Discow.user in msg.mentions:
                randms = ["**BIG BROTHER** is **WATCHING YOU", "I was called?", "Hi to you too, "+msg.author.mention, "Please don't disturb me, I'm busy being worked on.", "What do you want?", "Hey! Bots don't like being pinged either!", "Stop mentioning me! :rage:", "...", "If you need help, just do `"+discow_prefix+"help` and stop pinging me!", "Stop distracting me, do `"+discow_prefix+"help` if you want help.", "Silence!!!", "Leave me alone!", "Yes, I AM "+Discow.user.mention+'.', "Do you have a death wish?"]
                await Discow.send_message(msg.channel, randms[randint(0,len(randms)-1)])
            elif allowed_command("easteregg", msg.channel):
                if newHatingRe != msg.content:
                    await Discow.send_message(msg.channel, 'Woah '+msg.author.mention+'! Hating is rude! Don\'t be so negative, try this:\n"'+newHatingRe.lower()+'"')
                    await Discow.add_reaction(msg, "👎")
                if randint(1, 100) == 1:
                    e = list(Discow.get_all_emojis())
                    try:
                        await Discow.add_reaction(msg, e[randint(0, len(e)-1)])
                    except (discord.NotFound, ValueError):
                        pass
                if randint(1, 150) == 1:
                    await fun.easteregg(Discow, msg)
            return
        if closing:
            em = discord.Embed(title="Bot Shutting Down", description="Not accepting commands, bot is saving data.", colour=0xd32323)
            await send_embed(Discow, msg, em)
            return
        try:
            cmd = parse_command(msg.content)[0].lower()
            if msg.channel.is_private:
                try:
                    await private_message_handlers[cmd](Discow, msg)
                except KeyError:
                    if cmd in message_handlers:
                        await Discow.send_message(msg.channel, "The **"+cmd+"** command cannot be used in private channels!")
                return
            if cmd in command_settings and msg.channel in command_settings[cmd]:
                em = discord.Embed(title="Command Disabled", colour=0xd32323)
                em.description = "I'm sorry, but the command "+cmd+" cannot be used in "+msg.channel.mention+"."
                await send_embed(Discow, msg, em)
            else:
                try:
                    await message_handlers[cmd](Discow, msg)
                except KeyError:
                    if cmd in private_message_handlers:
                        await Discow.send_message(msg.channel, "The **"+cmd+"** command can only be used in private channels!")
                if cmd != 'save' and randint(1,50)==1:
                    await message_handlers["save"](Discow, msg, overrideperms=True)
        except IndexError:
            em = discord.Embed(title="Missing Inputs", description="Not enough inputs provided for **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            await send_embed(Discow, msg, em)
        except (TypeError, ValueError):
            em = discord.Embed(title="Invalid Inputs", description="Invalid inputs provided for **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            await send_embed(Discow, msg, em)
        except discord.Forbidden:
            em = discord.Embed(title="Missing Permissions", description="Discow is missing permissions to perform this task.", colour=0xd32323)
            try:
                await send_embed(Discow, msg, em)
            except discord.Forbidden:
                pass
        except Exception as e:
            em = discord.Embed(title="Unknown Error", description="An unknown error occurred in command **%s**. Trace:\n%s" % (parse_command(msg.content)[0], e), colour=0xd32323)
            await send_embed(Discow, msg, em)
    else:
        if msg.author != Discow.user and msg.channel.id == "433441820102361110" and msg.embeds and 'title' in msg.embeds[0] and msg.embeds[0]["title"] in bot_message_handlers:
            try:
                await bot_message_handlers[msg.embeds[0]["title"]](Discow, msg)
            except Exception:
                pass

async def on_reaction(Discow, reaction, user):
    for handler in reaction_handlers:
        await handler(Discow, reaction, user)

async def on_unreaction(Discow, reaction, user):
    for handler in reaction_handlers:
        await handler(Discow, reaction, user)

async def timed_msg(Discow):
    while True:
        if 'interest' not in global_data or global_data['interest'] < date.today():
            global_data['interest'] = date.today()
            await economy.interest()
        await asyncio.sleep(3600)
