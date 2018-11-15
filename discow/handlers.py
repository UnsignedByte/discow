# @Author: Edmund Lam <edl>
# @Date:   06:50:24, 02-May-2018
# @Filename: handlers.py
# @Last modified by:   edl
# @Last modified time: 23:09:37, 14-Nov-2018

bot_data = {}
discow_prefix = "cow "

import re
import os
import pickle
from random import randint
from shutil import copyfile
from utils import strutils, msgutils, datautils
from datetime import date
from commands.map.maputils import World

print("Begin Handler Initialization")

message_handlers = {}
private_message_handlers = {}
regex_message_handlers = {}
bot_message_handlers = {}
map_messages = {}
special_emojis = {}

print("\tBegin Loading Files")
closing = False

if not os.path.exists("Data/Backup/"):
    os.makedirs("Data/Backup/")

world = datautils.load_data_file('world.txt')
if not world:
    world = World()
    with open("Data/world.txt", "wb") as f:
        pickle.dump(world, f)

bot_data['world'] = world
bot_data['settings'] = datautils.load_data_file('settings.txt')
bot_data['user_data'] = datautils.load_data_file('user_data.txt')
bot_data['quiz_data'] = datautils.load_data_file('quiz_data.txt')
bot_data['global_data'] = datautils.load_data_file('global_data')

print("\tLoaded files")


def flip_shutdown():
    global closing
    closing = not closing

def disable_command(cmd, channels):
    global bot_data
    if cmd in bot_data['settings']:
        bot_data['settings'][cmd].extend(channels)
    else:
        bot_data['settings'][cmd] = channels
def enable_command(cmd, channels):
    global bot_data
    if cmd in bot_data['settings']:
        bot_data['settings'][cmd] = list(x for x in bot_data['settings'][cmd] if x not in channels)
def is_command(cmd):
    return cmd in message_handlers
def allowed_command(cmd, channel):
    if cmd not in bot_data['settings']:
        return True
    else:
        return channel not in bot_data['settings'][cmd]
def add_message_handler(handler, keyword):
    message_handlers[keyword] = handler

def add_private_message_handler(handler, keyword):
    private_message_handlers[keyword] = handler

def add_regex_message_handler(handler, keyword):
    regex_message_handlers[keyword] = handler

def add_bot_message_handler(handler, keyword):
    bot_message_handlers[keyword] = handler

def add_settings_handler(handler, keyword):
    bot_data['settings'][keyword] = handler

print("Handler initialized")
print("Begin Command Initialization")
# Add modules here
from commands import *
import commands.map.map
import discord
print("Command Initialization Finished")
import re

import asyncio

async def on_message(Bot, msg):
    if not msg.author.bot:
        if msg.role_mentions or msg.mention_everyone:
            for m in msg.server.members:
                if not m.bot and m.mentioned_in(msg) and (not datautils.nested_get('user_data', m.id, 'mentions')
                                                          or msg not in datautils.nested_get('user_data', m.id, 'mentions')):
                    datautils.nested_append(msg, 'user_data', m.id, 'mentions')
                    bot_data['user_data'][m.id]['mentions'] = bot_data['user_data'][m.id]['mentions'][-10:]
        else:
            for m in msg.mentions:
                if not m.bot and (not datautils.nested_get('user_data', m.id, 'mentions')
                                  or msg not in datautils.nested_get('user_data', m.id, 'mentions')):
                    datautils.nested_append(msg, 'user_data', m.id, 'mentions')
                    bot_data['user_data'][m.id]['mentions'] = bot_data['user_data'][m.id]['mentions'][-10:]
        if not msg.content.startswith(discow_prefix):
            for a in regex_message_handlers:
                reg = re.compile(a, re.I).match(msg.content)
                if reg:
                    await regex_message_handlers[a](Bot, msg, reg)
                    break
            if Bot.user in msg.mentions:
                await Bot.send_message(msg.channel, "Type `cow help` if you need help.")
            return
        if closing:
            em = discord.Embed(title="Bot Shutting Down", description="Not accepting commands, bot is saving data.", colour=0xd32323)
            await msgutils.send_embed(Bot, msg, em)
            return
        try:
            cmd = strutils.parse_command(msg.content)[0].lower()
            if msg.channel.is_private:
                try:
                    await private_message_handlers[cmd](Bot, msg)
                except KeyError:
                    if cmd in message_handlers:
                        await Bot.send_message(msg.channel, "The **"+cmd+"** command cannot be used in private channels!")
                return
            if msg.channel in datautils.nested_get('settings', cmd, default=[]):
                em = discord.Embed(title="Command Disabled", colour=0xd32323)
                em.description = "I'm sorry, but the command "+cmd+" cannot be used in "+msg.channel.mention+"."
                await msgutils.send_embed(Bot, msg, em)
            else:
                try:
                    await message_handlers[cmd](Bot, msg)
                except KeyError:
                    if cmd in private_message_handlers:
                        await Bot.send_message(msg.channel, "The **"+cmd+"** command can only be used in private channels!")
        except IndexError:
            em = discord.Embed(title="Missing Inputs", description="Not enough inputs provided for **%s**." % strutils.parse_command(msg.content)[0], colour=0xd32323)
            await msgutils.send_embed(Bot, msg, em)
        except (TypeError, ValueError):
            em = discord.Embed(title="Invalid Inputs", description="Invalid inputs provided for **%s**." % strutils.parse_command(msg.content)[0], colour=0xd32323)
            await msgutils.send_embed(Bot, msg, em)
        except discord.Forbidden:
            em = discord.Embed(title="Missing Permissions", description="Discow is missing permissions to perform this task.", colour=0xd32323)
            try:
                await msgutils.send_embed(Bot, msg, em)
            except discord.Forbidden:
                pass
        except Exception as e:
            em = discord.Embed(title="Unknown Error", description="An unknown error occurred in command **%s**. Trace:\n%s" % (strutils.parse_command(msg.content)[0], e), colour=0xd32323)
            await msgutils.send_embed(Bot, msg, em)
    else:
        if msg.author != Bot.user and msg.channel.id == "433441820102361110" and msg.embeds and 'title' in msg.embeds[0] and msg.embeds[0]["title"] in bot_message_handlers:
            try:
                await bot_message_handlers[msg.embeds[0]["title"]](Bot, msg)
            except Exception:
                pass

async def timed_msg(Bot):
    while True:
        if datautils.nested_get('global_data', 'interest', default=date.min) < date.today():
            datautils.nested_set(date.today(), 'global_data', 'interest')
            await economy.interest()
        await asyncio.sleep(3600)
async def timed_save(Bot):
    while True:
        await asyncio.sleep(60)
        await message_handlers["save"](Bot, None, overrideperms=True)
        try:
            for i in bot_data.keys():
                copyfile('Data/'+i+".txt", 'Data/Backup/'+i+".txt")
        except Exception as e:
            print(e)
