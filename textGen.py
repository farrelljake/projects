#!/usr/bin/env python3
"""
Get ngrams from file
"""

import sys
import re
import random

from argparse import ArgumentParser
from nltk.util import ngrams
from collections import Counter, defaultdict


def generateText(probs, genText, ngramType, n, seed):
    keepGenerating = True
    text = seed.split()

    if len(text) < n - 1:
        return f"ERROR: Provided text is {len(text)} words long - expected at least {n - 1} words."
    elif len(text) > n - 1:
        sys.stdout.write(f"Provided text is {len(text)}, but n is {n} - using only the last {n - 1} word(s).\n")

    loopCount = 0

    while keepGenerating:
        randThreshold = random.random()
        accumProb = .0

        if n > 2:
            sliceN = (n - 1) * -1
            prevWords = tuple(text[sliceN:])
        else:
            prevWords = text[-1]

        for word, prob in probs[prevWords].items():
            accumProb += prob

            if accumProb >= randThreshold:
                text.append(word)
                loopCount = 0
                break

        loopCount += 1

        if len(text) >= genText or loopCount > 3:
            keepGenerating = False

    return "Generated Sentence: " + " ".join(text)


def calcProbs(ngramFreqs, n):
    probs = defaultdict(lambda: defaultdict(lambda: 0))

    if n == 2:
        for bigram, count in ngramFreqs.items():
            probs[bigram[0]][bigram[1]] += count

        for w1 in probs:
            total = float(sum(probs[w1].values()))
            for w2 in probs[w1]:
                probs[w1][w2] /= total
    elif n == 3:
        for trigram, count in ngramFreqs.items():
            probs[(trigram[0], trigram[1])][trigram[2]] += count

        for w1w2 in probs:
            total = float(sum(probs[w1w2].values()))
            for w3 in probs[w1w2]:
                probs[w1w2][w3] /= total
    elif n == 4:
        for fourgram, count in ngramFreqs.items():
            probs[(fourgram[0], fourgram[1], fourgram[2])][fourgram[3]] += count

        for w1w2w3 in probs:
            total = float(sum(probs[w1w2w3].values()))
            for w4 in probs[w1w2w3]:
                probs[w1w2w3][w4] /= total
    elif n == 5:
        for fivegram, count in ngramFreqs.items():
            probs[(fivegram[0], fivegram[1], fivegram[2], fivegram[3])][fivegram[4]] += count

        for w1w2w3w4 in probs:
            total = float(sum(probs[w1w2w3w4].values()))
            for w5 in probs[w1w2w3w4]:
                probs[w1w2w3w4][w5] /= total
    else:
        sys.stderr.write("ERROR: n not valid")
        raise Exception("n not valid")

    return probs


def main():

    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('input', metavar='File name', help='A text file')
    parser.add_argument('-n', metavar='n-grams', help='The n in n-grams', default=2, type=int, choices=range(2, 6))
    parser.add_argument('-c', metavar='common', help='The most c common ngrams', default=10, type=int)
    parser.add_argument('-p', metavar='probs', help='Calculate ngram probabilities', default=False, choices=["True"])
    parser.add_argument('--predict', metavar='predict', help='Input the string to predict the next word of', default=False)
    parser.add_argument('--generate', metavar='generate', help='Generate a sentence of length n based on input', default=0, type=int)
    parser.add_argument('--seed', metavar='seed', help='Text seed for generating text', default=False)
    args = parser.parse_args()

    fileInput = args.input
    n = args.n
    c = args.c
    predict = args.predict
    getProbs = bool(args.p)
    genText = args.generate
    seed = args.seed
    nGramLookUp = {2: "bigram", 3: "trigram", 4: "4-gram", 5: "5-gram"}

    if predict is not False:
        predict = predict.split()
        predictLen = len(predict)

        if predictLen > 1:
            predict = tuple(predict)
        else:
            predict = "".join(predict)

        if predictLen < n - 1:
            sys.stdout.write(f"WARNING: Calculating {nGramLookUp[n]}s but given string to predict is only {predictLen} word(s) long. Ignoring.\n")
            predict = False
        elif predictLen > n - 1:
            sys.stdout.write(f"WARNING: Calculating {nGramLookUp[n]}s but given string to predict is {predictLen - (n - 1)} word(s) longer than expected. Ignoring.\n")
            predict = False

    with open(fileInput, "r") as textfile:
        text = textfile.read()

    punctRegex = "[();:.,\'\"?\/\\!”“—-]"
    textNoPunct = re.sub(punctRegex, "", text)

    tokens = textNoPunct.lower().split()
    ngramGen = ngrams(tokens, n)
    ngramFreqs = Counter(ngramGen)
    topNgrams = ngramFreqs.most_common(c)

    sys.stdout.write(f"Top {c} most common {nGramLookUp[n]}s:\n")
    for i in range(c):
        if i < len(topNgrams):
            sys.stdout.write(str(i + 1) + ": " + str(topNgrams[i]) + "\n")
        else:
            sys.stdout.write(f"Maximum number of {nGramLookUp[n]}s reached!\n")
            break

    if getProbs or predict or genText:
        probs = calcProbs(ngramFreqs, n)

        if predict is not False:
            if predictLen == 1:
                predictStr = '"' + predict + " ___" + '"'
            else:
                predictStr = '"' + " ".join(predict) + " ___" + '"'

            sys.stdout.write(f"\nPredicting next in sequence: {predictStr}\n")
            predictions = dict(probs[predict])

            for key, value in predictions.items():
                sys.stdout.write(f"{key}: {value}\n")

    if genText and seed is not False:
        sys.stdout.write(f"{generateText(probs, genText, nGramLookUp[n], n, seed)}\n")
    elif seed is False and genText is not 0:
        sys.stdout.write("No seed text provided, text generation abandoned.\n")


if __name__ == '__main__':
    main()
