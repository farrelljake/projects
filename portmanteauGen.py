#!/usr/bin/env python3
"""
Generates portmanteaus, converts graphemes to phonemes, and then checks against phonotactic constraints for English
"""

from g2p_en import G2p
from argparse import ArgumentParser

def phonotactics(blendedWordList):

    # Constraints: 
    #   - no word initial NX or NG
    #   - if first phoneme is S, then only P T K M N L W
    #   - if SH, then R
    #   - if second letter = l -> first letter = pbf, if second letter = r -> first letter = pbft TH kg, if second letter = w -> first letter = td TH k
    #   - skr/smj are possible, spw/stl/stw/snj are not
    #   - word final mb NGg mv nTHIS not possible, neither lTHIS lDj lg lNG
    
    return blendedWordList

def orthoFilter(blendedWordList):
    filteredList = []

    # must have a vowel or semivowel
    # cannot contain:   bx, cj, cv, cx, dx, fq, fx, gq, gx, hx, jc, jf, jg, jq, js, jv, jw, jx, jz, kq, kx, mx, px, pz, qb, qc, qd, qf, qg, qh, qj, qk, ql, 
    #                   qm, qn, qp, qs, qt, qv, qw, qx, qy, qz, sx, vb, vf, vh, vj, vm, vp, vq, vt, vw, vx, wx, xj, xx, zj, zq, zx

    for blend in blendedWordList:
        if "a" in blend or "e" in blend or "i" in blend or "o" in blend or "u" in blend or "y" in blend:
            filteredList.append(blend)


    return filteredList

def blendWord(w1, w2):
    blendedWordList = []

    if len(w1) > len(w2):
        shortWord = w2
        longWord = w1
    else:
        shortWord = w1
        longWord = w2

    for i in range(len(shortWord) - 1):
        for j in range(len(longWord) - 1):
            blendedWordList.append(shortWord[:len(shortWord) - i - 1] + longWord[len(longWord) - j - 1:])
            blendedWordList.append(longWord[:len(longWord) - j - 1] + shortWord[len(shortWord) - i - 1:])

    blendedWordList = orthoFilter(blendedWordList)

    return blendedWordList


def main():

    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('word1', help='first word')
    parser.add_argument('word2', help='second word')
    args = parser.parse_args()

    w1 = args.word1
    w2 = args.word2

    blendedWordList = blendWord(w1, w2)

#    blendedWordList = ["spot", "stop", "stew", "Scot", "smock", "snot", "slot", "swat", "shred"]

    for portmanteau in blendedWordList:
#        g2p = G2p()
#        out = g2p(portmanteau)
        print(portmanteau)
#        print(f"{portmanteau}: {out}")

if __name__ == '__main__':
    main()
