# @Author: Edmund Lam <edl>
# @Date:   17:59:50, 05-Nov-2018
# @Filename: objutils.py
# @Last modified by:   edl
# @Last modified time: 17:59:56, 05-Nov-2018
def integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
