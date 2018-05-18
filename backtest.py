from binance.client import Client

from live.Coinpair import Coinpair
from live.Position import Position

import matplotlib.pyplot as plt
import sys, pandas, utilities


# Convert a time from milliseconds to a pandas.DateTime object
# time - The time in milliseconds
def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


# A simple function for plotting a point
# x - The x-coordinate to plot, in milliseconds
# y - The y-coordinate to plot
# color - The desired color of the point
def plot_point(x, y, color):
    plt.scatter(to_datetime(x), y, color=color)


# The main backtesting function, where the magic happens
# coinpair - The coinpair being backtested
# data - All histrorical data
# balances - A dictionary of asset balances
# params - A dictionary of optional parameters used for optimization
def backtest(coinpair, data, balances, params):

    # Convert the historical data 'Open Time' values to a pandas.DateTime series.
    plotTime = []
    for candle in data.data:
        plotTime.append(to_datetime(candle.openTime))

    plt.plot(plotTime, [point.open for point in data.data])

    #plt.plot(plotTime, [point.high for point in data.data], label='high')
    plt.plot(plotTime, [point.low for point in data.data], label='low')
    #plt.plot(plotTime, [upperband for upperband in data.upperband], linestyle='dashed', label='upperband')
    plt.plot(plotTime, [lowerband for lowerband in data.lowerband], linestyle='dashed', label='lowerband')

    plt.plot(plotTime, [macd + 0.00046 for macd in data.macd], label='macd')
    plt.plot(plotTime, [0.00046 for macd in data.macd])

    # Set the default values for our positions list, current position dictionary, and order dictionary.
    positions = []
    curPos = None
    order = None

    # The long as fuck iterative traverse of the historical data.
    # All backtesting trades are done here.
    for index, point in enumerate(data.data):

        # Skip the first 2 time entries to provide past data that we can make decisions on.
        if index < 2: continue

        # Check the open order to see if the desired price fell within the high/low of the last candle.
        if order != None:
            if order['price'] > data.data[index - 1].low and order['price'] < data.data[index - 1].high:

                # Get the order quantity/price depending on the type of order.
                if order['type'] == 'buy': balance = balances['BTC']
                elif order['type'] == 'sell': balance = balances[coinpair[:-3]]

                quantity, price = data.validate_order(order['type'], balance, order['price'])

                # Only proceed if this is a valid order.
                if quantity != -1 and price != -1:
                    if order['type'] == 'buy':
                        curPos = Position(None, order['time'], coinpair, quantity, price)
                        balances['BTC'] -= quantity * price
                        balances[coinpair[:-3]] += quantity
                        plot_point(data.data[index - 1].closeTime, price, 'red')
                    elif order['type'] == 'sell':
                        balances['BTC'] += quantity * price
                        balances[coinpair[:-3]] -= quantity
                        curPos.open = 'False'
                        positions.append(curPos)
                        print('Position Closed at Result: ' + str(curPos.result))
                        curPos = None
                        plot_point(data.data[index - 1].closeTime, price, 'green')

                # Remove the order regardless whether it's a valid order or not.
                order = None

            # If the order took too long, than remove it.
            elif point.openTime - order['time'] > 18e5:
                order = None

        # Only do the rest if there isn't a current order being processed.
        else:

            # If there's a current position open.
            if curPos != None:
                curPos.update(point.openTime, point.open)

                # Hold the position if the MACD is increasing and above zero.
                if data.macd[index - 1] > data.macd[index - 2] and data.macd[index - 2] > 0: status = 'hold'
                else: status = ''

                # If not told to hold the position and the stop limit has been reached, sell the position.
                # If the age of the position is too old and the % result has dropped too low, sell the position.
                if not status == 'hold' and curPos.stopLoss == 'True':
                    order = {'type': 'sell', 'time': point.openTime, 'price': data.data[index - 1].close * 0.998}
                elif float(curPos.age) > 108e5 and float(curPos.result) < 0.96:
                    order = {'type': 'sell', 'time': point.openTime, 'price': data.data[index - 1].close * 0.998}

            else:
                if ((data.macd[index - 1] >= data.macd[index - 2] and data.macd[index] < 0) or data.data[index - 1].open < data.lowerband[index - 1]):
                    order = {'type': 'buy', 'time': point.openTime, 'price': data.data[index - 1].low * 1.002}

    # Return all the positions used, opened or closed.
    return positions


# A separate function for optimization so we only return the final total balance
# data - All histrorical data
# balances - A dictionary of asset balances
# params - A dictionary of optional parameters used for optimization
def optimize(data, balances, params):
    backtest(data, balances, params)
    return 0.0


if __name__ == "__main__":

    # Set the default plotting window size so it isn't tini tiny.
    fig = plt.figure(figsize=(13, 7))

    # Connect to the Binance API using our public and secret keys.
    try:
        client = Client('lfeDDamF6ckP7A2uWrd7uJ5nV0aJedQwD2H0HGujNuxmGgtyQQt0kL3lS6UFlRLS', 'phpomS4lCMKuIxF0BgrP4d5N9rEPzf8Dy4ZRVjJ0XeO4Wn7PmOC7uhYsyypi9gFJ')
    except:
        utilities.throw_error('Failed to Connect to Binance API', True)
    utilities.throw_info('Successfully Finished Connecting to Binance Client')

    # TODO: Set this to utilities.COINPAIRS when no longer testing one coinpair.
    coinpairs = ['ICXBTC']

    # Acquire all necessary historical data from the API for each coinpair.
    data = {}
    try:
        # Instantiate a new Coinpair object for each coinpair.
        for coinpair in coinpairs:
            data[coinpair] = Coinpair(client, coinpair)
    except:
        utilities.throw_error('Failed to Get Historical Data', True)
    utilities.throw_info('Successfully Finished Getting Historical Data')

    # Set the default values for available coin for each asset.
    balances = {'BTC': 1.0}
    for coinpair in coinpairs:
        balances[coinpair[:-3]] = 0.0

    # Run the backtesting function, getting the necessary information returned.
    positions = backtest('ICXBTC', data['ICXBTC'], balances, {'arm': 1.01, 'stop': 1.0, 'drop': 0.99})

    # If the '-p' argument was provided, show the plotting.
    if '-p' in sys.argv:
        plt.legend()
        plt.show()
