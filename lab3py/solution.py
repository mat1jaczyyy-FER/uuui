#!/usr/bin/env python3
# Dominik Matijaca 0036524568

from __future__ import annotations
from sys import argv
from collections import Counter, namedtuple
from math import log2, inf

BaseEntropy = namedtuple("Entropy", ['S', 'e', 'n'])
class Entropy(BaseEntropy):
    def best(self):
        return min(self.S, key=lambda x: [-self.S[x], x])

Gain = namedtuple("Gain", ['g', 'nodes'])

class Node:
    def __init__(self, dataset: Dataset, used_cols: set = set(), level: int = 0):
        self.dataset = dataset
        self.entropy = dataset.entropy()
        self.used_cols = used_cols
        self.level = level

        self.col = None
        self.nodes = {}
    
    def dead(self):
        return len(self.entropy.S) <= 1 or self.level >= DEPTH
    
    def expand(self):
        if self.dead(): return
        
        G = {i: self.dataset.gain(i, self) for i in range(len(self.dataset.header) - 1) if i not in self.used_cols}        
        #print('  '.join(f"IG({self.dataset.header[i]})={v.g:.4f}" for i, v in sorted(G.items(), key=lambda x: x[1].g, reverse=True)))
        
        self.col = min(G, key=lambda x: [-G[x].g, self.dataset.header[x]])
        self.nodes = G[self.col].nodes

        for n in self.nodes.values():
            n.expand()
    
    def predict(self, case: list[str]):
        if not self.dead():
            v = case[self.col]

            if v in self.nodes:
                return self.nodes[v].predict(case)

        return self.entropy.best()

    def branches(self, path: list[str] = []):
        if self.dead():
            yield f"{' '.join(path)} {self.entropy.best()}"
            return

        for i, n in self.nodes.items():
            path.append(f"{self.level + 1}:{self.dataset.header[self.col]}={i}")
            yield from n.branches(path)
            path.pop()

class Dataset:
    def __init__(self, header: list[str], table: list[list[str]]):
        self.header = header
        self.table = table

    @staticmethod
    def from_file(path: str):
        with open(path, "r", encoding = "utf8") as f:
            table = [[j.strip() for j in i.strip().split(",")] for i in f.readlines()]

        return Dataset(table[0], table[1:])

    def column(self, i: int):
        return [j[i] for j in self.table]

    def where(self, i: int, v: str):
        return Dataset(self.header, [j for j in self.table if j[i] == v])

    def entropy(self):
        S = Counter(self.column(-1))
        n = len(self.table)
        return Entropy(S, -sum(s / n * log2(s / n) for s in S.values()), n)
    
    def gain(self, i: int, parent: Node):
        nodes = {v: Node(self.where(i, v), parent.used_cols.copy() | {i}, parent.level + 1) for v in set(self.column(i))}
        return Gain(parent.entropy.e - sum(n.entropy.n / parent.entropy.n * n.entropy.e for n in nodes.values()), nodes)

class ID3:
    def fit(self, csv: Dataset):
        self.root = Node(csv)
        self.root.expand()

        print("[BRANCHES]:")
        print('\n'.join(self.root.branches()))

    def predict(self, csv: Dataset):
        predictions = [self.root.predict(i) for i in csv.table]
        accuracy = sum(i == j for i, j in zip(predictions, csv.column(-1))) / len(csv.table)

        print(f"[PREDICTIONS]: {' '.join(predictions)}")
        print(f"[ACCURACY]: {accuracy:.5f}")

        targets = sorted(set(self.root.dataset.column(-1)))
        results = list(zip(csv.column(-1), predictions))

        print("[CONFUSION_MATRIX]:")
        print('\n'.join(' '.join(str(results.count((row, col))) for col in targets) for row in targets))

FITTING = Dataset.from_file(argv[1])
PREDICTING = Dataset.from_file(argv[2])
DEPTH = int(argv[3]) if len(argv) > 3 else inf

model = ID3()
model.fit(FITTING)
model.predict(PREDICTING)
