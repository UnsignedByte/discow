from commands.map.maputils import World
import asyncio
from discow.handlers import add_message_handler, world

directions = {"\U000025C0":(1, 0), "\U000023EA":(3, 1), "\U000025B6":(1, 0), "\U000023E9":(1, 1), "\U00002B06":(0, 0), "\U000023EB":(0, 1), "\U00002B07":(2, 0), "\U000023EC":(2, 1)}

@asyncio.coroutine
def genmap(Discow, msg):
    if msg.author.id not in world.players:
        world.addPlayer(id=msg.author.id)
    mapmsg = yield from Discow.send_message(msg.channel, '```'+world.reqPlayer(msg.author.id)+'```')
    for a in directions:
        yield from Discow.add_reaction(mapmsg, a)
    yield from Discow.add_reaction(mapmsg, "\U000023EA")
    yield from Discow.add_reaction(mapmsg, "\U000025C0")
    yield from Discow.add_reaction(mapmsg, "\U00002B06")
    yield from Discow.add_reaction(mapmsg, "\U000023EB")
    yield from Discow.add_reaction(mapmsg, "\U00002B07")
    yield from Discow.add_reaction(mapmsg, "\U000023EC")
    yield from Discow.add_reaction(mapmsg, "\U000025B6")
    yield from Discow.add_reaction(mapmsg, "\U000023E9")
    yield from Discow.add_reaction(mapmsg, "👌")
    def check(reaction, user):
        e = str(reaction.emoji)
        print(e)
        return e in directions or e == "👌"
    while True:
        reaction = yield from Discow.wait_for_reaction(user=msg.author, timeout=600, check=check)
        if not reaction or reaction[0] == "👌":
            yield from Discow.delete_message(mapmsg)
            return

add_message_handler(genmap, 'map')
