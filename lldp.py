import struct
import json
from micropython import const

LLDP_TYPE = b"\x88\xcc"

def bytes2bin(b):
    return [int(X) for X in "".join(["{:0>8}".format(bin(X)[2:])for X in b])]

def getTLV(tlvBytes):
    print(tlvBytes)
    x = [ tlvBytes[0], tlvBytes[1] ]
    tlvTempType = bytes2bin(x)[0:7]
    ia = int()
    tlvType = int()
    while ia < len(tlvTempType):
        tlvType = tlvType + (tlvTempType[ia] << ia)
        ia += 1
    tlvTempLength = bytes2bin(x)[8:16]
    ib = int()
    tlvLength = int()
    while ib < len(tlvTempLength):
        tlvLength = tlvLength + (tlvTempLength[ib] << ib)
        ib += 1
    return (tlvType, tlvLength)

def parseLLDP(data):
    print(data)
    i = int()
    retval = []
    while i < (len(data) - 4):
        tlvType = None
        tlvLength = None
        (tlvType, tlvLength) = getTLV(data[i:i+2])
        returndata = {
                'type': tlvType,
                'length': tlvLength,
                'data': None
                }
        print("tlvLength: {}".format(tlvLength))
        print(data[i+3:i+tlvLength])
        returndata['data'] = data[i+3:i+tlvLength].decode('ascii')
        retval.append(returndata)
        i += tlvLength
    return retval

