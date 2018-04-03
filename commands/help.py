import asyncio
from discord import Embed
from discow.handlers import add_message_handler
from discow.utils import *
from collections import OrderedDict


print("Parsing Help Command")
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
                #helpvals[lastheader].append("**"+cmd[0].title()+"**: "+cmd[2]+" Usage: "+cmd[1]+". Name(s): "+cmd[3]+".")
            else:
                helpvals[lastheader].append('> '+l.replace('`', ''))

em = Embed(colour=0x9542f4)

first = True
for key, value in helpvals.items():
    if first:
        em.title = key
        em.description = '\n'.join(map(lambda x:x.lstrip(">").strip(), value))+"\n\n```markdown"
        first = False
    else:
        em.description+="\n\n# "+key+'\n\n'+'\n'.join(value)
em.description+='\n```'

print("Finished Parsing")

@asyncio.coroutine
def gethelp(Discow, msg):
    myinfo = yield from Discow.application_info()
    me = yield from Discow.get_user_info(myinfo.id)
    em.set_footer(text="Created by "+me.display_name+" on "+get_localized_time(msg.server)+".", icon_url=myinfo.icon_url)
    yield from Discow.send_message(msg.channel, embed=em)

add_message_handler(gethelp, "help")
