#!/usr/bin/env python3
# Dominik Matijaca 0036524568

from sys import argv
from collections import deque
from queue import PriorityQueue

def weight(a, b):
    return GRAPH[a][b] if a is not None else 0

def bfs(s):
    v = set()
    p = {None: [[], 0]}
    q = deque([[s, None]])

    while len(q):
        c, l = q.popleft()

        p[c] = [p[l][0] + [c], p[l][1] + weight(l, c)]

        for nn in NODES[c]:
            if nn in END:
                return [True, len(p), len(p[c][0]) + 1, p[c][1] + weight(c, nn), p[c][0] + [nn]]
    
            if nn not in v:
                q.append([nn, c])
                v.add(nn)

    return [False]

def ucs(s):
    p = {None: [[], 0]}
    q = PriorityQueue()
    q.put([0, s, None])

    while not q.empty():
        w, c, l = q.get()

        if c in p:
            continue

        p[c] = [p[l][0] + [c], w]

        if c in END:
            return [True, len(p) - 1, len(p[c][0]), p[c][1], p[c][0]]
    
        for nn in NODES[c]:
            if nn not in p.keys():
                q.put([w + weight(c, nn), nn, c])

    return [False]

def astar(s):
    p = {None: [[], 0]}
    q = PriorityQueue()
    q.put([0, s, 0, None])

    while not q.empty():
        _, c, w, l = q.get()

        if c in p and w >= p[c][1]:
            continue

        p[c] = [p[l][0] + [c], w]

        if c in END:
            return [True, len(p) - 1, len(p[c][0]), p[c][1], p[c][0]]
    
        for nn in GRAPH[c]:
            nw = w + weight(c, nn)
            q.put([nw + HEURISTIC[nn], nn, nw, c])

    return [False]

def optimistic(_):
    result = [[], True]

    for i in NODES:
        w = ucs(i)[3]

        result[0].append([HEURISTIC[i] <= w, i, HEURISTIC[i], w])
        result[1] = result[1] and result[0][-1][0]
    
    return result

def consistent(_):
    result = [[], True]

    for i, v in NODES.items():
        for j in v:
            w = weight(i, j)

            result[0].append([HEURISTIC[i] <= HEURISTIC[j] + w, i, j, HEURISTIC[i], HEURISTIC[j], w])
            result[1] = result[1] and result[0][-1][0]
    
    return result

def check(result, format):
    for i in result[0]:
        status = "OK" if i[0] else "ERR"
        print(f"[CONDITION]: [{status}] {format(i[1:])}")
    
    final = "" if result[1] else "not "
    print(f"[CONCLUSION]: Heuristic is {final}{ALG_NAME}.")

def simplearg(flag):
    return argv[argv.index(flag) + 1] if flag in argv else None

def filearg(flag):
    path = simplearg(flag)

    if path is None:
        return [None, None]

    with open(path, "r", encoding = "utf8") as f:
        return [[i.strip() for i in f.readlines() if not i.startswith("#")], path]

CHECK_OPTIMISTIC = "--check-optimistic" in argv
CHECK_CONSISTENT = "--check-consistent" in argv

ALG_NAME = simplearg("--alg")

if CHECK_OPTIMISTIC:
    ALG_NAME = "optimistic"

if CHECK_CONSISTENT:
    ALG_NAME = "consistent"

algos = [bfs, ucs, astar, optimistic, consistent]
ALG = [i.__name__ for i in algos].index(ALG_NAME)

info = ["#", ["BFS", "UCS", "A-STAR", "HEURISTIC-OPTIMISTIC", "HEURISTIC-CONSISTENT"][ALG]]

SS, SSPATH = filearg("--ss")

START = SS[0]
END = SS[1].split()

GRAPH = {}
NODES = {}

for i in SS[2:]:
    n, e = i.split(":")
    GRAPH[n] = {}
    
    for j in e.split():
        nn, w = j.split(",")
        GRAPH[n][nn] = float(w)
    
    NODES[n] = sorted(GRAPH[n])

H, HPATH = filearg("--h")

HEURISTIC = {}

if HPATH is not None:
    info.append(HPATH)

    for i in H:
        n, h = i.split(":")
        HEURISTIC[n] = float(h.strip())

result = algos[ALG](SS[0])

print(" ".join(info))

if CHECK_OPTIMISTIC:
    check(result, lambda i: f"h({i[0]}) <= h*: {i[1]:.1f} <= {i[2]:.1f}")

elif CHECK_CONSISTENT:
    check(result, lambda i: f"h({i[0]}) <= h({i[1]}) + c: {i[2]:.1f} <= {i[3]:.1f} + {i[4]:.1f}")
    
else:
    alg_output = ["FOUND_SOLUTION", "STATES_VISITED", "PATH_LENGTH", "TOTAL_COST", "PATH"]

    for i in range(min(len(alg_output), len(result))):
        if i == 0:
            result[i] = "yes" if result[i] else "no"
        if i == 3:
            result[i] = f"{result[i]:.1f}"
        if i == 4:
            result[i] = " => ".join(result[i])

        print(f"[{alg_output[i]}]: {result[i]}")
