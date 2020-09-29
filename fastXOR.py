#!/usr/bin/env python3
def mod4Bits(n):
    modTup = (n, 1, n + 1, 0)
    index = n % 4

    return modTup[index]

def quickXOR(n1, n2):
    return mod4Bits(n2) ^ mod4Bits(n1 - 1)
