# @Author: Edmund Lam <edl>
# @Date:   15:30:36, 12-Aug-2018
# @Filename: utils.py
# @Last modified by:   edl
# @Last modified time: 18:00:26, 05-Nov-2018


import itertools
from random import shuffle
from collections import OrderedDict

def group(lst, n):
  return list(zip(*[itertools.islice(lst, i, None, n) for i in range(n)]))

def chunkify(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]
