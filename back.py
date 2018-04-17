import numpy as np
import matplotlib.pyplot as plt
import sys, pandas, talib, math, glob, helpers


def plot_scatter(time, price, color):
    plt.scatter(pandas.to_datetime(time, unit='ms'), price, color=color)


def convert_to_OHLC(data, coinPair):
    return [np.array(data['open-' + coinPair]), np.array(data['high-' + coinPair]), np.array(data['low-' + coinPair]), np.array(data['close-' + coinPair])]


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


def backtest(data, coinPairs, params):

    # Initialize the trading-data DataFrame with our starting BTC/ETH values.
    trading = pandas.DataFrame(data={'type': 'start', 'coinPair': '', 'time': 0, 'price': 0, 'quantity': 1.0, 'fee': 0.0, 'btc': 0.0, 'eth': 0.1}, index=[0])

    macds = {}
    for coinPair in coinPairs:
        if not coinPair.startswith('BTC') and not coinPair.startswith('ETH'): trading[coinPair] = np.array([0.0])

        dataMinMax = [min(data['open-' + coinPair]), max(data['open-' + coinPair])]
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), 0.2 + (data['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]))

        macd, macdsignal, macdhist = talib.MACDFIX(np.array(data['close-' + coinPair]), signalperiod=9)
        #macd = talib.MA(macd, timeperiod=params['smooth'], matype=0)
        macds[coinPair] = macd

        macdMinMax = [get_min(macd), get_max(macd)]
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), (macd - macdMinMax[0]) / (macdMinMax[1] - macdMinMax[0]))
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), np.array([(0.0 - macdMinMax[0]) / (macdMinMax[1] - macdMinMax[0]) for i in range(len(data))]))

    peaks = {}
    bought = False
    for index, row in data.iterrows():
        if index < 3: continue

        for coinPair in coinPairs:
            macd = macds[coinPair]

            # peaks is a dict that looks for the extreme points in the MACD.
            # I use the term 'peak' interchangeablly to describe a peak or valley.

            # Set the initial peak point.
            if not coinPair in peaks or math.isnan(peaks[coinPair]):
                peaks[coinPair] = macd[index - 1]

            # If price is increasing and either (current peak was when price was decreasing or peak is lower than the current MACD).
            elif macd[index - 1] > 0 and (peaks[coinPair] < 0 or peaks[coinPair] < macd[index - 1]):
                peaks[coinPair] = macd[index - 1]

            # If price is descreasing and either (current peak was when price was increasing or peak is lower than the current MACD).
            elif macd[index - 1] < 0 and (peaks[coinPair] > 0 or peaks[coinPair] > macd[index - 1]):
                peaks[coinPair] = macd[index - 1]

            # bought is (debug only) used to not call plot_scatter too many times.
            # plot_scatter is a function used to just plot a point.
            # minmax values are being used (debug only) when plotting so it's normalized to easily read.
            # helpers.buy or helpers.sell automatically won't buy/sell if it doesn't have the funds.

            # If the price is increasing but our current MACD is below our % threshold from that peak showing that it soon will be decreasing.
            elif not bought and peaks[coinPair] > 0 and macd[index - 1] < params['cut'] * peaks[coinPair]:
                trading = helpers.buy(trading, coinPair, row['Open Time'], row['open-' + coinPair], 1.0, 0.001)
                plot_scatter(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'red')
                bought = True

            # If the price is decreasing but our current MACD is above our % threshold from that peak showing that it soon will be increasing.
            elif bought and peaks[coinPair] < 0 and macd[index - 1] > params['cut'] * peaks[coinPair]:
                trading = helpers.sell(trading, coinPair, row['Open Time'], row['open-' + coinPair], 1.0, 0.001)
                plot_scatter(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'green')
                bought = False
                del peaks[coinPair]

    # Return both the final BTC and the trading-data.
    return [helpers.combined_total(data, trading, coinPairs), trading]


# A separate function for optimization so we only acknowledge the final BTC value.
def optimize(data, coinPairs, params):
    return backtest(data, coinPairs, params)[0]


if __name__ == "__main__":

    if len(sys.argv) > 2:
        print('ERROR: Too Many Arguments!')
        sys.exit()

    if '-p' in sys.argv: plotting = True
    else: plotting = False

    coinPairs = []
    for file in glob.glob('data_30_min/*.csv'):
        coinPair = file.split('/')[1].split('.')[0]
        if coinPair == 'ALL': data = pandas.read_csv(file)
        elif coinPair == 'BNBETH': coinPairs.append(coinPair)

    # Actually run the backtesting function.
    results = backtest(data, coinPairs, {'cut': 0.9716, 'smooth': 12})
    print('INFO: Finished with ' + str(results[0]) + ' BTC')

    # Save the backtesting trading-data to the ./results/ directory.
    results[1].to_csv('results/ALL_results.csv', index=False)

    # Plot the trading-data and the price-data if the argument was provided.
    if plotting:

        # Convert the time intervals from milliseconds to datetime objects.
        #data['Open Time'] = pandas.to_datetime(data['Open Time'], unit='ms')
        #results[1]['time'] = pandas.to_datetime(results[1]['time'], unit='ms')

        # Convert the buy/sell data selling so they may be used in a scatter plot.
        if False and len(trading.index) > 1:
            a, b = results[1][results[1].type == 'buy'].as_matrix(['time', 'price']).T
            plt.scatter(a, b, color='red')
            c, d = results[1][results[1].type == 'sell'].as_matrix(['time', 'price']).T
            plt.scatter(c, d, color='green')
        '''for coinPair in coinPairs:
            minmax = [min(data['open-' + coinPair]), max(data['open-' + coinPair])]
            data['open-' + coinPair] -= minmax[0]
            data['open-' + coinPair] /= (minmax[1] - minmax[0])
            plt.plot(data['Open Time'], data['open-' + coinPair])'''

        # Simply plot the price-data as a line graph.
        #plt.plot(data['Open Time'], data['Open'], linestyle='dashed', color='blue')

        plt.legend()
        plt.show()
