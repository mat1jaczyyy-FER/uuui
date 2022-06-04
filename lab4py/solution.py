#!/usr/bin/env python3
# Dominik Matijaca 0036524568

from __future__ import annotations
from sys import argv
import numpy as np

def simplearg(flag: str):
    return argv[argv.index(flag) + 1] if flag in argv else None

def filearg(flag: str):
    with open(simplearg(flag), "r", encoding = "utf8") as f:
        return [[float(j.strip()) for j in i.strip().split(",")] for i in f.readlines()[1:]]

def ndarray_combine(a: np.ndarray, b: np.ndarray):
    mean = (a + b) / 2
    return np.where(np.random.uniform(size=mean.shape) < P, mean + np.random.normal(0, K, mean.shape), mean)

class Transform():
    def combine(self, other: Transform):
        return self

    def forward(self, input: np.ndarray):
        raise Exception("Not implemented")

class MatrixTransform(Transform):
    def __init__(self, w: np.ndarray, b: np.ndarray):
        self.W = w; self.B = b

    @staticmethod
    def from_size(input: int, output: int):
        return MatrixTransform(np.random.normal(0, 0.01, (input, output)), np.random.normal(0, 0.01, output))
        
    def combine(self, other: MatrixTransform):
        return MatrixTransform(ndarray_combine(self.W, other.W), ndarray_combine(self.B, other.B))

    def forward(self, input: np.ndarray):
        return np.dot(input, self.W) + self.B
    
class SigmoidTransform(Transform):
    def forward(self, input: np.ndarray):
        return 1 / (1 + np.exp(-input))

class NeuralNet:    
    def __init__(self, t: list[Transform]):
        self.transforms = t
        self.fitness = 1 / self.mse(TRAIN)

    @staticmethod
    def from_config(config: list, size: int):
        t = []
        for c in config:
            if isinstance(c, int):
                t.append(MatrixTransform.from_size(size, c))
                size = c
            else:
                t.append(SigmoidTransform())
        return NeuralNet(t)

    def mse(self, data: list[list[float]]):
        return sum((i[-1] - self.predict(i[:-1])) ** 2 for i in data) / len(data)

    def predict(self, l: list[float]):
        l = np.array(l)
        for t in self.transforms:
            l = t.forward(l)
        return l[0]
    
    def combine(self, other: NeuralNet):
        return NeuralNet([i.combine(j) for i, j in zip(self.transforms, other.transforms)])

TRAIN = filearg("--train")
TEST = filearg("--test")
NN = {
    '5s': [5, 's', 1],
    '20s': [20, 's', 1],
    '5s5s': [5, 's', 5, 's', 1]
}[simplearg("--nn")]
POPSIZE = int(simplearg("--popsize"))
ELITISM = int(simplearg("--elitism"))
P = float(simplearg("--p"))
K = float(simplearg("--K"))
ITER = int(simplearg("--iter"))

def genetic():
    prev = [NeuralNet.from_config(NN, len(TRAIN[0]) - 1) for _ in range(POPSIZE)]

    for iter in range(1, ITER + 1):
        prev.sort(key=lambda x: -x.fitness)
        
        if iter % 2000 == 0: print(f"[Train error @{iter}]: {1 / prev[0].fitness:.6f}")
        if iter == ITER: return prev[0]

        wheel = np.array([i.fitness for i in prev]) / sum([i.fitness for i in prev])
        curr = [p1.combine(p2) for p1, p2 in [np.random.choice(prev, 2, replace=False, p=wheel) for _ in range(POPSIZE - ELITISM)]]
        prev = prev[:ELITISM]
        prev.extend(curr)

print(f"[Test error]: {genetic().mse(TEST):.6f}")
