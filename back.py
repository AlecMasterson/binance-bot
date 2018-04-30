import numpy as np
import matplotlib.pyplot as plt
import sys, pandas, talib, math, glob, utilities


# Round down x to the nearest 0.001 (Binance Trade Minimum)
# x - The number to round down
def round_down(x):
    return float(math.floor(x * 1000) / 1000)


# Return the normalized number used for plotting
# min - Minimum value of the series
# max - Maximum value of the series
# num - The number to be normalized
def normalize(min, max, num):
    return (num - min) / (max - min)


# Convert a time from milliseconds to a pandas DateTime
# time - The time in milliseconds
def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


# A simple function for plotting a point
# x - The x-coordinate to plot, in milliseconds
# y - The y-coordinate to plot
def plot_point(x, y, color):
    plt.scatter(to_datetime(x), y, color=color)


# Return the primary asset of the coinpair
# i.e. Return 'BTC' from the 'ETHBTC' coinpair
def get_source(pair):
    return pair[-3:]


# Return the secondary asset of the coinpair
# i.e. Return 'ETH' from the 'ETHBTC' coinpair
def get_asset(pair):
    return pair[:-3]


# data - All price-data used for testing
# balances - A dictionary of asset balances
def get_total_balance(data, balances):
    btc = balances['BTC']
    for balance in balances:
        if balance != 'BTC':
            pair = balance + 'BTC'
            btc += data.iloc[-1]['close-' + pair] * balances[balance]
    return btc


# Creates a new open position. This is used when making a buy trade
# open - True if the position is still open, has not yet been sold
# time - The time in milliseconds of the start of the position
# age - How long the position has been open, in milliseconds
# pair - The coinpair this position belongs to
# amount - How much of the secondary asset was bought for this position
# price - The price at which the trade was made
# current - The current price of the coinpair
# fee -  Total amount lost to fees in terms of the secondary asset
# result - The percentage profit/loss on this position based on the current price and fees
# peak - Used for stop-loss functionality
# stop-loss: True if the stop-loss threshold has been triggered
def create_position(time, pair, amount, price, fee):
    return {'open': True, 'time': time, 'age': 0.0, 'pair': pair, 'amount': amount, 'price': price, 'current': price, 'fee': fee, 'result': 0.0, 'peak': 0.0, 'stop-loss': False}


# Update a position with the current price
# position - The position to update
# time - The current time, in milliseconds, for calculating the position age
# current - The current price of the position's coinpair
# arm - The percent increase needed to arm the stop-loss trigger
def update_position(position, time, current, arm):
    position['age'] = time - position['time']
    position['current'] = current
    position['result'] = (position['amount'] * position['current']) / (position['amount'] * position['price'])
    if position['result'] > position['peak']: position['peak'] = position['result']
    if position['peak'] > arm: position['stop-loss'] = True


# Return all positions associated with a coinpair
# positions - The list of all positions, opened or closed
# pair - the coinpair we're looking for
def get_positions(positions, pair):
    getting = []
    for position in positions:
        if position['pair'] == pair: getting.append(position)
    return getting


def buy(balances, positions, time, pair, quantity, price, dataMinMax):
    using = round_down(balances[get_source(pair)] * quantity)
    if using > 0.0:
        totalFee = using / price * 0.001
        total = using / price - totalFee

        positions.append(create_position(time, pair, total, price, totalFee))

        balances[get_source(pair)] -= using
        balances[get_asset(pair)] += total

        plot_point(time, normalize(dataMinMax[0], dataMinMax[1], price), 'red')


def sell(balances, position, time, dataMinMax):
    using = round_down(position['amount'])
    if using > 0.0:
        totalFee = using * position['current'] * 0.001
        total = using * position['current'] - totalFee

        position['open'] = False
        position['fee'] += totalFee

        balances[get_source(position['pair'])] += total
        balances[get_asset(position['pair'])] -= using

        plot_point(time, normalize(dataMinMax[0], dataMinMax[1], position['current']), 'green')


def get_min(macds):
    min = 0
    for i in macds:
        if i < min: min = i
    return min


