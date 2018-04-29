import csv


class CSVStreamer():
    """Data generator from csv file.
    The csv file should no index columns.

    Args:
        filename (str): Filepath to a csv file.
        header (bool): True if the file has got a header, False otherwise
    """

    def __init__(self, filename, header=False):
        self.filename = filename
        self.csvfile = open(filename, "r")
        self.csv = csv.DictReader(self.csvfile)

    def rewind(self):
        return self.__init__(self.filename)

    def next(self):
        return next(self.csv)
