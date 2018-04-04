from random import randint
import os
import pickle

message_handlers = {}
reaction_handlers = []
unreaction_handlers = []

closing = False
command_settings = {}
if os.path.isfile("discow/client/data/settings.txt"):
    with open("discow/client/data/settings.txt", "rb") as f:
        command_settings = pickle.load(f)
user_data = {}
if os.path.isfile("discow/client/data/user_data.txt"):
    with open("discow/client/data/user_data.txt", "rb") as f:
        user_data = pickle.load(f)


persistent_variables = {}

def flip_shutdown():
    global closing
    closing = not closing
def get_data():
    return [command_settings, user_data]
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



# Add modules here
from commands import *
import commands.gunn_schedule.schedule
from discow.utils import *
import discord

import asyncio

whitespace = [' ', '\t', '\n']

@asyncio.coroutine
def on_message(Discow, msg):
    if not msg.author.bot:
        if msg.content[:len(discow_prefix)].lower() != discow_prefix:
            if Discow.user in msg.mentions:
                randms = ["I was called?", "Hi to you too, "+msg.author.mention, "Please don't disturb me, I'm busy being worked on.", "What do you want?", msg.author.mention+" to you too!", "Stop mentioning me! :rage:", "..."]
                yield from Discow.send_message(msg.channel, randms[randint(0,len(randms)-1)])
            if allowed_command("easteregg", msg.channel):
                if randint(1, 50) == 1:
                    e = msg.server.emojis
                    yield from Discow.add_reaction(msg, e[randint(0, len(e)-1)])
                if randint(1, 100) == 1:
                    yield from fun.easteregg(Discow, msg)
            return
        if closing:
            em = discord.Embed(title="Bot Shutting Down", description="Not accepting commands, bot is saving data.", colour=0xd32323)
            yield from Discow.send_message(msg.channel, embed=em)
            return
        try:
            cmd = parse_command(msg.content)[0]
            if cmd in command_settings and msg.channel in command_settings[cmd]:
                em = discord.Embed(title="Command Disabled", colour=0xd32323)
                em.description = "I'm sorry, but the command "+cmd+" cannot be used in "+msg.channel.mention+"."
                yield from Discow.send_message(msg.channel, embed=em)
            else:
                yield from message_handlers[cmd](Discow, msg)
        except IndexError:
            em = discord.Embed(title="Missing Inputs", description="Not enough inputs provided for **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            yield from Discow.send_message(msg.channel, embed=em)
        except KeyError:
            em = discord.Embed(title="Unknown Command", description="Unknown command **%s**." % parse_command(msg.content)[0], colour=0xd32323)
            yield from Discow.send_message(msg.channel, embed=em)
        except discord.Forbidden:
            em = discord.Embed(title="Missing Permissions", description="Discow is missing permissions to perform this task.", colour=0xd32323)
            yield from Discow.send_message(msg.channel, embed=em)
        except Exception as e:
            em = discord.Embed(title="Unknown Error", description="An unknown error occurred in command **%s**. Trace:\n%s" % (parse_command(msg.content)[0], e), colour=0xd32323)
            yield from Discow.send_message(msg.channel, embed=em)

@asyncio.coroutine
def on_reaction(Discow, reaction, user):
    for handler in reaction_handlers:
        yield from handler(Discow, reaction, user)

@asyncio.coroutine
def on_unreaction(Discow, reaction, user):
    for handler in reaction_handlers:
        yield from handler(Discow, reaction, user)
