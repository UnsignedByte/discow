# @Author: Edmund Lam <edl>
# @Date:   15:30:46, 04-Nov-2018
# @Filename: fileutils.py
# @Last modified by:   edl
# @Last modified time: 15:42:27, 07-Nov-2018

import os
import pickle
from shutil import copyfile
from discow.handlers import bot_data

def load_data_file(file):
    res = {}
    if os.path.isfile('Data/'+file):
        with open('Data/'+file, 'rb') as f:
            res = pickle.load(f)
    else:
        with open('Data/'+file, 'wb') as f:
            pickle.dump(res, f)
    copyfile('Data/'+file, 'Data/Backup/'+file)
    print('\t\t%s Loaded' % file)
    return res

def nested_set(value, *keys):
    dic = bot_data
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def nested_pop(*keys):
    nested_get(*keys[:-1]).pop(keys[-1], None)


def alt_pop(key, *keys):
    nested_get(*keys).pop(key)


def nested_get(*keys, default=None):
    dic = bot_data
    for key in keys:
        dic=dic.setdefault( key, {} )
    if not dic:
        dic=default
    return dic


def nested_append(value, *keys):
    v = nested_get(*keys)
    if v:
        v.append(value)
    else:
        nested_set([value], *keys)

def nested_extend(value, *keys):
    v = nested_get(*keys)
    if v:
        v.extend(value)
    else:
        nested_set([value], *keys)

def nested_addition(to_add, *keys, default=0):
    nested_set(nested_get(*keys, default=default)+to_add, *keys)

def nested_multiplication(to_mult, *keys, default=0):
    nested_set(nested_get(*keys, default=default)*to_mult, *keys)

def nested_remove(value, *keys, **kwargs):
    kwargs['func'] = kwargs.get('func', None)
    v = nested_get(*keys)
    if not v:
        return
    try:
        if not kwargs['func']:
            v.remove(value)
        else:
            for x in v:
                if kwargs['func'](x, value):
                    v.remove(x)
                    break
    except ValueError:
        return

def get_data():
    return bot_data
