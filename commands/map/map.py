from commands.map.maputils import World
import asyncio
from discow.handlers import add_message_handler, world, special_emojis, map_messages
from commands.utilities import save

directions = {"\U000025C0":(3, 0), "\U000023EA":(3, 1), "\U000025B6":(1, 0), "\U000023E9":(1, 1), "\U00002B06":(0, 0), "\U000023EB":(0, 1), "\U00002B07":(2, 0), "\U000023EC":(2, 1)}

@asyncio.coroutine
def genmap(Discow, msg):
    if msg.author.id not in map_messages or not map_messages[msg.author.id]:
        map_messages[msg.author.id] = msg
        if msg.author.id not in world.players:
            world.addPlayer(id=msg.author.id)
        mapmsg = yield from Discow.send_message(msg.channel, '```'+world.reqPlayer(msg.author.id)+'```')
        blankmapmsg = yield from Discow.send_message(msg.channel, '\u200D')
        blankmapmsg1 = yield from Discow.send_message(msg.channel, '\u200D')
        mod_emotes = [a for a in Discow.get_server("433441820102361108").emojis if a.name == "empty"]
        yield from Discow.add_reaction(blankmapmsg1, "\U000025C0")
        yield from Discow.add_reaction(blankmapmsg1, "\U00002B07")
        yield from Discow.add_reaction(blankmapmsg1, "\U000025B6")
        yield from Discow.add_reaction(blankmapmsg, mod_emotes[0])
        yield from Discow.add_reaction(blankmapmsg, "\U00002B06")
        yield from Discow.add_reaction(blankmapmsg, mod_emotes[1])
        yield from Discow.add_reaction(blankmapmsg, mod_emotes[2])
        yield from Discow.add_reaction(blankmapmsg, "\U000023EB")
        yield from Discow.add_reaction(blankmapmsg, mod_emotes[3])
        yield from Discow.add_reaction(blankmapmsg1, "\U000023EA")
        yield from Discow.add_reaction(blankmapmsg1, "\U000023EC")
        yield from Discow.add_reaction(blankmapmsg1, "\U000023E9")
        yield from Discow.add_reaction(mapmsg, "👌")
        def check(reaction, user):
            try:
                e = str(reaction.emoji)
            except TypeError:
                return False
            return reaction.message.id in [mapmsg.id, blankmapmsg.id, blankmapmsg1.id] and user.id == msg.author.id and (e in directions or e == "👌")
        while True:
            reaction = yield from Discow.wait_for_reaction(user=msg.author, timeout=600, check=check)
            if not reaction:
                yield from Discow.delete_messages([blankmapmsg, blankmapmsg1])
                yield from Discow.remove_reaction(mapmsg, "👌", Discow.user)
                yield from save(None, None, overrideperms=True)
                return
            emoji = str(reaction.reaction.emoji)
            reactedmessage = reaction.reaction.message
            usr = str(reaction.user)
            if emoji == "👌":
                yield from Discow.delete_messages([blankmapmsg, blankmapmsg1])
                yield from Discow.remove_reaction(mapmsg, emoji, msg.author)
                yield from Discow.remove_reaction(mapmsg, emoji, Discow.user)
                yield from save(None, None, overrideperms=True)
                return
            movement = directions[emoji]
            world.move(msg.author.id, movement[0], movement[1]*world.getPlayerAttr(msg.author.id, "speed")+1)
            yield from Discow.remove_reaction(reactedmessage, emoji, msg.author)
            yield from Discow.edit_message(mapmsg, '```'+world.reqPlayer(msg.author.id)+'```')
    else:
        yield from Discow.send_message(msg.channel, "You already have a map running! Please close it first.")

add_message_handler(genmap, 'map')
