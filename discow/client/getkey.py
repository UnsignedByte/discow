import os

_keyfile = "discow/client/data/key.txt"

def readKey():
    return open(_keyfile, 'r').read()

_keyvalue = None

def key(cache = True):
    global _keyvalue

    if not _keyvalue:
        if cache:
            _keyvalue = readKey().strip()
            return _keyvalue
        return readKey()
    else:
        return _keyvalue
