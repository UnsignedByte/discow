# @Author: Edmund Lam <edl>
# @Date:   13:44:12, 21-Apr-2018
# @Filename: map.py
# @Last modified by:   edl
# @Last modified time: 15:56:43, 12-Aug-2018


from commands.map.maputils import World
import asyncio
from discow.handlers import add_message_handler, world, special_emojis, map_messages, add_private_message_handler
from commands.utilities import save

directions = {"\U000025C0":(3, 0), "\U000023EA":(3, 1), "\U000025B6":(1, 0), "\U000023E9":(1, 1), "\U00002B06":(0, 0), "\U000023EB":(0, 1), "\U00002B07":(2, 0), "\U000023EC":(2, 1)}

async def genmap(Discow, msg):
    if msg.author.id not in map_messages or not map_messages[msg.author.id]:
        map_messages[msg.author.id] = msg
        if msg.author.id not in world.players:
            world.addPlayer(id=msg.author.id)
        mapmsg = await Discow.send_message(msg.channel, '```'+world.reqPlayer(msg.author.id)+'```')
        blankmapmsg = await Discow.send_message(msg.channel, '\u200D')
        blankmapmsg1 = await Discow.send_message(msg.channel, '\u200D')
        await Discow.add_reaction(mapmsg, special_emojis["empty"][0])
        await Discow.add_reaction(mapmsg, "\U00002B06")
        await Discow.add_reaction(mapmsg, special_emojis["empty"][1])
        await Discow.add_reaction(mapmsg, special_emojis["empty"][2])
        await Discow.add_reaction(mapmsg, "\U000023EB")
        await Discow.add_reaction(mapmsg, special_emojis["empty"][3])
        await Discow.add_reaction(blankmapmsg, "\U000025C0")
        await Discow.add_reaction(blankmapmsg, "\U00002B07")
        await Discow.add_reaction(blankmapmsg, "\U000025B6")
        await Discow.add_reaction(blankmapmsg, "\U000023EA")
        await Discow.add_reaction(blankmapmsg, "\U000023EC")
        await Discow.add_reaction(blankmapmsg, "\U000023E9")
        await Discow.add_reaction(blankmapmsg1, "👌")
        await Discow.add_reaction(blankmapmsg1, special_emojis["pack"][0])
        def check(reaction, user):
            e = str(reaction.emoji)
            return reaction.message.id in [mapmsg.id, blankmapmsg.id, blankmapmsg1.id] and user.id == msg.author.id and (e in directions or e == "👌" or e == str(special_emojis['pack'][0]))

        while True:
            reaction = await Discow.wait_for_reaction(user=msg.author, timeout=600, check=check)
            if not reaction:
                await Discow.delete_messages([blankmapmsg, blankmapmsg1])
                await Discow.remove_reaction(mapmsg, "👌", Discow.user)
                await Discow.remove_reaction(mapmsg, special_emojis["pack"][0], Discow.user)
                del map_messages[msg.author.id]
                await save(None, None, overrideperms=True)
                return
            emoji = str(reaction.reaction.emoji)
            reactedmessage = reaction.reaction.message
            usr = str(reaction.user)
            if emoji == "👌":
                if invlook:
                    await Discow.edit_message(blankmapmsg1, '\u200D')
                    await Discow.clear_reactions(blankmapmsg1)
                    await Discow.add_reaction(blankmapmsg1, "👌")
                    await Discow.add_reaction(blankmapmsg1, special_emojis["pack"][0])
                else:
                    await Discow.delete_messages([blankmapmsg, blankmapmsg1])
                    await Discow.remove_reaction(mapmsg, emoji, msg.author)
                    await Discow.remove_reaction(mapmsg, emoji, Discow.user)
                    await Discow.remove_reaction(mapmsg, special_emojis["pack"][0], Discow.user)
                    del map_messages[msg.author.id]
                await save(None, None, overrideperms=True)
                return
            if emoji == str(special_emojis["pack"][0]):
                await Discow.edit_message(blankmapmsg1, world.reqPlayerInv(msg.author.id))
            else:
                movement = directions[emoji]
                world.move(msg.author.id, movement[0], movement[1]*world.getPlayerAttr(msg.author.id, "speed")+1)
                await Discow.edit_message(mapmsg, '```'+world.reqPlayer(msg.author.id)+'```')
            await Discow.remove_reaction(reactedmessage, reaction.reaction.emoji, msg.author)
    else:
        await Discow.send_message(msg.channel, "You already have a map running! Please close it first.")

add_message_handler(genmap, 'map')
add_private_message_handler(genmap, 'map')
