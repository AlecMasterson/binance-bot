import numpy as np


class RandomWalk():
    """Random walk data generator
    """

    @staticmethod
    def _generator(bias=0.0):
        """Generator for a pure random walk

        Args:
            bais (float): bias to apple to the random walk (positive is increasing in value)

        Yields:
            int: current price
        """
        val = 0
        while True:
            yield val
            val += np.random.standard_normal() + bias
