#!/usr/bin/env python3
"""
Creates a dictionary of Levenshtein distances
"""

import sys
import json

from argparse import ArgumentParser
from collections import Counter, defaultdict


def buildTemplates(opsList, key, subkey):
    delayedOperations = []
    operationsTemplate = ["_"] * len(key)
    startTemplate = ["_"] * len(key)
    endTemplate = ["_"] * len(key)

    for operation in opsList:
        command = operation[0]
        fromLetterIndex = operation[1]
        toLetterIndex = operation[2]

        # insertions must be delayed because they mess up the ordering info
        if command == "insert":
            delayedOperations.append(operation)
        elif command == "delete":
            operationsTemplate[fromLetterIndex] = "D"
            startTemplate[fromLetterIndex] = key[fromLetterIndex]
            endTemplate[fromLetterIndex] = "∅"
        elif command == "replace":
            operationsTemplate[fromLetterIndex] = "R"
            startTemplate[fromLetterIndex] = key[fromLetterIndex]
            endTemplate[fromLetterIndex] = subkey[toLetterIndex]
        elif command == "transpose":
            operationsTemplate[fromLetterIndex] = "T"
            operationsTemplate[toLetterIndex] = "T"
            startTemplate[fromLetterIndex] = key[fromLetterIndex]
            startTemplate[toLetterIndex] = key[toLetterIndex]
            endTemplate[fromLetterIndex] = key[toLetterIndex]
            endTemplate[toLetterIndex] = key[fromLetterIndex]

    for insert in delayedOperations:
        fromLetterIndex = insert[1]
        toLetterIndex = insert[2]

        if fromLetterIndex > len(operationsTemplate):
            operationsTemplate.extend("I")
            startTemplate.extend("_∅_")
            endTemplate.extend(subkey[toLetterIndex])
        else:
            operationsTemplate.insert(toLetterIndex, "I")
            startTemplate.insert(toLetterIndex, "_∅_")
            endTemplate.insert(toLetterIndex, subkey[toLetterIndex])

    ops, lineA, lineB = templateHelper(operationsTemplate), templateHelper(startTemplate), templateHelper(endTemplate)

    if len(lineA) > 1:
        return [], []

    return ops, list(zip(lineA, lineB))[0]


def templateHelper(template):
    return list(filter(lambda x: x != "", "".join(template).split("_")))


def main():
    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('editDict', help='A JSON editDict')
    parser.add_argument('--json', help='Dump to JSON', action='store_true', default=False)
    parser.add_argument('--examples', help='Provide instances of examples', action='store_true', default=False)

    args = parser.parse_args()

    fileInput = args.editDict
    dumpToJSON = args.json
    examples = args.examples

    with open(fileInput) as f:
        editDict = json.loads(f.read())

    variantDict = Counter()
    examplesDict = defaultdict(list)

    for i, items in enumerate(editDict.items()):
        key, subDict = items
        for subkey, operations in subDict.items():
            ops, variant = buildTemplates(operations, key, subkey)

            if ops:
                assembledKey = tuple(sorted([variant[0] + "/" + variant[1], variant[1] + "/" + variant[0]]))
                variantDict[assembledKey] += 1
                examplesDict[assembledKey].append([key, subkey])
        sys.stderr.write('Processed %s / %s words\r' % (i + 1, len(editDict.keys())))
    sys.stderr.write("\n")

    if examples:
        print(examplesDict)

    if dumpToJSON:
        sys.stdout.write(json.dumps(variantDict, separators=(',', ':')))
    else:
        for key, value in variantDict.most_common():
            sys.stdout.write(f"{key} : {value}\n")


if __name__ == "__main__":
    main()
