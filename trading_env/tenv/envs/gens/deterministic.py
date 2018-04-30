import numpy as np


class SineSignal():
    # Depricated
    """Modulated sine generator
    """

    def __init__(self, period_1, period_2, epsilon, bias=0.0):
        print("DON'T USE ME")
        1 / 0
        self.period_1, self.period_2, self.epsilon, self.bias = period_1, period_2, epsilon, bias
        self.i = 0

    def __next__(self):
        val = (1 - self.epsilon) * np.sin(2 * self.i * np.pi / self.period_1) + self.epsilon * np.sin(2 * self.i * np.pi / self.period_2) + (
            self.bias * self.i)
        self.i += 1
        return val

    def __iter__(self):
        return self

    def rewind(self):
        return self

    def next(self):
        return self.__next__()
