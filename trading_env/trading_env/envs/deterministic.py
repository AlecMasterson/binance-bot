import numpy as np


class SineSignal():
    """Modulated sine generator
    """
    @staticmethod
    def _generator(period_1, period_2, epsilon, bias=0.0):
        i = 0
        while True:
            i += 1
            val = (1 - epsilon) * np.sin(2 * i * np.pi / period_1) + \
                epsilon * np.sin(2 * i * np.pi / period_2) + (bias * i)
            yield val
