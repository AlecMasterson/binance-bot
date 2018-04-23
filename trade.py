from binance.client import Client
from binance.enums import *
import sys, glob, pandas
import utilities, get_history

def buy(assets, coinpair, price, quantity, fee):
    dest = coinpair[:-3]

    source: trading.iloc[-1][source] - round_down(trading.iloc[-1][source] * quantity),
    dest: trading.iloc[-1][dest] + round_down(trading.iloc[-1][source] * quantity) / price * (1.0 - fee)

def sell(assets, coinpair, price, quantity, fee):


if __name__ == "__main__":

    # Command Usage Verification
    if len(sys.argv) != 2: utilities.throw_error('Command Usage -> \'python3 trade.py [data_directory]\'', True)

    # Connect to the Binance API using our public and secret keys.
    try:
        client = Client('lfeDDamF6ckP7A2uWrd7uJ5nV0aJedQwD2H0HGujNuxmGgtyQQt0kL3lS6UFlRLS', 'phpomS4lCMKuIxF0BgrP4d5N9rEPzf8Dy4ZRVjJ0XeO4Wn7PmOC7uhYsyypi9gFJ')
    except:
        utilities.throw_error('Could Not Connect to Binance API', True)

    # Only use the directory given as an argument.
    locations = [location for location in utilities.DIRS_INTERVALS if location['dir'] == sys.argv[1]]

    # Update all historical data.
    if not get_history.execute(locations):
        utilities.throw_error('Failed to Update All Historical Data', True)

    # Populate with all used assets and their current balance in our account.
    try:
        assets = []
        for balance in client.get_account()['balances']:
            if balance['asset'] in utilities.ASSETS: assets.append({'asset': balance['asset'], 'val': balance['free']})
    except:
        utilities.throw_error('Failed to Get Asset Balances', True)

    # Get the combined price-data file for all used coinpairs. This should never fail as get_history handles it.
    try:
        data = pandas.read_csv(sys.argv[1] + 'ALL.csv')
    except:
        utilities.throw_error('Data File \'ALL.csv\' Not Found in ' + sys.argv[1], True)

    macds = {}
    sources = [0, 0]
    for coinpair in utilities.COINPAIRS:
        if not coinpair.startswith('BTC') and not coinpair.startswith('ETH'): trading[coinpair] = np.array([0.0])
        if coinpair.endswith('BTC'): sources[0] += 1
        else: sources[1] += 1

        macd, macdsignal, macdhist = talib.MACDFIX(np.array(data['close-' + coinpair]), signalperiod=9)
        macds[coinpair] = macd

    peaks = {}
    bought = False
    for index, row in data.iterrows():
        if index == 0: continue

        for coinpair in coinpairs:
            macd = macds[coinpair]

            if coinpair.endswith('BTC'): quantity = 1.0 / sources[0]
            else: quantity = 1.0 / sources[1]

            if not coinpair in peaks or math.isnan(peaks[coinpair]):
                peaks[coinpair] = macd[index - 1]

            elif macd[index - 1] > 0 and (peaks[coinpair] < 0 or peaks[coinpair] < macd[index - 1]):
                peaks[coinpair] = macd[index - 1]

            elif macd[index - 1] < 0 and (peaks[coinpair] > 0 or peaks[coinpair] > macd[index - 1]):
                peaks[coinpair] = macd[index - 1]

            elif peaks[coinpair] > 0 and macd[index - 1] < params['cut'] * peaks[coinpair]:
                buy(assets, conpair, row['open-'+coinpair], quantity, 0.001)

            elif peaks[coinpair] < 0 and macd[index - 1] > params['cut'] * peaks[coinpair]:
                sell(assets, conpair, row['open-'+coinpair], quantity, 0.001)
                del peaks[coinpair]