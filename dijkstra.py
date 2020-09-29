#!/usr/bin/env python3

'''
-- dijkstra - implementation of Dijkstra's shortest path algorithm
-- dijkstraBidrectional - implementation of Dijkstra's shortest path algorithm, uses bidirectional search to speed up
'''

from collections import defaultdict
import heapq


def dijkstra(graph, nodes):

    # intialize shortestPath dict 
    shortestPath = {}
    for node in nodes:
        shortestPath[node] = float("inf")

    # since first node is counted, set to 1
    shortestPath[(0, 0)] = 1

    # generate visited and unvisited, and turn unvisited into heap to pop out min dist
    visited = set([])
    unvisited = [(shortestPath[node], node) for node in nodes]
    heapq.heapify(unvisited)

    while unvisited:
        current = heapq.heappop(unvisited)[1]
        currentPath = shortestPath[current]
        visited.add(current)

        for neighbour in graph[current]:
            if shortestPath[neighbour] > currentPath:
                shortestPath[neighbour] = currentPath + 1
        
        # update heap with new distances
        unvisited = [(shortestPath[node], node) for node in nodes if node not in visited]
        heapq.heapify(unvisited)

    return shortestPath


def dijkstraBidirectional(graph, nodes, endPoint):

    # intialize shortestPath dict 
    shortestPath = {}
    for node in nodes:
        shortestPath[node] = float("inf")

    # create copies to serve as heaps
    fShortestPath = shortestPath
    bShortestPath = shortestPath.copy()

    # since first node is counted, set both to 1
    fShortestPath[(0, 0)] = 1
    bShortestPath[endPoint] = 1

    # generate forward and backwards versions of visited and unvisited, and turn unvisited into heap to pop out min dist
    fVisited = set([])
    bVisited = set([])
    fUnvisited = [(fShortestPath[node], node) for node in nodes]
    bUnvisited = [(bShortestPath[node], node) for node in nodes]
    heapq.heapify(fUnvisited)
    heapq.heapify(bUnvisited)

    while True:
            # run forwards step
            fCurrent = heapq.heappop(fUnvisited)[1]
        
            #check if paths overlap, terminate search if found
            if fCurrent in bVisited:
                return fShortestPath[fCurrent] +  bShortestPath[fCurrent], fShortestPath, bShortestPath

            fCurrentPath = fShortestPath[fCurrent]
            fVisited.add(fCurrent)

            # check and update distances if shorter path present, weight is always 1
            for neighbour in graph[fCurrent]:
                if fShortestPath[neighbour] > fCurrentPath:
                    fShortestPath[neighbour] = fCurrentPath + 1
        
            # update heap with new distances
            fUnvisited = [(fShortestPath[node], node) for node in nodes if node not in fVisited]
            heapq.heapify(fUnvisited)

            # run backwards step
            bCurrent = heapq.heappop(bUnvisited)[1]
        
            #check if paths overlap, terminate search if found
            if bCurrent in fVisited:
                return fShortestPath[bCurrent] + bShortestPath[bCurrent], fShortestPath, bShortestPath

            bCurrentPath = bShortestPath[bCurrent]
            bVisited.add(bCurrent)

            # check and update distances if shorter path present, weight is always 1
            for neighbour in graph[bCurrent]:
                if bShortestPath[neighbour] > bCurrentPath:
                    bShortestPath[neighbour] = bCurrentPath + 1
        
            # update heap with new distances
            bUnvisited = [(bShortestPath[node], node) for node in nodes if node not in bVisited]
            heapq.heapify(bUnvisited)



