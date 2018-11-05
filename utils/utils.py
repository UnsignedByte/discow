# @Author: Edmund Lam <edl>
# @Date:   15:30:36, 12-Aug-2018
# @Filename: utils.py
# @Last modified by:   edl
# @Last modified time: 20:19:11, 04-Nov-2018


import itertools
from random import shuffle
from collections import OrderedDict


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
