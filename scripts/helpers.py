import pandas, sys, os
from binance.client import Client

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def connect_binance():
    try:
        return Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        print('Failed to Connect to the Binance API')
        return None


def to_csv(file, structure, data):
    try:
        if data is None: data = pandas.DataFrame(columns=structure)
        data.to_csv(file)
        return data
    except:
        print('Failed to Write to File \'' + file + '\'')
        return None


def read_csv(file, structure):
    try:
        return pandas.read_csv(file)
    except FileNotFoundError:
        print('Failed to Find File \'' + file + '\'')
        return to_csv(file, structure, None)
    except:
        print('Failed to Read File \'' + file + '\'')
        return None
