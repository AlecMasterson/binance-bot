from binance.client import Client
from binance.enums import *
import sys, utilities, glob, pandas
import get_history

if __name__ == "__main__":

    # Command Usage Verification
    if len(sys.argv) != 2: utilities.throw_error('Command Usage -> \'python3 trade.py [data_directory]\'', True)

    # Connect to the Binance API using our public and secret keys.
    try:
        client = Client('lfeDDamF6ckP7A2uWrd7uJ5nV0aJedQwD2H0HGujNuxmGgtyQQt0kL3lS6UFlRLS', 'phpomS4lCMKuIxF0BgrP4d5N9rEPzf8Dy4ZRVjJ0XeO4Wn7PmOC7uhYsyypi9gFJ')
    except:
        utilities.throw_error('Could Not Connect to Binance API', True)

    # Update all historical data. Two attempts to update.
    if not get_history.execute():
        if not get_history.execute():
            utilities.throw_error('Failed to Update All Historical Data', True)

    # Populate with all used assets and their current balance in our account.
    try:
        assets = []
        for balance in client.get_account()['balances']:
            if balance['asset'] in utilities.ASSETS: assets.append({'asset': balance['asset'], 'val': balance['free']})
    except:
        utilities.throw_error('Failed to Get Asset Balances', True)

    # Get the combined price-data file for all used coinpairs.
    try:
        data = pandas.read_csv(sys.argv[1] + 'ALL.csv')
    except:
        utilities.throw_error('Data File \'ALL.csv\' Not Found in ' + sys.argv[1], True)
