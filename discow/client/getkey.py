import os

_keyfile = "discow/client/data/key.txt"
if not os.path.exists(_keyfile):
    print("It seems your bot key is unknown. Please input it below.")
    open(_keyfile, 'w+').write(input("Bot Key:"))

def readKey():
    return open(_keyfile, 'r').read().strip()

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