def get_max(macds):
    max = 0
    for i in macds:
        if i > max: max = i
    return max


# The main backtesting function, where the magic happens
# data - All price-data used for testing
# balances - A dictionary of asset balances
# pairs - A list of coinpairs being used
# params - A dictionary of optional parameters used for optimization
def backtest(data, balances, pairs, params):

    # Overhead dictionaries that will contain the MACD and MACD-Signal for the coinpairs.
    macds = {}
    signals = {}

    # Overhead dictionaries that will contain the upper/lower bollinger bands for the coinpairs.
    bbandsUpper = {}
    bbandsLower = {}

    # Plotting dictionary.
    dataMinMaxs = {}

    # Run our overhead code on all the coinpairs before running through the price-data.
    for pair in pairs:

        # If our balances dictionary doesn't contain an asset, add it.
        if not get_asset(pair) in balances: balances[get_asset(pair)] = 0.0

        # INFO: During talib calculation, we must multiply by 1e6. Extremely small numbers (prices) break talib.

        # Populate the MACD and MACD-Signal dictionaries with the current coinpair's info.
        macd, macdsignal, macdhist = talib.MACDFIX(np.array(data['close-' + pair] * 1e6), signalperiod=9)
        macds[pair] = macd / 1e6
        signals[pair] = macdsignal / 1e6

        # Populate the upper/lower bollinger band dictionaries with the current coinpair's info.
        upperband, middleband, lowerband = talib.BBANDS(np.array(data['close-' + pair] * 1e6), timeperiod=14, nbdevup=2, nbdevdn=2, matype=0)
        bbandsUpper[pair] = upperband / 1e6
        bbandsLower[pair] = lowerband / 1e6

        # Get all price-data as a pandas.DateTime for plotting.
        plotDataTime = to_datetime(data['Open Time'])

        # Plot the normalized price-data.
        dataMinMaxs[pair] = [min(data['open-' + pair]), max(data['open-' + pair])]
        plt.plot(plotDataTime, normalize(dataMinMaxs[pair][0], dataMinMaxs[pair][1], data['open-' + pair]))

        # Only plot the normalized info if we're testing one coinpair, otherwise it gets too cluttered.
        if len(pairs) == 1:
            plt.plot(plotDataTime, normalize(dataMinMaxs[pair][0], dataMinMaxs[pair][1], data['low-' + pair]), label='low')

            minmax = [get_min(macd), get_max(macd)]
            plt.plot(plotDataTime, normalize(minmax[0], minmax[1], macd), label='macd')
            plt.plot(plotDataTime, np.array([normalize(minmax[0], minmax[1], 0.0) for i in range(len(data))]))

            plt.plot(plotDataTime, normalize(dataMinMaxs[pair][0], dataMinMaxs[pair][1], bbandsUpper[pair]), linestyle='dashed', label='upperband')
            plt.plot(plotDataTime, normalize(dataMinMaxs[pair][0], dataMinMaxs[pair][1], bbandsLower[pair]), linestyle='dashed', label='lowerband')

    # Reset all positions and open orders to an empty list or dictionary.
    positions = []
    orders = {}

    # All coinpairs open orders start as an empty list, no orders.
    for pair in pairs:
        orders[pair] = []

    # The long as fuck iterative traverse of all price-data. All backtesting trades are done here.
    for index, row in data.iterrows():

        # Skip the section in February where Binance was missing data, plus a buffer after.
        # Skip the first 3 time entries to provide past data that we can make decisions on.
        if row['Open Time'] > 1517961600000 and row['Open Time'] < 1518307200000: continue
        if index < 3: continue

        # For each time entry, check all coinpairs for a potential buy/sell trade.
        for pair in pairs:

            # Skip unusual anomolies where we have a horizontal (stair stepping) trend.
            if row['open-' + pair] == data.iloc[index - 1]['open-' + pair]: continue

            # Load in the coinpair's MACD, MACD-Signal, and bollinger bands.
            macd = macds[pair]
            signal = signals[pair]
            upperband = bbandsUpper[pair]
            lowerband = bbandsLower[pair]

            # Check all open orders for a potential purchase or if an order needs to be cancelled.
            for order in orders[pair]:
                # If the order was opened within the past hour, attempt a buy, else cancel the order.
                if row['Open Time'] - order['time'] <= 36e5:
                    # If the asking price fell within the high/low of the last time entry, complete the buy order.
                    if order['price'] < data.iloc[index - 1]['high-' + pair] and order['price'] > data.iloc[index - 1]['low-' + pair]:
                        # TODO: Determine function for calculating percent of total BTC you want to use to buy.
                        # TODO: Replace row['Open Time'] with a more precise time of the purchase.
                        buy(balances, positions, row['Open Time'], pair, 1.0, order['price'], dataMinMaxs[pair])
                else:
                    orders[pair].remove(order)

            # Hold the position if the MACD is above zero and increasing.
            if macd[index - 1] > macd[index - 2] and macd[index - 2] > 0: status = 'hold'
            else: status = ''

            # For all positions, if they're open then update it.
            for position in get_positions(positions, pair):
                if position['open']:
                    update_position(position, row['Open Time'], row['open-' + pair], params['arm'])

                    # If not told to hold the position and the stop limit has been reached, sell the position.
                    # If the age of the position is too old and the % result has dropped too low, sell the position.
                    if not status == 'hold' and position['stop-loss']:
                        sell(balances, position, row['Open Time'], dataMinMaxs[pair])
                    elif position['age'] > 108e5 and position['result'] < params['drop']:
                        sell(balances, position, row['Open Time'], dataMinMaxs[pair])

            # If the previous time entry's lowest price was below the previous time entry's lower bollinger band, then create a buy order.
            # TODO: This couldn't be more simple. Clearly room to grow.
            if data.iloc[index - 1]['low-' + pair] < lowerband[index - 1]: orders[pair].append({'time': row['Open Time'], 'price': row['open-' + pair] * 0.993})

    # Return the final balances and all positions used, opened or closed
    return balances, positions


