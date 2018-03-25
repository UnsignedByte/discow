import os

_keyfile = os.path.dirname(__file__) + "/data/key.txt"

def readKey():
    return open(_keyfile, 'r').read().replace('\n', '')

_keyvalue = None

def key(cache = True):
    global _keyvalue

    if not _keyvalue:
        if cache:
            _keyvalue = readKey()
            return _keyvalue
        return readKey()
    else:
        return _keyvalue