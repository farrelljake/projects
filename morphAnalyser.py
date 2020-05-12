#!/usr/bin/env python3
"""
morphAnalyser

The function of this script is to identify a potential combination of a stem and morphemes in a given word.
The flow is main -> buildCoordDict -> coordMatch => (findSeqs -> buildPath -> filterSeqs)

TODO:
    Single Morphs:
    - OPTIONAL: Fix greedyMatch to work on morphs that overlap on the last/first char of each morph
    - Fix to work with single items at beginning (for prefixes) and end (for suffixes) of word
    - Work on extracting data straight from lexDict instead of building morphDict
    - Implement filterSeqs to cut down on redundant morph splitter info
    - Implement filterSeqs to create likely sequences of morphs and stems
    
    Word Comparison:
    - Implement variant checker
    - Find common differences
"""

import sys
import json

from argparse import ArgumentParser
from csv import reader
from itertools import combinations, chain
from collections import Counter


def findVariants(word, variantGroups, coordType):
    variantsFound = []

    if coordType == "suffixes" and word[0] != "-":
        word = "-" + word
    elif coordType == "prefixes" and word[-1] != "-":
        word = word + "-"

    for i, varList in enumerate(variantGroups):
        if word in varList:
            variantsFound.append(variantGroups[i])

    if len(variantsFound) and type(variantsFound[0]) == list:
        return variantsFound[0]
    else:
        return variantsFound


def compareWords(wordComparisons, morphDict):
    variantList = morphDict["has_variants"]
    variantGroups = morphDict["variants"]
    coordType = ""

    for w1, w2, dist in wordComparisons:
        w1HasVar = False
        w2HasVar = False

        if w1 in variantList:
            w1Vars = findVariants(w1, variantGroups, coordType)
            w1HasVar = True

        if w2 in variantList:
            w2Vars = findVariants(w2, variantGroups, coordType)
            w2HasVar = True

        if w1HasVar and w2HasVar:
            if w1 in w2Vars and w2 in w1Vars:
                print(f"{w1} and {w2} are variants")

        print(f"{w1} -> {w2} {dist}")

    return None


def filterSeqs(pathList, coordType, possibleStems, coordDict):
    # use variants
    #paths need to be filtered by:
    # suffix cannot appear before prefix or stem / prefix cannot appear after stem or suffix
    # must have a stem

    print(coordType, pathList)

    return []


def findStem(word, coordDict, stems):
    stemCoords = list(coordDict["stems"].keys())
    lexMatches = []
    stemList = []
    stemFound = False

    # check if part of word can be identified as stem
    for stem in stemCoords:
        if stem in stems:
            lexMatches.append(coordDict["stems"][stem])
        
        stemList.append(coordDict["stems"][stem])

    if lexMatches:
        #stemMatches = lexMatches
        stemMatches = max(lexMatches, key=len)
        stemFound = True
    else:
        stemMatches = stemList

    return stemFound, stemMatches


def buildPath(pathList, pathDict):
    newPathList = []
    count = 0
    countStop = len(pathList)
    stopSignal = False

    for path in pathList:
        endPoint = path[-1]
        if endPoint in pathDict.keys():
            for newEndPoint in pathDict[endPoint]:
                newPath = path.copy()
                newPath.append(newEndPoint)
                newPathList.append(newPath)
        else:
            newPathList.append(path)
            count += 1
    
    # will loop until all paths exhausted
    if count == countStop:
        stopSignal = True

    return newPathList, stopSignal


