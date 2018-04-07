import numpy as np
import matplotlib.pyplot as plt
import sys, pandas, math, helpers


def backtest(data, params):

    # Initialize the trading-data DataFrame with our starting BTC value.
    trading = pandas.DataFrame(data={'type': 'start', 'time': 0, 'price': 0, 'quantity': 1.0, 'btc': 0.01, 'alt': 0.0}, index=[0])

    # Traverse through price-data row by row.
    for index, row in data.iterrows():

        # Skip the first section of the price-data so we can analyze the past
        if index < math.floor(params['arc']): continue

        # Get the previous 'arc' rows and create a parabola.
        section = data[index - math.floor(params['arc']):index]
        line = np.poly1d(np.polyfit(section['Close Time'], section['Close'], 2))

        # A potential trade could occur if the one of the following is true:
        # - The parabola faces down, is of a certain thinness, AND the current price is below the start.
        # - The parabola faces up, is of a certain thinness, AND the current price is above the start.
        potentialTrade = False
        if line.c[0] < float(params['thin'] * -1 * pow(10, -17)) and row['Close'] < section.iloc[0]['Close']:
            potentialTrade = True
        elif line.c[0] > float(params['thin'] * pow(10, -17)) and row['Close'] > section.iloc[0]['Close']:
            potentialTrade = True

        # Move on if there's no potential trade to make.
        if not potentialTrade: continue

        # Buy if the current price is below the last price.
        # Sell if the current price is above the last price and a profit % decrease/increase is outside the bounds.
        if row['Close'] < section.iloc[-1]['Close']:
            trading = helpers.buy(trading, row['Close Time'], row['Close'], 1.0)
        elif row['Close'] > section.iloc[-1]['Close'] and helpers.predict_change(trading, row['Close'], 1.0, params):
            trading = helpers.sell(trading, row['Close Time'], row['Close'], 1.0)

    # Return both the final BTC and the trading-data.
    return [helpers.combined_total(trading.iloc[-1]), trading]


# A separate function for optimization so we only acknowledge the final BTC value.
def optimize(data, params):
    return backtest(data, params)[0]


# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

if __name__ == "__main__":

    # The different parameters for the different coin-pairs.
    paramBNB = {'arc': 3, 'thin': 0.1189, 'low': 0.9639, 'hi': 1.0061}

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
        data['Close Time'] = pandas.to_datetime(data['Close Time'], unit='ms')

        # Convert the buy/sell data points so they may be used in a scatter plot.
        a, b = results[1][results[1].type == 'buy'].as_matrix(['time', 'price']).T
        plt.scatter(a, b, color='red', s=10)
        c, d = results[1][results[1].type == 'sell'].as_matrix(['time', 'price']).T
        plt.scatter(c, d, color='green', s=10)

        # Simply plot the price-data as a line graph.
        plt.plot(data['Close Time'], data['Close'], color='blue', linestyle='dashed')

        plt.show()
