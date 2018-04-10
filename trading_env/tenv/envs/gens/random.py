import csv
import numpy as np
import random


class RandomCSV:
    """Reads the csv in a random order
    """

    def __init__(self, filename, header=False):
        random.seed()
        self.filename = filename
        self.csvfile = open(filename, "r")
        self.list = [line for line in csv.DictReader(self.csvfile)]

    def __next__(self):
        # Rewinding automatically would cause a loop that would cause extreme shifts in value
        try:
            return random.choice(self.list)
        except:
            self.rewind()
            return random.choice(self.list)

    def rewind(self):
        return self.__init__(self.filename)

    def next(self):
        return self.__next__()
