import numpy as np


class RandomWalk:
    """Random walk data generator
    """

    def __init__(self, val=100.0, multiplier=1, bias=0.0):
        self.val, self.multiplier, self.bias = val, multiplier, bias

    def __next__(self):
        self.val += np.random.standard_normal() * self.multiplier + self.bias
        return self.val

    def __iter__(self):
        return self

    def rewind(self):
        return self

    def next(self):
        return self.__next__()
