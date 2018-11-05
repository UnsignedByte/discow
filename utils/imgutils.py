# @Author: Edmund Lam <edl>
# @Date:   10:00:34, 03-Nov-2018
# @Filename: imgutils.py
# @Last modified by:   edl
# @Last modified time: 10:00:48, 03-Nov-2018

from PIL import Image, ImageDraw

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
