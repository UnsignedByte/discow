# @Author: Edmund Lam <edl>
# @Date:   15:55:15, 12-Aug-2018
# @Filename: wolframalpha.py
# @Last modified by:   edl
# @Last modified time: 19:58:42, 04-Nov-2018

import asyncio
import os
import pyimgur
from utils import imgutils, msgutils, strutils
from discow.handlers import add_message_handler, add_private_message_handler
from discord import Embed
import wolframalpha
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import itertools
import textwrap
import urllib

print("\tInitializing Wolfram Alpha Command")

_wakey = "Data/keys/wolframalphakey.txt"
_imgurkey = "Data/keys/imgurkey.txt"
wa_app_id = None

if not os.path.exists(_wakey):
    print("Missing wolfram alpha key. Add one for wolfram alpha API integration.")
else:
    wa_app_id = open(_wakey, 'r').read().strip()

imgur_app_id = None

if not os.path.exists(_imgurkey):
    print("Missing wolfram alpha key. Add one for wolfram alpha API integration.")
else:
    imgur_app_id = open(_imgurkey, 'r').read().strip()

wa_client = wolframalpha.Client(wa_app_id)
imgur_client = pyimgur.Imgur(imgur_app_id)

async def query(Bot, msg):

    question = strutils.strip_command(msg.content)
    em = Embed(title=question, description="Requesting Data", colour=0xe4671b)
    oldem = await msgutils.send_embed(Bot, msg, em)
    res = wa_client.query(question)

    if "@pods" not in res:
        try:
            resp = urllib.request.urlopen(res["@recalculate"])
            assert resp.headers.get_content_type() == 'text/xml'
            assert resp.headers.get_param('charset') == 'utf-8'
            res = wolframalpha.Result(resp)
        except ValueError:
            pass

    titles = []
    images = []

    try:

        for pod in res.pods:
            titles.append(textwrap.wrap(pod.title, width=50))
            subimgs = []
            for sub in pod.subpods:
                subimgs.append(Image.open(BytesIO(requests.get(sub['img']['@src']).content)))
            images.append(subimgs)
    except AttributeError:
        em = Embed(title=question, description="No results", colour=0xe4671b)
        await msgutils.edit_embed(Bot, oldem, em)
        return

    chained_imgs = list(itertools.chain.from_iterable(images))




    widths, heights = zip(*(i.size for i in chained_imgs))

    item_padding = 20
    font_size = 15
    font_padding = 3


    max_width = max(widths)+2*item_padding
    total_height = sum(heights)+item_padding*(len(chained_imgs)+2+len(titles))+(font_padding+font_size)*len(list(itertools.chain.from_iterable(titles)))

    new_im = imgutils.round_rectangle((max_width, total_height), item_padding, "white")

    font = ImageFont.truetype("Data/Roboto-Regular.ttf", font_size)

    total_pods = 0

    draw = ImageDraw.Draw(new_im)
    y_offset = item_padding
    for i in range(len(titles)):
        pod = images[i]
        for line in titles[i]:
            draw.text((item_padding, y_offset), line, fill=(119, 165, 182), font=font)
            y_offset+=font_size+font_padding

        y_offset+=item_padding
        for im in pod:
            total_pods+=1
            new_im.paste(im, (item_padding,y_offset))
            y_offset += im.size[1]+item_padding
            if(total_pods < len(chained_imgs)):
                draw.line((0,y_offset-item_padding/2,max_width,y_offset-item_padding/2),fill=(233,233,233),width=1)


    new_im.save("Data/wa_save.png")

    res_img = imgur_client.upload_image("Data/wa_save.png", title=question)

    em = Embed(title=question, url=res_img.link, colour = 0xe4671b)
    em.set_image(url=res_img.link)
    await msgutils.edit_embed(Bot, oldem, em)

add_message_handler(query, "wolfram")
add_message_handler(query, "wolframalpha")
add_message_handler(query, "wa")
add_private_message_handler(query, "wolfram")
add_private_message_handler(query, "wolframalpha")
add_private_message_handler(query, "wa")
print("\tWolfram Alpha Command Initialized")
