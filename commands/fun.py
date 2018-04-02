import asyncio
from discow.utils import *
from discow.handlers import add_message_handler
from random import randint, shuffle

@asyncio.coroutine
def hi(Discow, msg):
    yield from Discow.send_message(msg.channel, format_response("Hi **{_name}**, I'm Discow! Tag me! {mymention}", _msg = msg, mymention=Discow.user.mention))

@asyncio.coroutine
def invite(Discow, msg):
    inv = yield from Discow.create_invite(msg.channel, max_age=60, max_uses=0, unique=False)
    outstr = "You have been invited to "+msg.server.name+"!\nJoin with this link:\n"+inv.url
    yield from Discow.send_message(msg.channel, outstr)

@asyncio.coroutine
def rps(Discow, msg):
    valid = ["rock", "paper", "scissors"]
    mine = valid[randint(0, 2)]
    yours = parse_command(msg.content, 1)[1]
    result = ""
    if mine == yours:
        result = "It's a tie!"
    else:
        comb = mine+yours
        if comb == "rockpaper" or "scissorsrock" or "paperscissors":
            result = format_response("{_mention} wins!", _msg=msg)
        else:
            result = "I win!"
    if yours in valid:
        yield from Discow.send_message(msg.channel, format_response("**{_mention}** chooses **{yours}**, while I choose **{mine}**. {result}", yours=yours, mine=mine, _msg = msg, result=result))
    else:
        yield from Discow.send_message(msg.channel, "Your input was invalid. Please choose **rock**, **paper**, or **scissors.**")

@asyncio.coroutine
def reaction(Discow, msg):
    num = int(parse_command(msg.content, 1)[1])
    e = msg.server.emojis
    shuffle(e)
    yield from Discow.delete_message(msg)
    m = yield from Discow.logs_from(msg.channel, limit=1)
    m = list(m)[0]
    for i in range(0, min(len(e), num, 20-len(m.reactions))):
        yield from Discow.add_reaction(m, e[i])

@asyncio.coroutine
def easteregg(Discow, msg):
    msgs = [
        "Nice!",
        "I agree",
        format_response("{_mention} is right, obviously", _msg=msg),
        "Hello!",
        "Eggs are superior",
        "I think it's almost Easter!",
        "Google \"do a barrel roll\"",
        "I'm sorry, what are we talking about again?"
    ]
    yield from Discow.send_message(msg.channel, msgs[randint(0,len(msgs)-1)])

add_message_handler(hi, "hi")
add_message_handler(rps, "rps")
add_message_handler(reaction, "reaction")
add_message_handler(easteregg, "easteregg")
add_message_handler(invite, "invite")
