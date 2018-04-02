import sys, pandas, math, datetime, helpers, glob
import numpy as np
import matplotlib.pyplot as plt
from bayes_opt import BayesianOptimization

def get_min_max(frame):
	return [min(frame['Close']), max(frame['Close'])]

# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def backtest(coin, args):

	trading = pandas.DataFrame(
		data={
			'type': 'start', 'time': 0,
			'price': 0, 'quantity': 1.0,
			'btc': 0.01, 'alt': 0.0
		}, index=[0]
	)

	for index, row in coin.iterrows():
		if index > 2:
			section = coin[index-3:index]
			line = np.poly1d(
				np.polyfit(section['Close Time'], section['Close'], 2)
			)

			potentialTrade = False
			if line.c[0] < float(args['thindown'] * pow(10, math.floor(args['power']))) and row['Close'] < section.iloc[0]['Close']:
				potentialTrade = True
			elif line.c[0] > float(args['thinup'] * pow(10, math.floor(args['power']))) and row['Close'] > section.iloc[0]['Close']:
				potentialTrade = True

			if potentialTrade:
				prevCount = len(trading.index)
				if row['Close'] < section.iloc[-1]['Close']:
					trading = helpers.buy(trading, row['Close Time'], row['Close'], 1.0)
				elif row['Close'] > section.iloc[-1]['Close'] and helpers.predict_change(trading, row['Close'], 1.0, args):
					trading = helpers.sell(trading, row['Close Time'], row['Close'], 1.0)

	return [helpers.combined_total(trading.iloc[-1]), trading]

def baye(coin, args):
	return backtest(coin, args)[0]


# ------------------------------------------------------------------------------



args = {
	'data/ADABTC.csv': {
		'thinup': 9.8474, 'thindown': -9.2006, 'power': -20,
		'low': 0.9871, 'hi': 1.0085
	},
	'data/BNBBTC.csv': {
		'thinup': 9.99, 'thindown': -9.99, 'power': -21,
		'low': 0.96, 'hi': 1.01
	},
	'data/ETHBTC.csv': {
		'thinup': 5.5667, 'thindown': -7.8263, 'power': -17,
		'low': 0.9701, 'hi': 1.0013
	},
	'data/LTCBTC.csv': {
		'thinup': 9.1349, 'thindown': -7.5062, 'power': -18,
		'low': 0.9822, 'hi': 1.0071
	},
	'data/XRPBTC.csv': {
		'thinup': 8.3554, 'thindown': -5.1044, 'power': -20,
		'low': 0.9647, 'hi': 1.0042
	}
}

total = 0
for fileName in glob.glob('data/*.csv'):
	coin = pandas.read_csv(fileName)
	# Only looking at BNB
	if fileName != 'data/BNBBTC.csv': continue
	print('INFO: Backtesting '+fileName)

	if fileName == 'data/BNBBTC.csv':
		bo = BayesianOptimization(
			lambda thinup, thindown, power, low, hi: baye(
				coin.head(720), {
					'thinup': thinup, 'thindown': thindown, 'power': power,
					'low': low, 'hi': hi
				}
			), {
				'thinup': (5.00, 9.99), 'thindown': (-9.99, -5.00), 'power': (-21, -16),
				'low': (0.9600, 0.9900), 'hi': (1.0001, 1.0100)
			}
		)
		print(bo.maximize(init_points=10, n_iter=15, kappa=10))

	vals = backtest(coin, args[fileName])
	print('\tFinished with '+str(vals[0])+' BTC')
	total += vals[0]

	coinMinMax = get_min_max(coin)
	for index, row in coin.iterrows():
		coin.at[index, 'Close'] = (row['Close'] - coinMinMax[0]) / (coinMinMax[1] - coinMinMax[0])

	# Change to true to show plotting.
	if False:
		for index, row in vals[1].iterrows():
			vals[1].at[index, 'price'] = (row['price'] - coinMinMax[0]) / (coinMinMax[1] - coinMinMax[0])

		vals[1]['time'] = pandas.to_datetime(vals[1]['time'], unit='ms')

		a, b = vals[1][vals[1].type == 'buy'].as_matrix(['time', 'price']).T
		plt.scatter(a, b, color='red', s=10)
		c, d = vals[1][vals[1].type == 'sell'].as_matrix(['time', 'price']).T
		plt.scatter(c, d, color='green', s=10)

		coin['Close Time'] = pandas.to_datetime(coin['Close Time'], unit='ms')
		plt.plot(coin['Close Time'], coin['Close'], color='pink', linestyle='dashed', label=fileName)

print('\nFinal BTC: '+str(total))
plt.legend()
plt.show()