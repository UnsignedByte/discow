import asyncio

"""COMMANDS HERE"""

@asyncio.coroutine
def test_message(Discow, msg):
    tmp = yield from Discow.send_message(msg.channel, "Hi **%s**! I'm Discow." % msg.author.name)

@asyncio.coroutine
def rps(Discow, msg):
    mine = "rock"
    try:
        tmp = yield from Discow.send_message(msg.channel, format_response("**{_mention}** chooses **%s**, while I choose **%s**." % (msg.content.split(" ")[1], mine)))
    except IndexError:
        tmp = yield from Discow.send_message(msg.channel, "Please provide an input.")


message_handlers = {
    # Format is (command, function)
    "test": test_message,
    "rps": rps
}

discow_prefix = "&"


whitespace = [' ', '\t', '\n']

def get_command(cont):
    trim = cont[len(discow_prefix):]

    for i, c in enumerate(trim):
        if c in whitespace:
            return trim[:i]
    return trim


@asyncio.coroutine
def on_message(Discow, msg):
    if msg.content[:len(discow_prefix)] != discow_prefix:
        return
    try:
        yield from message_handlers[get_command(msg.content[len(discow_prefix)-1:].split(" ")[0])](Discow, msg)
    except KeyError:
        tmp = yield from Discow.send_message(msg.channel, "Unknown command **%s**." % get_command(msg.content))
