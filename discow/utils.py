# @Author: Edmund Lam <edl>
# @Date:   15:30:36, 12-Aug-2018
# @Filename: utils.py
# @Last modified by:   edl
# @Last modified time: 19:32:57, 02-Nov-2018


discow_prefix = "cow "

import os
import pickle
from shutil import copyfile
from discord import ServerRegion, Forbidden
import datetime
from pytz import timezone
import pytz
import itertools
import asyncio
from random import shuffle
from collections import OrderedDict
from PIL import Image, ImageDraw

def format_response(string, **kwargs):
    if "_msg" in kwargs:
        message = kwargs["_msg"]
        kwargs["_msgcontent"] = message.content
        kwargs["_author"] = message.author
    if "_author" in kwargs:
        author = kwargs["_author"]
        kwargs["_name"] = author.display_name
        kwargs["_username"] = author.name
        kwargs["_mention"] = author.mention

    return string.format(**kwargs)

def parse_command(msg, num=-1):
    cont = msg[len(discow_prefix):].split(" ")
    if num is not -1:
        if len(cont)<num+1:
            raise IndexError("Not enough inputs")
        else:
            return cont[:num]+[' '.join(cont[num:])]
    else:
        return cont

def strip_command(msg):
    return parse_command(msg, 1)[1]

def convertTime(time, msg):
    if msg.channel.is_private:
        zone = timezone("Europe/London")
    else:
        timezones = {
        ServerRegion.us_west:"America/Los_Angeles",
        ServerRegion.us_east:"America/New_York",
        ServerRegion.us_central:"US/Central",
        ServerRegion.eu_west:"Europe/Amsterdam",
        ServerRegion.eu_central:"Europe/Berlin",
        ServerRegion.singapore:"Singapore",
        ServerRegion.london:"Europe/London",
        ServerRegion.sydney:"Australia/Sydney",
        ServerRegion.amsterdam:"Europe/Amsterdam",
        ServerRegion.frankfurt:"Europe/Berlin",
        ServerRegion.brazil:"Brazil/Acre",
        ServerRegion.vip_us_east:"America/New_York",
        ServerRegion.vip_us_west:"America/Los_Angeles",
        ServerRegion.vip_amsterdam:"Europe/Amsterdam",
        'russia':'Europe/Russia'
        }
        zone = timezone(timezones[msg.server.region])
    time_naive = time.replace(tzinfo=pytz.utc)
    loctime = time_naive.astimezone(zone)
    fmt = '%Y-%m-%d at %H:%M:%S %Z'
    return loctime.strftime(fmt)

def nickname(usr, srv):
    if not srv:
        return usr.name
    n = srv.get_member(usr.id).nick
    if not n:
        return usr.name
    return n

async def send_embed(Discow, msg, embed, time=datetime.datetime.utcnow(), usr=None):
    if not usr:
        usr = Discow.user
    txt = "Created by "+nickname(usr, msg.server)+" on "+convertTime(time, msg)+"."
    embed.set_footer(text=txt, icon_url=(usr.avatar_url if usr.avatar_url else usr.default_avatar_url))
    try:
        m = await Discow.send_message(msg.channel, embed=embed)
        return m
    except Forbidden:
        await Discow.send_message(msg.channel,
                                       "**Missing Permissions**\nDiscow is missing permissions to send embeds.")
        return None


async def edit_embed(Discow, msg, embed, time=datetime.datetime.utcnow(), usr=None):
    if not usr:
        usr = Discow.user
    txt = "Edited by "+nickname(usr, msg.server)+" on "+convertTime(time, msg)+"."
    embed.set_footer(text=txt, icon_url=(usr.avatar_url if usr.avatar_url else usr.default_avatar_url))
    m = await Discow.edit_message(msg, embed=embed)
    return m

def group(lst, n):
  return list(zip(*[itertools.islice(lst, i, None, n) for i in range(n)]))

def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def chunkify(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

class Question:
    def __init__(self, q, o, s):
        self.question = q
        self.options = o
        self.shuffle = s
    def isCorrect(self, option):
        return list(self.options.values())[option-1]
    def optshuf(self):
        if self.shuffle:
            keeeeys = list(self.options.keys())
            shuffle(keeeeys)
            newoptions = OrderedDict()
            for k in keeeeys:
                newoptions[k] = self.options[k]
            self.options = newoptions
    def getstr(self, selected=None, showCorrect=False):
        if showCorrect:
            outstr = "```css\n{Question: '"+self.question.replace('\'', '’')+"'}"
        else:
            outstr = "```markdown\n# "+self.question
        for a in range(len(self.options)):
            if a == selected:
                if showCorrect:
                    outstr+="\n."+chr(a+65)+":  "
                    if self.isCorrect(a+1):
                        outstr+="("+list(self.options.keys())[a].center(49)+")"
                    else:
                        outstr+="["+list(self.options.keys())[a].center(49)+"]"
                else:
                    outstr+="\n<["+chr(a+65)+"]> ["+list(self.options.keys())[a].center(46)+"]()"
            else:
                if showCorrect:
                    outstr+="\n{"+chr(a+65)+":} "
                    if self.isCorrect(a+1):
                        outstr+="("+list(self.options.keys())[a].center(49)+")"
                    else:
                        outstr+="["+list(self.options.keys())[a].center(49)+"]"
                else:
                    outstr+="\n<<"+chr(a+65)+">> ["+list(self.options.keys())[a].center(46)+"]()"
        return outstr+'```'

def load_data_file(file):
    res = {}
    print('\t\tLoading %s' % file)
    if os.path.isfile('Data/'+file):
        with open('Data/'+file, 'rb') as f:
            res = pickle.load(f)
    else:
        with open('Data/'+file, 'wb') as f:
            pickle.dump(res, f)
    copyfile('Data/'+file, 'Data/Backup/'+file)
    print('\t\t%s Loaded' % file)
    return res



# http://web.archive.org/web/20130306020911/http://nadiana.com/pil-tutorial-basic-advanced-drawing#Drawing_Rounded_Corners_Rectangle
def round_corner(radius, fill):
    """Draw a round corner"""
    corner = Image.new('RGBA', (radius, radius), (0, 0, 0, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner

def round_rectangle(size, radius, fill):
    """Draw a rounded rectangle"""
    width, height = size
    rectangle = Image.new('RGBA', size, fill)
    corner = round_corner(radius, fill)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius)) # Rotate the corner and paste it
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle
