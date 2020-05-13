#!/usr/bin/env python3
"""
Converts between TSVs and CSVs
TODO:
    - Implement reverse
"""

import sys
import re

from argparse import ArgumentParser
from csv import reader


def escapeChar(cell, char, escapeType):

    if escapeType == "quotes":
        escapedCell = '"' + cell + '"'
    elif escapeType == "slash":
        charRe = '\\' + char
        escapedCell = re.sub(char, charRe, cell)
    elif escapeType == "newline":
        charRe = "\n" + char
        escapedCell = re.sub(char, charRe, cell)
    else:
        sys.stderr.write("ERROR: escape type not recognised")
        return cell

    return escapedCell


def toCSV(fileInput, isExcel, escapeType):

    if not isExcel:
        with open(fileInput) as f:
            tsvFile = reader(f, delimiter="\t")

            for i, row in enumerate(tsvFile):
                for j, cell in enumerate(row):
                    if '"' in cell:
                        if cell.count('"') % 2 != 0:
                            sys.stderr.write('WARNING: unmatched " detected in row {}, cell {}!\n'.format(i + 1, j+1))

                        noQuotesCell = re.sub('"', '""', cell)
                    else:
                        noQuotesCell = cell

                    if "," in cell:
                        escapedCell = escapeChar(noQuotesCell, ",", escapeType)
                        sys.stdout.write(escapedCell + ",")
                    else:
                        sys.stdout.write(noQuotesCell + ",")

                sys.stdout.write("\n")
    else:
        with open(fileInput) as f:
            tsvFile = reader(f, dialect="excel-tab")

            for row in tsvFile:
                for cell in row:
                    if '"' in cell:
                        if cell.count('"') % 2 != 0:
                            sys.stderr.write('WARNING: unmatched " detected in row {}, cell {}!\n'.format(i + 1, j+1))

                        noQuotesCell = re.sub('"', '""', cell)
                    else:
                        noQuotesCell = cell

                    if "," in cell:
                        escapedCell = escapeChar(noQuotesCell, ",", escapeType)
                        sys.stdout.write(escapedCell + ",")
                    else:
                        sys.stdout.write(noQuotesCell + ",")

                sys.stdout.write("\n")


def toTSV(fileInput, isExcel, escapeType):

    sys.stdout.write("Not implemented yet.\n")

    return None


def main():
    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('input', metavar='File name', help='A CSV or TSV file')
    parser.add_argument('-d', dest='direction', help='Specifies the direction of the conversion', choices=["tocsv", "totsv"], default="tocsv")
    parser.add_argument('--excel', dest='excel', action="store_true", default=False)
    parser.add_argument('--escape', dest='escape', choices=["quotes", "slash", "newline"], default="quotes")
    args = parser.parse_args()

    direction = args.direction
    fileInput = args.input
    isExcel = args.excel
    escapeType = args.escape

    if direction == "totsv":
        toTSV(fileInput, isExcel, escapeType)
    elif direction == "tocsv":
        toCSV(fileInput, isExcel, escapeType)
    else:
        # this should never trigger
        sys.stderr.write("File type not recognised! Please specify which direction you want to convert with '-d tocsv' or '-d totsv'.")


if __name__ == '__main__':
    main()