def findSeqs(word, coords, coordType):
    #coords is a list of the indices for prefixes, stems, or suffixes
    filteredCoords = []
    pathDict = {}
    pathList = []
    stopSignal = False

    # prefilter coordinates depending on type:
    # suffixes cannot start at 0, prefixes cannot end at word length
    if coordType == "suffixes":
        for coord in coords:
            if coord[0] != 0:
                filteredCoords.append(coord)
        coords = filteredCoords
    elif coordType == "prefixes":
        for coord in coords:
            if coord[1] != len(word):
                filteredCoords.append(coord)

        coords = filteredCoords
    elif coordType == "stems":
        filteredCoords = coords

    # if filteredCoords is empty, then no possible matches
    if not filteredCoords:
        return []
    
    # create pathDict to loop over
    for coord_i in coords:
        for coord_j in coords:
            if coord_i[1] == coord_j[0]:
                if coord_i not in pathDict.keys():
                    pathDict[coord_i] = [coord_j]
                else:
                    pathDict[coord_i].append(coord_j)

    # loop over pathDict to get first pathList
    for key, values in pathDict.items():
        if len(values) > 1:
            #multiple branches
            for value in values:
                pathList.append([key, value])
        else:
            pathList.append([key, values[0]])
    
    while stopSignal == False:
        pathList, stopSignal = buildPath(pathList, pathDict)

    return pathList


def coordMatch(word, coordDict, stems, lexDict, morphDict):
    sequences = []
    charList = []
    morphList = []
    preCoords = ("prefixes", list(coordDict["prefixes"].keys()))
    stemCoords = ("stems", list(coordDict["stems"].keys()))
    sufCoords = ("suffixes", list(coordDict["suffixes"].keys()))
    morphAnalysis = {}
    variantList = morphDict["has_variants"]
    variantGroups = morphDict["variants"]

    morphTuple = (preCoords, stemCoords, sufCoords)
    stemFound, stemMatches = findStem(word, coordDict, stems)

    sys.stdout.write(f"Word is {word}, length: {len(word)}\n")
    if stemFound:
        sys.stdout.write(f"Possible stem(s):")
        for stem in stemMatches:
            sys.stdout.write(f"{stem} : {lexDict[stem][0][0]}\n")
    for morph in morphTuple:
        coordType, coords = morph
        pathList = findSeqs(word, coords, coordType)
        morphCounter = Counter()
        itemCount = 0

        # sequence filtering
        # sequences = filterSeqs(pathList, coordType, possibleStems, coordDict)

        sys.stdout.write(f"Possible {coordType}:\n")
        for path in pathList:
            charList = []
            morphList = []
            for coord in path:
                char = coordDict[coordType][coord]
                charList.append(char)
                if coordType == "suffixes":
                    char = "-" + char
                elif coordType == "prefixes":
                    char = char + "-"
                if char in lexDict.keys():
                    morph = lexDict[char][0][0]
                    if morph != None:
                        morphList.append(morph)
                        morphCounter[morph] += 1
                        itemCount += 1
                    else:
                        if char in variantList:
                            variantsFound = findVariants(char, variantGroups, coordType)
                            if variantsFound:
                                morphVariantList = []
                                for variant in variantsFound:
                                    if variant in lexDict.keys():
                                        morphVariantList.append(lexDict[variant][0][0])
                                morphVariantList =  filter(None, morphVariantList)
                                variants = "/".join(morphVariantList)
                                morphList.append(variants)
                        else:
                            morphList.append("∅")
                else:
                    if char in variantList:
                        variantsFound = findVariants(char, variantGroups, coordType)
                        if variantsFound:
                            morphVariantList = []
                            for variant in variantsFound:
                                if variant in lexDict.keys():
                                    morphVariantList.append(lexDict[variant][0][0])

                            morphVariantList =  filter(None, morphVariantList)
                            variants = "/".join(morphVariantList)
                            morphList.append(variants)
                    else:
                        morphList.append("∅")
            charOut = "-".join(charList)
            # get rid of possible Nones
            morphList = list(filter(None, morphList))
            morphOut = "-".join(morphList)
            sys.stdout.write(f"{charOut} : ")
            sys.stdout.write(f"{morphOut}\n")
        sys.stdout.write("\n")
    sys.stdout.write(f"{morphCounter}, Total morphs: {itemCount} \n\n")
    return None


