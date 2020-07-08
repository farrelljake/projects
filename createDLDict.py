#!/usr/bin/env python3
"""
Creates a dictionary of Levenshtein distances
"""

import sys
import json
import numpy as np

from argparse import ArgumentParser


def calcDL(w1, w2):
    n1 = len(w1)
    n2 = len(w2)

    distMatrix = np.zeros((n1 + 1, n2 + 1), dtype=int)

    # initialise first row and first column
    for i in range(n1 + 1):
        distMatrix[i, 0] = i
    for j in range(n2 + 1):
        distMatrix[0, j] = j

    # loop through matrix
    for i in range(n1):
        for j in range(n2):
            # if characters are the same, no cost
            if w1[i] == w2[j]:
                cost = 0
            else:
                cost = 1

            # update matrix - insert, delete, replace
            distMatrix[i + 1, j + 1] = min(distMatrix[i, j + 1] + 1, distMatrix[i + 1, j] + 1, distMatrix[i, j] + cost)

            # check for transpositions
            if i > 0 and j > 0 and w1[i] == w2[j - 1] and w1[i - 1] == w2[j]:
                distMatrix[i + 1, j + 1] = min(distMatrix[i + 1, j + 1], distMatrix[i - 1, j - 1] + cost)

    # limit distance
    if distMatrix[n1][n2] > 3:
        return []

    i = n1
    j = n2
    ops = []

    # get specific operations
    while i != -1 and j != -1:
        if i > 1 and j > 1 and w1[i - 1] == w2[j - 2] and w1[i - 2] == w2[j - 1]:
            if distMatrix[i - 2, j - 2] < distMatrix[i, j]:
                ops.insert(0, ('transpose', i - 1, i - 2))
                i -= 2
                j -= 2
                continue

        index = np.argmin([distMatrix[i - 1, j - 1], distMatrix[i, j - 1], distMatrix[i - 1, j]])

        if index == 0:
            if distMatrix[i, j] > distMatrix[i - 1, j - 1]:
                ops.insert(0, ('replace', i - 1, j - 1))
            i -= 1
            j -= 1
        elif index == 1:
            ops.insert(0, ('insert', i - 1, j - 1))
            j -= 1
        elif index == 2:
            ops.insert(0, ('delete', i - 1, i - 1))
            i -= 1

    return ops


def createEditDict(words):
    editDict = {}

    for i, w1 in enumerate(words):
        for w2 in words:
            if w1 == w2:
                continue
            if abs(len(w1) - len(w2)) > 2:
                continue
            if (w2 in editDict.keys() and w1 in editDict[w2].keys()):
                continue

            ops = calcDL(w1, w2)

            if ops:
                editDict[w1] = {w2: ops}

        sys.stderr.write('Processed %s / %s words\r' % (i + 1, len(words)))
    sys.stderr.write("\n")

    return editDict


def main():
    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('corpus', metavar='File name', help='A text file')
    parser.add_argument('--writeout', help='Write to stdout', action='store_true', default=False)
    parser.add_argument('--minsize', help='Minimum wordsize', default=4, type=int)

    args = parser.parse_args()

    fileInput = args.corpus
    writeout = args.writeout
    minsize = args.minsize

    words = []

    with open(fileInput) as f:
        for line in f:
            tempLine = line.strip().split(" ")
            if tempLine:
                for word in tempLine:
                    tempWord = word.strip()
                    if tempWord and len(tempWord) >= minsize and tempWord not in words:
                        words.append(tempWord)

    editDict = createEditDict(words)

    if writeout:
        for key, value in editDict.items():
            sys.stdout.write(f"{key} : {value}\n")
    else:
        sys.stdout.write(json.dumps(editDict, separators=(',', ':')))


if __name__ == "__main__":
    main()
