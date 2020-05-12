#!/usr/bin/env python3
"""
Summarise a text file based on weighting of sentences
"""

import sys
import re
import numpy as np
import networkx as nx

from argparse import ArgumentParser
from nltk.tokenize import sent_tokenize
from nltk.cluster.util import cosine_distance
from nltk.corpus import stopwords
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
from gensim.summarization.bm25 import BM25


def getSentenceScore(model, tokens, genDict):
    scores = {}
    docScore = 0

    for lineID, line in enumerate(tokens):
        sentenceScore = 0
        lineScore = model[genDict.doc2bow(line)]

        for lineTuple in lineScore:
            sentenceScore += lineTuple[1]
            docScore += lineTuple[1]

        scores[lineID] = sentenceScore

    rankedDict = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}
    avgScore = docScore / len(rankedDict)

    return rankedDict, avgScore


def getBOW(tokens):
    genDict = Dictionary(tokens)
    bow = [genDict.doc2bow(token) for token in tokens]

    return bow, genDict


def bm25Summarise(tokens):
    bow, genDict = getBOW(tokens)
    model = BM25(bow)

    rankedScores = {}
    sumScore = 0
    vectorCount = 0

    for i, vector in enumerate(bow):
        vectorSum = sum(model.get_scores(vector))
        rankedScores[i] = vectorSum
        sumScore += vectorSum
        vectorCount += 1

    avgScore = sumScore / vectorCount

    return rankedScores, avgScore


def tfidfModel(tokens):
    bow, genDict = getBOW(tokens)
    model = TfidfModel(bow)
    rankedScores, avgScore = getSentenceScore(model, tokens, genDict)

    return rankedScores, avgScore


def cosineModel(sentences, langStopWords, topN):
    summary = []

    sentLen = len(sentences)
    simMatrix = np.zeros((sentLen, sentLen))

    for i in range(sentLen):
        for j in range(sentLen):
            if i == j:
                continue
            simMatrix[i][j] = sentenceSim(sentences[i], sentences[j], langStopWords)

    # build graph from matrix and use page rank
    simGraph = nx.from_numpy_array(simMatrix)
    scores = nx.pagerank(simGraph)

    ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    # sys.stdout.write(f"Indexes of top ranked_sentence order are {ranked_sentence}")

    for i in range(topN):
        summary.append(ranked_sentence[i][1])

    return " ".join(summary)


def sentenceSim(sentenceOne, sentenceTwo, langStopWords):
    if langStopWords is None:
        langStopWords = []

    sentenceOne = [w.lower() for w in sentenceOne]
    sentenceTwo = [w.lower() for w in sentenceTwo]

    allWords = list(set(sentenceOne + sentenceTwo))
    vectorOne = [0] * len(allWords)
    vectorTwo = [0] * len(allWords)

    for w in sentenceOne:
        if w in langStopWords:
            continue
        vectorOne[allWords.index(w)] += 1

    for w in sentenceTwo:
        if w in langStopWords:
            continue
        vectorTwo[allWords.index(w)] += 1

    return 1 - cosine_distance(vectorOne, vectorTwo)


def main():
    parser = ArgumentParser(usage=__doc__)
    parser.add_argument('input', metavar='File name', help='A text file')
    parser.add_argument('-n', metavar='Top number of sentences', help='The n amount of sentences you want from the top ranked sentences', type=int, default=1)
    parser.add_argument('--lang', metavar='language setting', help='Stop word language setting', default=None)
    parser.add_argument('--model', metavar='model setting', help='Model setting', default="bm25", choices=["cosine", "tfidf", "bm25"])
    parser.add_argument('--other', metavar='return above average score', help='Returns sentences above average score instead of top n items', default=False, choices=["avg"])
    args = parser.parse_args()

    fileInput = args.input
    topN = args.n
    lang = args.lang
    model = args.model
    aboveAverage = args.other
    byLine = False
    summaryNum = topN

    if aboveAverage == "avg":
        aboveAverage = True

    if lang == "eng":
        langStopWords = stopwords.words('english')
    else:
        langStopWords = None

    with open(fileInput, "r") as textfile:
        text = textfile.readlines()

        punctRegex = "[();:,\'\"?\/\\!”“—-]"
        sentences = []
        sentWithPunct = []
        
        for line in text:
            if line.strip():
                processedLine = re.sub(punctRegex, "", line).lower()
                sentences.extend(sent_tokenize(processedLine))
                sentWithPunct.extend(sent_tokenize(line))

    if topN > len(sentences):
        sys.stderr.write("ERROR: The amount of sentences requested is larger than the amount of sentences in the input!\n")
        raise Exception("More sentences requested than in input")

    if model == "cosine":
        out = cosineModel(sentences, langStopWords, topN)
    elif model == "tfidf":
        tokens = [sentence.lower().split() for sentence in sentences]
        rankedScores, avgScore = tfidfModel(tokens)
        byLine = True
    elif model == "bm25":
        tokens = [sentence.lower().split() for sentence in sentences]
        rankedScores, avgScore = bm25Summarise(tokens)
        byLine = True
    else:
        sys.stderr.write("ERROR: Not a valid model choice.\n")
        raise Exception("Model not recognised")

    if aboveAverage:
        summaryNum = 0
        out = ""
        for key, value in rankedScores.items():
            if value >= avgScore:
                out = out + sentWithPunct[key] + " "
                summaryNum += 1
    elif byLine:
        out = ""
        rankedList = [k for k, v in sorted(rankedScores.items(), key=lambda item: item[1], reverse=True)]

        for i in range(topN):
            out = out + sentWithPunct[rankedList[i]] + " "

    sys.stdout.write(f"Summary:\n{out}\n")
    sys.stdout.write(f"\nOriginal number of sentences = {len(sentWithPunct)}\nNumber of summary sentences = {summaryNum}\nSummary size = {round((summaryNum / len(sentWithPunct)) * 100)}%\n")


if __name__ == '__main__':
    main()
