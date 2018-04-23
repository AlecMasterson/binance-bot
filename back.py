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


def get_slope(x1, x2, y1, y2):
    return (y2 - y1) / (x2 - x1)


def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0] * p2[1] - p2[0] * p1[1])
    return A, B, -C


def intersection(L1, L2):
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return False


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
    signals = {}
    for coinPair in coinPairs:

        dataMinMax = [min(data['open-' + coinPair]), max(data['open-' + coinPair])]
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), (data['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]))

        trading[coinPair] = np.array([0.0])

        macd, macdsignal, macdhist = talib.MACDFIX(np.array(data['close-' + coinPair]), signalperiod=9)
        macds[coinPair] = macd
        signals[coinPair] = macdsignal

        minmax = [get_min(macd), get_max(macd)]
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), (macd - minmax[0]) / (minmax[1] - minmax[0]), label='macd')
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), np.array([(0.0 - minmax[0]) / (minmax[1] - minmax[0]) for i in range(len(data))]))

        minmax = [get_min(macdsignal), get_max(macdsignal)]
        plt.plot(pandas.to_datetime(data['Open Time'], unit='ms'), (macdsignal - minmax[0]) / (minmax[1] - minmax[0]), label='signal')

    peaks = {}
    bought = False
    peakIndex = 0
    for index, row in data.iterrows():
        if index < 2: continue

        for coinPair in coinPairs:
            macd = macds[coinPair]
            signal = signals[coinPair]

            if bought and macd[index - 1] > 0 and macd[index - 2] > macd[index - 1]:
                trading = helpers.sell(trading, coinPair, row['Open Time'], row['open-' + coinPair], 1.0 / len(coinPairs), 0.001)
                plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'green')
                bought = False
            elif not bought and macd[index - 1] < 0 and macd[index - 2] < macd[index - 1]:
                trading = helpers.buy(trading, coinPair, row['Open Time'], row['open-' + coinPair], 1.0, 0.001)
                plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'red')
                bought = True
            '''elif bought and macd[index - 1] < 0 and macd[index - 1] < signal[index - 1] and helpers.predict_loss(trading, coinPair, row['open-' + coinPair], quantity) > 1.003:
                trading = helpers.sell(trading, coinPair, row['Open Time'], row['open-' + coinPair], quantity, 0.001)
                plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'green')
                bought = False'''

            #if row['Open Time'] > 1519084800000 and row['Open Time'] < 1519344000000:
            #print(str(pandas.to_datetime(row['Open Time'], unit='ms')) + '\t' + str(macd[index - 1]) + '\t' + str(signal[index - 1]))
            '''elif bought and helpers.predict_loss(trading, coinPair, row['open-' + coinPair], quantity) < params['loss']:
                trading = helpers.sell(trading, coinPair, row['Open Time'], row['open-' + coinPair], 1.0, 0.001)
                plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'green')
                bought = False'''
            #else:
            #print(helpers.predict_loss(trading, coinPair, row['Open Time'], quantity))
            '''if not coinPair in peaks or math.isnan(peaks[coinPair]):
                peaks[coinPair] = macd[index - 1]
                peakIndex = index

            elif macd[index - 1] > 0 and (peaks[coinPair] < 0 or peaks[coinPair] < macd[index - 1]):
                peaks[coinPair] = macd[index - 1]
                peakIndex = index

            elif macd[index - 1] < 0 and (peaks[coinPair] > 0 or peaks[coinPair] > macd[index - 1]):
                peaks[coinPair] = macd[index - 1]
                peakIndex = index

            elif bought and peaks[coinPair] > 0 and macd[index - 1] < peaks[coinPair]:
                trading = helpers.sell(trading, coinPair, row['Open Time'], row['open-' + coinPair], 1.0, 0.001)
                plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'green')
                bought = False
                del peaks[coinPair]

            elif not bought and peaks[coinPair] < 0 and macd[index - 1] > peaks[coinPair]:
                trading = helpers.buy(trading, coinPair, row['Open Time'], row['open-' + coinPair], quantity, 0.001)
                plot_point(row['Open Time'], (row['open-' + coinPair] - dataMinMax[0]) / (dataMinMax[1] - dataMinMax[0]), 'red')
                bought = True'''

    # Return both the final BTC and the trading-data.
    return [helpers.combined_total(data, trading, coinPairs), trading]


def optimize(data, coinPairs, params):
    return backtest(data, coinPairs, params)[0]


if __name__ == "__main__":

    fig = plt.figure(figsize=(13, 7))

    coinPairs = []
    for file in glob.glob(sys.argv[1].split('/')[0] + '/*.csv'):
        coinPair = file.split('/')[1].split('.')[0]
        if coinPair == 'ALL': data = pandas.read_csv(file)
        elif coinPair == 'ADAETH': coinPairs.append(coinPair)
    '''maxNums = [0, 0, 0, 0]
    for one in range(9, 13):
        for two in range(7, 27):
            for three in range(5, 16):
                result = backtest(data, coinPairs, {'cut': 0.9503, 'buffer': 4, 'loss': 0.982, 'one': one, 'two': two, 'three': three})[0]
                if result > maxNums[0]:
                    maxNums[0] = result
                    maxNums[1] = one
                    maxNums[2] = two
                    maxNums[3] = three
                    print(maxNums)
    print('Done: ' + str(maxNums))
    sys.exit()'''
    results = backtest(data, coinPairs, {'cut': 0.9503, 'buffer': 4, 'loss': 0.975, 'one': 12, 'two': 26, 'three': 9, 'training': 5760})
    results[1].to_csv('results/' + sys.argv[1].split('/')[0] + '.csv', index=False)
    print('INFO: Finished with ' + str(results[0]) + ' BTC from ' + str(helpers.starting_total(data, results[1])))
    print('\t' + str(100 * results[0] / helpers.starting_total(data, results[1])) + '% ROI')
    diff = pandas.to_datetime(data.iloc[-1]['Open Time'], unit='ms') - pandas.to_datetime(data.iloc[0]['Open Time'], unit='ms')
    print('\tOver ' + str(diff) + ' hours')

    if '-p' in sys.argv:
        plt.legend()
        plt.show()
