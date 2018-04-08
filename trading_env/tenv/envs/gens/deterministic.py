import numpy as np


class SineSignal():
    """Modulated sine generator
    """

    def __init__(period_1, period_2, epsilon, bias=0.0):
        self.period_1, self.period_2, self.epsilon, self.bias = period_1, period_2, epsilon, bias
        self.i = 0

    def __next__(self):
        val = (1 - self.epsilon) * np.sin(2 * i * np.pi / self.period_1) + self.epsilon * np.sin(2 * i * np.pi / self.period_2) + (self.bias * self.i)
        self.i += 1
        return val

    def __iter__(self):
        return self
