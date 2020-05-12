#!/usr/bin/env python3
"""
Find unmatched brackets.
"""

import sys

from argparse import ArgumentParser
from collections import deque

def main():
    unmatchedList = []
    stack = deque()

    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('input', metavar='File name', help='An input file')
    parser.add_argument('--line', help='Makes checks line sensitive', action="store_true", default=False)
    parser.add_argument('--type', help='Type to match', choices=["brackets", "parentheses", "braces"], default="brackets")
    args = parser.parse_args()

    inputFile = args.input
    lineSensitive = args.line
    bracketType = args.type

    if bracketType == "brackets":
        leftChar = "<"
        rightChar = ">"
    elif bracketType == "braces":
        leftChar = "{"
        rightChar = "}"
    elif bracketType == "parentheses":
        leftChar = "("
        rightChar = ")"
    else:
        sys.stderr.write("Bracket type not recognised.\n")
        return None

    with open(inputFile) as text:
        readFile = text.readlines()

    for i, line in enumerate(readFile):
        if leftChar in line or rightChar in line:
            for char in line:
                if char == leftChar:
                    stack.append((char, i))
                if char == rightChar:
                    if lineSensitive:
                        if not stack:
                            unmatchedList.append((char, i))
                        elif stack[0][1] != i:
                            unmatchedList.append((char, i))
                        else:
                            stack.pop()
                    else:
                        if not stack:
                            unmatchedList.append((char, i))
                        else:
                            stack.pop()
        else:
            continue

        if lineSensitive:
            unmatchedList.extend(list(stack))
            stack.clear()

    if stack:
        for elem in stack:
            unmatchedList.append(elem)
    
    if unmatchedList:
        for char, lineNum in unmatchedList:
            sys.stdout.write(f"Unmatched {char} in line {lineNum + 1}\n")
    else:
        sys.stdout.write(f"No unmatched '{leftChar}{rightChar}' detected.\n")

                    



if __name__ == '__main__':
    main()

