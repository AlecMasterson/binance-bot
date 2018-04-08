import numpy as np


class RandomWalk:
    """Random walk data generator
    """

    def __init__(self, val=100.0, bias=0.0):
        self.val, self.bias = val, bias

    def __next__(self):
        self.val += np.random.standard_normal() + self.bias
        return self.val

    def __iter__(self):
        return self
