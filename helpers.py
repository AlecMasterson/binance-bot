import pandas, sys, math

# Round down x to the nearest 0.001 (Binance Trade Minimum)
def round_down(x):
	return float(math.floor(x * 1000) / 1000)

# Buy ETH with a 0.1% fee using quantity percentage of available BTC
def buy(trading, time, price, quantity):
	if round_down(trading.iloc[-1]['btc'] * quantity) == 0.0:
		return trading
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
	if round_down(trading.iloc[-1]['eth'] * quantity) == 0.0:
		return trading
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

# Return combined wallet total of BTC and ETH in the form of BTC
def combined_total(row):
	return row['btc'] + (row['eth'] * row['price'])

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