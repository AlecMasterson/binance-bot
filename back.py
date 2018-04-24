import numpy as np
import matplotlib.pyplot as plt
import sys, pandas, talib, math, glob, helpers, utilities


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
    position['age'] = time - position['age']
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
    using = helpers.round_down(balances[get_source(pair)] * quantity)
    if using > 0.0:
        totalFee = using / price * 0.001
        total = using / price - totalFee

        positions.append(create_position(time, pair, total, price, totalFee))

        balances[get_source(pair)] -= using
        balances[get_asset(pair)] += total

        plot_point(time, normalize(dataMinMax[0], dataMinMax[1], price), 'red')


def sell(balances, position, time, dataMinMax):
    using = helpers.round_down(position['amount'])
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

    # Run our overhead code on all the coinpairs before running through the price-data.
    for pair in pairs:

        # If our balances dictionary doesn't contain an asset, add it.
        if not get_asset(pair) in balances: balances[get_asset(pair)] = 0.0

        # Get all price-data as a pandas.DateTime for plotting.
        plotDataTime = to_datetime(data['Open Time'])

        # Plot the normalized price-data.
        dataMinMax = [min(data['open-' + pair]), max(data['open-' + pair])]
        plt.plot(plotDataTime, normalize(dataMinMax[0], dataMinMax[1], data['open-' + pair]))

        # Populate the MACD and MACD-Signal dictionary with the current coinpair's info.
        macd, macdsignal, macdhist = talib.MACDFIX(np.array(data['close-' + pair]), signalperiod=9)
        macds[pair] = macd
        signals[pair] = macdsignal

        # Only plot the normalized MACD if we're testing one coinpair, otherwise it gets to cluttered.
        if len(pairs) == 1:
            minmax = [get_min(macd), get_max(macd)]
            plt.plot(plotDataTime, normalize(minmax[0], minmax[1], macd), label='macd')
            plt.plot(plotDataTime, np.array([normalize(minmax[0], minmax[1], 0.0) for i in range(len(data))]))

            #minmax = [get_min(macdsignal), get_max(macdsignal)]
            plt.plot(plotDataTime, normalize(minmax[0], minmax[1], macdsignal), label='signal')

    # Reset all positions to an empty list, none.
    positions = []

    for index, row in data.iterrows():
        if index < 3: continue

        # For each time entry, check all coinpairs for a potential buy/sell trade.
        for pair in pairs:
            # Load in the coinpair's MACD and MACD-Signal info.
            macd = macds[pair]
            signal = signals[pair]

            status = 'hold'

            # TODO: Determine a 'buy' status.

            # Self explanatory.
            # It automatically updates the balances and positions.
            # TODO: Replace 0.5 with percent of total BTC you want to use to buy.
            if status == 'buy':
                buy(balances, positions, row['Open Time'], pair, min(1.0, 0.5), row['open-' + pair], dataMinMax)

            # For all positions, if they're open then update it. If the status is sell, sell.
            # It automatically updates the balances and positions.
            for position in get_positions(positions, pair):
                if position['open']:
                    update_position(position, row['Open Time'], row['open-' + pair], params['arm'])
                    #if status == 'sell': sell(balances, position, row['Open Time'], dataMinMax)
                    if position['stop-loss'] and position['result'] / position['peak'] < params['stop']:
                        sell(balances, position, row['Open Time'], dataMinMax)
                    elif position['result'] < params['drop']:
                        sell(balances, position, row['Open Time'], dataMinMax)

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
        elif pair == 'NEOBTC': pairs.append(pair)

    # Verify that all coinpairs were loaded correctly.
    # Comment out if only testing one coinpair.
    '''if len(pairs) != len(glob.glob(sys.argv[1].split('/')[0] + '/*.csv')) - 1 or len(pairs) != len(utilities.COINPAIRS):
        utilities.throw_error('Not all coinpairs loaded. Some history may be missing.', True)'''

    # Run the backtesting function, getting the necessary information returned.
    balances, positions = backtest(data, {'BTC': 1.0}, pairs, {'arm': 1.01, 'stop': 0.996, 'drop': 0.98})

    #results[1].to_csv('results/' + sys.argv[1].split('/')[0] + '.csv', index=False)
    print('INFO: Finished with ' + str(get_total_balance(data, balances)) + ' BTC from 1 BTC')
    #print('\t' + str(100 * results[0] / helpers.starting_total(data, results[1])) + '% ROI')
    #diff = pandas.to_datetime(data.iloc[-1]['Open Time'], unit='ms') - pandas.to_datetime(data.iloc[0]['Open Time'], unit='ms')
    #print('\tOver ' + str(diff) + ' hours')

    # If the '-p' argument was provided, show the plotting.
    if '-p' in sys.argv:
        plt.legend()
        plt.show()