def buildCoordDict(word, morphDict):
    coordDict = {"suffixes": {}, "prefixes": {}, "stems": {}}
    stems = morphDict["stems"]
    wordFound = False

    if word in stems:
        wordFound = True
        coordDict["stems"] = word
        return coordDict, stems, wordFound

    # creates every possible sequential ordering
    allCombos = [((i, j), word[i:j]) for i, j in combinations(range(len(word) + 1), 2)]

    for combo in allCombos:
        isSuf = False
        isPre = False

        # checks for suffixes, ignores matches at beginning of words
        if "-" + combo[1] in morphDict["suffixes"] and combo[1] != word and int(combo[0][0]) != 0:
            coordDict["suffixes"][combo[0]] = combo[1]
            isSuf = True

        # checks for prefixes, ignores matches at end of words
        if combo[1] + "-" in morphDict["prefixes"] and combo[1] != word and int(combo[0][1]) != len(word):
            coordDict["prefixes"][combo[0]] = combo[1]
            isPre = True

        # if neither flag is set, assume this is possibly (part of) the stem
        if not isSuf and not isPre:
            coordDict["stems"][combo[0]] = combo[1]

    return coordDict, stems, wordFound


def getWordLists(tsvFile):
    wordList = []
    wordComparisons = []

    # skip header
    next(tsvFile)

    for line in tsvFile:
        w1 = line[0]
        w2 = line[1]
        dist = line[2]

        wordComparisons.append((w1, w2, dist))

        if w1 not in wordList:
            wordList.append(w1)
        if w2 not in wordList:
            wordList.append(w2)

    return wordList, wordComparisons


def createMorphDict(lexDict):
    
    morphDict = {}
    variantGroups = []
    variantList = []
    stemList = []
    suffixList = []
    prefixList = []
    hasVariantList = []

    for i, j in lexDict.items():
        variantList = []
        variantList.append(i)
        if i[0] == "-":
            suffixList.append(i)
            for x in j[0][1]:
                if x is not None:
                    variantList.append(x)
                    hasVariantList.append(x)
                    suffixList.append(str(x))
        elif i[-1] == "-":
            prefixList.append(i)
            for x in j[0][1]:
                if x is not None:
                    variantList.append(x)
                    hasVariantList.append(x)
                    prefixList.append(str(x))
        else:
            stemList.append(i)
            for x in j[0][1]:
                if x is not None:
                    variantList.append(x)
                    hasVariantList.append(x)
                    stemList.append(str(x))

        if len(set(variantList)) > 1:
                variantGroups.append(variantList)
    
    morphDict["suffixes"] = suffixList
    morphDict["prefixes"] = prefixList
    morphDict["variants"] = variantGroups
    morphDict["has_variants"] = hasVariantList
    morphDict["stems"] = stemList

    return morphDict


def main():
    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('input1', help='A JSON file of the lexicon')
    parser.add_argument('input2', help='A TSV file with Levenshtein distances')
    parser.add_argument('--compare', help='Compare words', action='store_true', default=False)       
    parser.add_argument('--size', help='Option to ignore words beneath a certain size', default=0, type=int)
    args = parser.parse_args()

    fileInput = args.input1
    compareInput = args.input2
    wordSize = args.size
    compare = args.compare

    with open(fileInput) as f:
        raw = f.read()
        lexDict = dict(json.loads(raw))

    morphDict = createMorphDict(lexDict)

    with open(compareInput) as wl:
        distTSV = wl.readlines()
    
    tsvFile = reader(distTSV, delimiter="\t")
    wordList, wordComparisons = getWordLists(tsvFile)

    if compare:
        compareWords(wordComparisons, morphDict)
        return None

    for word in wordList:
        # builds coordDict, which is the indicies of every identifable prefix and suffix and possible stem in a word
        coordDict, stems, wordFound = buildCoordDict(word, morphDict)

        # check to see if buildCoordDict found that word is already in the dictionary
        if not wordFound:
            coordMatch(word, coordDict, stems, lexDict, morphDict)
        else:
            if word in lexDict.keys():
                sys.stdout.write(f"{word} : {lexDict[word][0][0]}\n\n")
            else:
                sys.stdout.write(f"{word} : variant\n\n")
    

if __name__ == '__main__':
    main()
