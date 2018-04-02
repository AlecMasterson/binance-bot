import pandas, sys, math

# Round down x to the nearest 0.001 (Binance Trade Minimum)
def round_down(x):
	return float(math.floor(x * 1000) / 1000)

# Buy ALT with a 0.1% fee using quantity percentage of available BTC
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
			'alt': trading.iloc[-1]['alt'] + ((
				round_down(trading.iloc[-1]['btc'] * quantity) / price
			) * 0.999)
		}, ignore_index=True
	)

# Sell BTC with a 0.1% fee using quantity percentage of available ALT
def sell(trading, time, price, quantity):
	if round_down(trading.iloc[-1]['alt'] * quantity) == 0.0:
		return trading
	return trading.append(
		{
			'type': 'sell', 'time': time,
			'price': price, 'quantity': quantity,
			'btc': trading.iloc[-1]['btc'] + ((
				round_down(trading.iloc[-1]['alt'] * quantity) * price
			) * 0.999),
			'alt': trading.iloc[-1]['alt'] - round_down(
				trading.iloc[-1]['alt'] * quantity
			)
		}, ignore_index=True
	)

# Return combined wallet total of BTC and ALT in the form of BTC
def combined_total(row):
	return row['btc'] + (row['alt'] * row['price'])

# Return True if potential gain/loss of selling is outside the bounds
# TODO: Unsure if function works properly when quantity isn't always 1.0
def predict_change(trading, price, quantity, args):
	change = trading.iloc[len(trading.index) - 2]['btc'] / (
		trading.iloc[-1]['btc'] + (
			round_down(trading.iloc[-1]['alt'] * quantity) * price
		) * 0.999
	)
	if change < args['low'] or change > args['hi']:
		return True
	return False

def predict_change_2(trading, price, quantity, args):
	change = trading.iloc[len(trading.index) - 2]['btc'] / (
		trading.iloc[-1]['btc'] + (
			round_down(trading.iloc[-1]['alt'] * quantity) * price
		) * 0.999
	)
	if change < args['low']:
		return True
	return False