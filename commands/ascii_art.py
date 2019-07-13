# @Author: Edmund Lam <edl>
# @Date:   17:50:00, 16-Oct-2018
# @Filename: ascii_art.py
# @Last modified by:   edl
# @Last modified time: 09:15:33, 11-Nov-2018

import asyncio
from discow.handlers import add_message_handler
from discord import Embed
from PIL import Image,ImageDraw,ImageFont,ImageEnhance, ImageOps
import os
import math

CONST_WHITE = 0.1
WHITE_THRESHOLD = 0.3

BRAILLES = [chr(i) for i in range(int('2800', 16), int('2900', 16))]

def sigmoidSquish(x):
    return 1/(1+math.e**(x/-100000))

def isNum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def CALC_WHITE(x):
    return 0 if x < CONST_WHITE else tround(x)+1

def Braille(img, max, fsize):
    w,h=img.size
    out=[]
    h/=fsize[1]/fsize[0] * 1/2
    if max is not None:
        f = math.sqrt(max/(h/4*w/2))
        w *=f
        h *=f
    w = round(w//2*2)
    h = round(h//4*4)

    enhancement = ((-sigmoidSquish(w*h)+1)+1)**6
    # enhancement = 1
    img = ImageEnhance.Sharpness(img.resize((w,h), Image.ANTIALIAS)).enhance(enhancement)
    print("Sharpness factor: "+str(enhancement))
    colors = []
    for color in img.getdata():
        try:
            r=color[0]
            g=color[1]
            b=color[2]
            #0.3*r + 0.59*g + 0.11*b
            colors.append(1-((0.2126*r + 0.7152*g + 0.0722*b)/255))
        except TypeError:
            colors.append(1-color/255)

    for i in range(h//4):
        line = ""
        for j in range(w//2):
            b = i*4*w+j*2
            aa, bb = colors[b:b+2]
            cc, dd = colors[b+w:b+w+2]
            ee, ff = colors[b+2*w:b+2*w+2]
            gg, hh = colors[b+3*w:b+3*w+2]

            if list(map(lambda x:CALC_WHITE(x), [aa, bb, cc, dd, ee, ff, gg, hh])) == [1]*8:
                line+=BRAILLES[64]
            else:
                line+=BRAILLES[64*(tround(hh)*2+tround(gg))+int(''.join(list(map(lambda x:str(tround(x)), [ff,dd,bb,ee,cc,aa]))), 2)]
        out.append(line)
    mr = w
    for i in out:
        mr = min(len(i)-len(i.lstrip('\u2800')), mr)
    out = '\n'.join([i[mr:].rstrip('\u2800') for i in out])

    return out.strip("\n")


def tround(x):
    return 0 if x<WHITE_THRESHOLD else 1








async def braille(Bot, msg):
    args = dict(map(lambda x: "=".split(x, 1), parse_command(msg.content)[1:]))
    if len(args) <= 4:
        return
    else:
        await Bot.send_message("Too many arguments!")

add_message_handler(braille, "braille")
add_message_handler(braille, "art")