# A separate function for optimization so we only return the final total balance
# data - All price-data used for testing
# balances - A dictionary of asset balances
# pairs - A list of coinpairs being used
# params - A dictionary of optional parameters used for optimization
def optimize(data, balances, pairs, params):
    balances, positions = backtest(data, balances, pairs, params)
    return get_total_balance(data, balances)


if __name__ == "__main__":

    # Verify command usage before executing.
    if len(sys.argv) < 2: utilities.throw_error('Command Usage -> \'python3 back.py [price-data directory]\'', True)

    # Set the default plotting window size so it isn't tini tiny.
    fig = plt.figure(figsize=(13, 7))

    # Get all the coinpairs being used for the given time interval.
    pairs = []
    for file in glob.glob(sys.argv[1].split('/')[0] + '/*.csv'):
        pair = file.split('/')[1].split('.')[0]
        if pair == 'ALL': data = pandas.read_csv(file)
        elif pair != 'BNBBTC': pairs.append(pair)

    # Verify that all coinpairs were loaded correctly.
    # Comment out if only testing one coinpair.
    '''if len(pairs) != len(glob.glob(sys.argv[1].split('/')[0] + '/*.csv')) - 1 or len(pairs) != len(utilities.COINPAIRS):
        utilities.throw_error('Not all coinpairs loaded. Some history may be missing.', True)'''

    # Run the backtesting function, getting the necessary information returned.
    balances, positions = backtest(data, {'BTC': 1.0}, pairs, {'arm': 1.01, 'stop': 0.999, 'drop': 0.985})

    # I used this for debugging...
    '''for pos in positions:
        print(pos['pair'] + '\t' + str(pos['time']) + '\t' + str(pos['time'] + pos['age']) + '\t' +
              str(pos['amount']) + '\t' + str(pos['price']) + '\t' + str(pos['current']) + '\t ' + str(pos['result']))'''

    print('INFO: Finished with ' + str(get_total_balance(data, balances)) + ' BTC from 1 BTC')

    # If the '-p' argument was provided, show the plotting.
    if '-p' in sys.argv:
        plt.legend()
        plt.show()
