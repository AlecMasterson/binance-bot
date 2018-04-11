from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import sys, pandas, talib, math, helpers


def identify(kind, open, high, low, close):
    results = kind(open, high, low, close)

    positions = []
    pos = 0
    for num in results:
        if num != 0:
            positions.append(pos)
        pos += 1
    return positions


def predict_change(trading, price, quantity, args):
    change = trading.iloc[len(trading.index) - 2]['btc'] / (trading.iloc[-1]['btc'] + (helpers.round_down(trading.iloc[-1]['alt'] * quantity) * price) * 0.999)
    if change < args['low'] or change > args['hi']:
        return True
    return False


def backtest(data, params):

    # Convert necessary information to numpy arrays for candlestick classification.
    open = np.array(data['Open'])
    high = np.array(data['High'])
    low = np.array(data['Low'])
    close = np.array(data['Close'])

    hammer = identify(talib.CDLHAMMER, open, high, low, close)
    shootingStar = identify(talib.CDLSHOOTINGSTAR, open, high, low, close)
    hangingMan = identify(talib.CDLHANGINGMAN, open, high, low, close)
    englufing = identify(talib.CDLENGULFING, open, high, low, close)
    doji = identify(talib.CDLDOJI, open, high, low, close)
    dragonfly = identify(talib.CDLDRAGONFLYDOJI, open, high, low, close)

    # Initialize the trading-data DataFrame with our starting BTC value.
    trading = pandas.DataFrame(data={'type': 'start', 'time': 0, 'price': 0, 'fee': 0.0, 'quantity': 1.0, 'btc': 0.01, 'alt': 0.0}, index=[0])

    purchase = pandas.DataFrame(columns=['time', 'price'])
    maybe = pandas.DataFrame(columns=['time', 'price'])
    selling = pandas.DataFrame(columns=['time', 'price'])

    # Traverse through price-data row by row.
    for index, row in data.iterrows():
        #if index in doji: maybe = maybe.append({'time': row['Open Time'], 'price': row['Open']}, ignore_index=True)
        #if index in dragonfly: purchase = purchase.append({'time': row['Open Time'], 'price': row['Open']}, ignore_index=True)
        #if index in hammer:
        #purchase = purchase.append({'time': row['Open Time'], 'price': row['Open']}, ignore_index=True)
        if index in englufing: maybe = maybe.append({'time': row['Open Time'], 'price': row['Open']}, ignore_index=True)

        if row['Open'] > data.iloc[index - 1]['Open']:
            trading = helpers.sell(trading, row['Close Time'], row['Close'], 0.001, 1.0)
            selling = selling.append({'time': row['Open Time'], 'price': row['Open']}, ignore_index=True)
        else:
            trading = helpers.buy(trading, row['Close Time'], row['Close'], 0.001, 1.0)
            purchase = purchase.append({'time': row['Open Time'], 'price': row['Open']}, ignore_index=True)

    # Return both the final BTC and the trading-data.
    return [helpers.combined_total(trading.iloc[-1]), trading, selling, purchase, maybe]


# A separate function for optimization so we only acknowledge the final BTC value.
def optimize(data, params):
    return backtest(data, params)[0]


if __name__ == "__main__":

    # The different parameters for the different coin-pairs.
    paramBNB = {'arc': 3, 'thin': 0.1189, 'lo': 0.9639, 'hi': 1.0061, 'low': 1.0112, 'high': 1.023}

    # Test for the -p command argument.
    if '-p' in sys.argv: plotting = True
    else: plotting = False

    # Test for the price-data .csv argument.
    if not sys.argv[-1].endswith('.csv'):
        print('ERROR: Last argument must be your price-data .csv file!')
        sys.exit()

    # Get the price-data to backtest.
    data = pandas.read_csv(sys.argv[-1])

    # Test that the price-data has the correct DataFrame column structure.
    columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number Trades', 'Taker Base Asset Volume', 'Take Quote Asset Volume', 'Ignore']
    if list(data) != columns:
        print('ERROR: Incorrect price-data DataFrame column structure!')
        sys.exit()

    # Actually run the backtesting function.
    results = backtest(data, paramBNB)
    print('INFO: Finished with ' + str(results[0]) + ' BTC')

    # Save the backtesting trading-data to the ./results/ directory.
    results[1].to_csv('results/' + str(sys.argv[-1].split('/')[1]), index=False)

    # Plot the trading-data and the price-data if the argument was provided.
    if plotting:

        # Convert the time intervals from milliseconds to datetime objects.
        results[1]['time'] = pandas.to_datetime(results[1]['time'], unit='ms')
        results[2]['time'] = pandas.to_datetime(results[2]['time'], unit='ms')
        results[3]['time'] = pandas.to_datetime(results[3]['time'], unit='ms')
        results[4]['time'] = pandas.to_datetime(results[4]['time'], unit='ms')
        data['Open Time'] = pandas.to_datetime(data['Open Time'], unit='ms')

        # Convert the buy/sell data selling so they may be used in a scatter plot.
        a, b = results[1][results[1].type == 'buy'].as_matrix(['time', 'price']).T
        plt.scatter(a, b, color='red')
        c, d = results[1][results[1].type == 'sell'].as_matrix(['time', 'price']).T
        plt.scatter(c, d, color='green')
        if len(results[2].index) > 0:
            e, f = results[2].as_matrix(['time', 'price']).T
            plt.scatter(e, f, color='orange')
        if len(results[3].index) > 0:
            g, h = results[3].as_matrix(['time', 'price']).T
            plt.scatter(g, h, color='purple')
        if len(results[4].index) > 0:
            j, k = results[4].as_matrix(['time', 'price']).T
            plt.scatter(j, k, color='blue')

        # Simply plot the price-data as a line graph.
        plt.plot(data['Open Time'], data['Open'], color='blue')

        plt.show()
