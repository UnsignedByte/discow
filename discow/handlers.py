message_handlers = {}

# Add modules here
import discow.test_functions
import discow.gunn_schedule.schedule

import asyncio
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
        yield from message_handlers[get_command(msg.content)](Discow, msg)
    except KeyError:
        yield from Discow.send_message(msg.channel, "Unknown command **%s**." % get_command(msg.content))
    except Exception as e:
        yield from Discow.send_message(msg.channel, "An unknown error occurred in command **%s**. Trace:\n%s" % (get_command(msg.content), e))
