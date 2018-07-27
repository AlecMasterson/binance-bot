import pandas, sys, os
from binance.client import Client

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def connect_binance():
    try:
        return Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        print('Failed to Connect to the Binance API')


def to_csv(file, data):
    try:
        pandas.DataFrame().to_csv(file)
    except:
        print('Failed to Write to File \'' + file + '\'')


def read_csv(file, create):
    try:
        return pandas.read_csv(file)
    except FileNotFoundError:
        print('Failed to Find File \'' + file + '\'')
        if create: pandas_to_csv(file)
    except:
        print('Failed to Read File \'' + file + '\'')
