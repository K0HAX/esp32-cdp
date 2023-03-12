#!/usr/bin/env python
def bytes2bin(b):
    return [int(X) for X in "".join(["{:0>8}".format(bin(X)[2:])for X in b])]

