# @Author: Edmund Lam <edl>
# @Date:   06:50:24, 02-May-2018
# @Filename: handlers.py
# @Last modified by:   edl
# @Last modified time: 16:22:26, 20-Aug-2018


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
import discord
print("Command Initialization Finished")
import re

import asyncio

async def on_message(Discow, msg):
    if not msg.author.bot:
        if msg.content[:len(discow_prefix)].lower() != discow_prefix:
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
                await Discow.send_message(msg.channel, msg.content.split(':', 1)[1])
                return
            if Discow.user in msg.mentions:
                await Discow.send_message(msg.channel, "Type `cow help` if you need help.")
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
