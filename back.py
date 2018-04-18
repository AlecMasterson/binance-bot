import numpy as np
import matplotlib.pyplot as plt
import sys, pandas, talib, math, glob, helpers


# A simple function for plotting a point.
# x - The x-coordinate to plot, in milliseconds
# y - The y-coordinate to plot
def plot_point(x, y, color):
    plt.scatter(pandas.to_datetime(x, unit='ms'), y, color=color)


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
    trading = pandas.DataFrame(data={'type': 'start', 'coinPair': '', 'time': 0, 'price': 0.0, 'quantity': 0.0, 'fee': 0.0, 'btc': 0.0, 'eth': 0.1}, index=[0])

    macds = {}
    sources = [0, 0]
    for coinPair in coinPairs:
        if not coinPair.startswith('BTC') and not coinPair.startswith('ETH'): trading[coinPair] = np.array([0.0])
        if coinPair.endswith('BTC'): sources[0] += 1
        else: sources[1] += 1

        dataMinMax = [min(data['open-' + coinPair]), max(data['open-' + coinPair])]
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), (data['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]))

        macd, macdsignal, macdhist = talib.MACDFIX(np.array(data['close-' + coinPair]), signalperiod=9)
        macds[coinPair] = macd

        #macdMinMax = [get_min(macd), get_max(macd)]
        #plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), (macd - macdMinMax[0]) / (macdMinMax[1] - macdMinMax[0]))
        #plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), np.array([(0.0 - macdMinMax[0]) / (macdMinMax[1] - macdMinMax[0]) for i in range(len(data))]))

    peaks = {}
    bought = False
    for index, row in data.iterrows():
        if index == 0: continue

        for coinPair in coinPairs:
            macd = macds[coinPair]

            if coinPair.endswith('BTC'): quantity = 1.0 / sources[0]
            else: quantity = 1.0 / sources[1]

            if not coinPair in peaks or math.isnan(peaks[coinPair]):
                peaks[coinPair] = macd[index - 1]

            elif macd[index - 1] > 0 and (peaks[coinPair] < 0 or peaks[coinPair] < macd[index - 1]):
                peaks[coinPair] = macd[index - 1]

            elif macd[index - 1] < 0 and (peaks[coinPair] > 0 or peaks[coinPair] > macd[index - 1]):
                peaks[coinPair] = macd[index - 1]

            elif not bought and peaks[coinPair] > 0 and macd[index - 1] < params['cut'] * peaks[coinPair]:
                trading = helpers.buy(trading, coinPair, row['Open Time'], row['open-' + coinPair], quantity, 0.001)
                #plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'red')
                bought = True

            elif bought and peaks[coinPair] < 0 and macd[index - 1] > params['cut'] * peaks[coinPair]:
                trading = helpers.sell(trading, coinPair, row['Open Time'], row['open-' + coinPair], 1.0, 0.001)
                #plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'green')
                bought = False
                del peaks[coinPair]

    # Return both the final BTC and the trading-data.
    return [helpers.combined_total(data, trading, coinPairs), trading]


def optimize(data, coinPairs, params):
    return backtest(data, coinPairs, params)[0]


if __name__ == "__main__":

    coinPairs = []
    for file in glob.glob(sys.argv[1].split('/')[0] + '/*.csv'):
        coinPair = file.split('/')[1].split('.')[0]
        if coinPair == 'ALL': data = pandas.read_csv(file)
        else: coinPairs.append(coinPair)

    results = backtest(data, coinPairs, {'cut': 0.9082})
    results[1].to_csv('results/' + sys.argv[1].split('/')[0] + '.csv', index=False)
    print('INFO: Finished with ' + str(results[0]) + ' BTC')
    print('\t' + str(100 * results[0] / helpers.starting_total(data, results[1])) + '% ROI')
    diff = pandas.to_datetime(data.iloc[-1]['Open Time'], unit='ms') - pandas.to_datetime(data.iloc[0]['Open Time'], unit='ms')
    print('\tOver ' + str(diff) + ' hours')

    if '-p' in sys.argv:
        plt.legend()
        plt.show()
