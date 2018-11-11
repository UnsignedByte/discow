# @Author: Edmund Lam <edl>
# @Date:   10:01:28, 03-Nov-2018
# @Filename: strutils.py
# @Last modified by:   edl
# @Last modified time: 08:35:32, 11-Nov-2018

from discow.handlers import discow_prefix
import re

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

def split_str_chunks(content, maxlen, prefix='', suffix=''):
    clist = []
    cchunk = ""
    for l in content.splitlines():
        if len(cchunk)+len(l)> maxlen-len(prefix)-len(suffix):
            clist.append(prefix+cchunk+suffix)
            cchunk = ""
        while len(l) > maxlen-len(prefix)-len(suffix):
            clist.append(prefix+l[:maxlen-len(prefix)-len(suffix)]+suffix)
            l = l[maxlen-len(prefix)-len(suffix):]
        cchunk+=l+"\n"
    clist.append(prefix+cchunk+suffix)
    return clist

def escape_markdown(s):
    return re.sub(r'(?:`|\(|\\|\[|\]|\)|\*|~|_)', r'\\\g<0>', s)
