# @Author: Edmund Lam <edl>
# @Date:   06:50:24, 02-May-2018
# @Filename: handlers.py
# @Last modified by:   edl
# @Last modified time: 19:38:09, 02-Nov-2018

import pickle
from random import randint
from discow.utils import *
from datetime import date
from commands.map.maputils import World

print("Begin Handler Initialization")

message_handlers = {}
private_message_handlers = {}
bot_message_handlers = {}
special_emojis = {}
map_messages = {}

print("\tBegin Loading Files")
closing = False

if not os.path.exists("Data/Backup/"):
    os.makedirs("Data/Backup/")

world = load_data_file('world.txt')
if not world:
    world = World()
    with open("Data/world.txt", "wb") as f:
        pickle.dump(world, f)

command_settings = load_data_file('settings.txt')
user_data = load_data_file('user_data.txt')
quiz_data = load_data_file('quiz_data.txt')
global_data = load_data_file('global_data.txt')

print("\tLoaded files")


def nested_set(value, *keys):
    dic = server_data
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def nested_pop(*keys):
    nested_get(*keys[:-1]).pop(keys[-1], None)


def alt_pop(key, *keys):
    nested_get(*keys).pop(key)


def nested_get(*keys):
    dic = server_data
    for key in keys:
        dic=dic.setdefault( key, {} )
    return dic


def nested_append(value, *keys):
    v = nested_get(*keys)
    if v:
        v.append(value)
    else:
        nested_set([value], *keys)


def nested_remove(value, *keys, **kwargs):
    kwargs['func'] = kwargs.get('func', None)
    v = nested_get(*keys)
    if not v or isinstance(v, discord.Member):
        return
    try:
        if not kwargs['func']:
            v.remove(value)
        else:
            for x in v:
                if kwargs['func'](x, value):
                    v.remove(x)
                    break
    except ValueError:
        return


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
        if msg.content[:len(discow_prefix)].lower() != discow_prefix:
            if msg.content.startswith("echo:") and msg.content.strip() != 'echo:':
                await Bot.send_message(msg.channel, msg.content.split(':', 1)[1])
                return
            if Bot.user in msg.mentions:
                await Bot.send_message(msg.channel, "Type `cow help` if you need help.")
            return
        if closing:
            em = discord.Embed(title="Bot Shutting Down", description="Not accepting commands, bot is saving data.", colour=0xd32323)
            await send_embed(Bot, msg, em)
            return
        try:
            cmd = parse_command(msg.content)[0].lower()
            if msg.channel.is_private:
                try:
                    await private_message_handlers[cmd](Bot, msg)
                except KeyError:
                    if cmd in message_handlers:
                        await Bot.send_message(msg.channel, "The **"+cmd+"** command cannot be used in private channels!")
                return
            if cmd in command_settings and msg.channel in command_settings[cmd]:
                em = discord.Embed(title="Command Disabled", colour=0xd32323)
                em.description = "I'm sorry, but the command "+cmd+" cannot be used in "+msg.channel.mention+"."
                await send_embed(Bot, msg, em)
            else:
                try:
                    await message_handlers[cmd](Bot, msg)
                except KeyError:
                    if cmd in private_message_handlers:
                        await Bot.send_message(msg.channel, "The **"+cmd+"** command can only be used in private channels!")
                if cmd != 'save' and randint(1,50)==1:
                    await message_handlers["save"](Bot, msg, overrideperms=True)
        except IndexError:
            em = discord.Embed(title="Missing Inputs", description="Not enough inputs provided for **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            await send_embed(Bot, msg, em)
        except (TypeError, ValueError):
            em = discord.Embed(title="Invalid Inputs", description="Invalid inputs provided for **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            await send_embed(Bot, msg, em)
        except discord.Forbidden:
            em = discord.Embed(title="Missing Permissions", description="Discow is missing permissions to perform this task.", colour=0xd32323)
            try:
                await send_embed(Bot, msg, em)
            except discord.Forbidden:
                pass
        except Exception as e:
            em = discord.Embed(title="Unknown Error", description="An unknown error occurred in command **%s**. Trace:\n%s" % (parse_command(msg.content)[0], e), colour=0xd32323)
            await send_embed(Bot, msg, em)
    else:
        if msg.author != Bot.user and msg.channel.id == "433441820102361110" and msg.embeds and 'title' in msg.embeds[0] and msg.embeds[0]["title"] in bot_message_handlers:
            try:
                await bot_message_handlers[msg.embeds[0]["title"]](Bot, msg)
            except Exception:
                pass

async def timed_msg(Bot):
    while True:
        if 'interest' not in global_data or global_data['interest'] < date.today():
            global_data['interest'] = date.today()
            await economy.interest()
        await asyncio.sleep(3600)
