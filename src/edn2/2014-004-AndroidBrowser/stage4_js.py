#!/usr/bin/env python

import string
import sys
import os

# MAGIC: -213173581276 (= -1 * 0x44 * 0xbadadd07)
# Magic checksum
MAGIC = -213173581276

KEY = ${B_KEY}
FAKE_KEY = ${B_FAKE_KEY}

def stage4_js(magic):
    if str(magic) == str(MAGIC):
        key = KEY
    else:
        key = FAKE_KEY

    with open("stage4.js") as fp:
        content = fp.read()

    tpl = string.Template(content)

    key_js  = "["
    key_js += ", ".join(["0x{:02x}".format(ord(x)) for x in key])
    key_js += "]"

    return tpl.safe_substitute({"R_KEY": key_js})
    
def main():
    env = os.environ
    magic = env.get('_REQUEST__trk')

    data = stage4_js(magic)
    sys.stdout.write(data)
    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
