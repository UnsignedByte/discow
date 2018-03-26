import asyncio
from discow.handlers import reaction_handlers,unreaction_handlers

killer_emoji = "\U00002620"

@asyncio.coroutine
def add_message_killer(Discow, msg):
    yield from Discow.add_reaction(msg, killer_emoji)

@asyncio.coroutine
def destroy_message_on_reaction(Discow, reaction, user):
    if user == Discow.user or reaction.message.author != Discow.user:
        return

    if reaction.emoji == killer_emoji:
        yield from Discow.delete_message(reaction.message)

reaction_handlers.append(destroy_message_on_reaction)