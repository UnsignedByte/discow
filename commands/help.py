import asyncio
from discord import Embed
from discow.handlers import add_message_handler
from discow.utils import *
from collections import OrderedDict

print("\tInitializing Help Command")
print("\t\tParsing Help Command")
helpvals = OrderedDict()

with open("README.md", "r") as f:
    lastheader = ""
    lines = f.readlines()
    for l in lines:
        l = l.strip()
        if l:
            if l.startswith("#"):
                lastheader = l.lstrip("#").strip()
                helpvals.update({lastheader : []})
            elif l in ["| **Name** | **Usage** | **Description** | **Aliases** |", "|:-:|:-:|:-:|:-:|"]:
                pass
            elif l.startswith("|") and l.endswith("|"):
                cmd = list(map(lambda x:x.replace('`', ""), l.strip("|").split("|")))
                helpvals[lastheader].append("< "+cmd[1]+" >\n[ AKA "+cmd[3].ljust(15)+" ]( "+cmd[2]+" )")
            else:
                helpvals[lastheader].append('> '+l.replace('`', ''))

helpembed = Embed(colour=0x9542f4)

desc = "```markdown"

first = True
for key, value in helpvals.items():
    if first:
        helpembed.title = key
        helpembed.description = '\n'.join(map(lambda x:x.lstrip(">").strip(), value))
        first = False
    else:
        stoadd = "\n\n# "+key+'\n\n'+'\n'.join(value)
        if len(desc)+len(stoadd) >= 1000:
            helpembed.add_field(name="\a", value=desc+'```')
            desc = "```markdown"+stoadd
        else:
            desc+=stoadd
helpembed.add_field(name="\a", value=desc+'```')
print("\t\tFinished Parsing")

@asyncio.coroutine
def gethelp(Discow, msg):
    yield from send_embed(Discow, msg, helpembed)

add_message_handler(gethelp, "help")
print("\tHelp Command Initialized")
