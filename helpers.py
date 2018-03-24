import sys, math

# Round down x to the nearest 0.001 (Binance Trade Minimum)
def round_down(x):
	return float(math.floor(x * 1000) / 1000)

# Buy ETH with a 0.1% fee using quantity percentage of available BTC
def buy(trading, time, price, quantity):
	return trading.append(
		{
			'type': 'buy', 'time': time,
			'price': price, 'quantity': quantity,
			'btc': trading.iloc[-1]['btc'] - round_down(
				trading.iloc[-1]['btc'] * quantity
			),
			'eth': trading.iloc[-1]['eth'] + ((
				round_down(trading.iloc[-1]['btc'] * quantity) / price
			) * 0.999)
		}, ignore_index=True
	)

# Sell BTC with a 0.1% fee using quantity percentage of available ETH
def sell(trading, time, price, quantity):
	return trading.append(
		{
			'type': 'sell', 'time': time,
			'price': price, 'quantity': quantity,
			'btc': trading.iloc[-1]['btc'] + ((
				round_down(trading.iloc[-1]['eth'] * quantity) * price
			) * 0.999),
			'eth': trading.iloc[-1]['eth'] - round_down(
				trading.iloc[-1]['eth'] * quantity
			)
		}, ignore_index=True
	)

# Return True if potential gain/loss of selling is outside the bounds
# TODO: Unsure if function works properly when quantity isn't always 1.0
def predict_change(trading, price, quantity, args):
	change = trading.iloc[len(trading.index) - 2]['btc'] / (
		trading.iloc[-1]['btc'] + (
			round_down(trading.iloc[-1]['eth'] * quantity) * price
		) * 0.999
	)
	if change < args['low'] or change > args['hi']:
		return True
	return False

# Return combined wallet total of BTC and ETH in the form of BTC
def combined_total(row):
	return row['btc'] + (row['eth'] * row['price'])

# Get the price-data file used for testing.
def get_price_data(fileName):
	try:
		print('IO: Looking For Price Data...')
		df = pandas.read_csv(fileName)
		print('Found!')
		return df
	except:
		print('ERROR: No Price Data Found!')
		sys.exit()

# Save the trading-data obtained from backtesting.
# Use analyze.py following the specification in the README file to obtain info.
def save_trading_data(trading):
	try:
		print('IO: Writing Back-Testing Results to backtest_results.csv')
		trading.to_csv(
			'backtest_results.csv',
			columns=[
				'type', 'time', 'price', 'quantity', 'btc', 'eth'
			], index=False
		)
		print('Success!')
	except:
		print('ERROR: Failed Writing to File!')
		sys.exit()