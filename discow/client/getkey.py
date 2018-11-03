import os

_keyfile = "Data/keys/key.txt"

if not os.path.exists(_keyfile):
    print("It seems your bot key is unknown. Please input it below.")
    open(_keyfile, 'w+').write(input("Bot Key:"))

def readKey():
    return open(_keyfile, 'r').read().strip()

_keyvalue = None

def key():
    global _keyvalue

    if not _keyvalue:
        return readKey()
    else:
        return _keyvalue
