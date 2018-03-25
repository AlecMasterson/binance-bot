import sys, pandas, math, datetime, helpers
import numpy as np
import matplotlib.pyplot as plt
from bayes_opt import BayesianOptimization

# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def backtest(df, trading, args):
	try:
		for index, row in df.iterrows():
			if index > math.floor(args['arc'])-1:
				section = df[index-math.floor(args['arc']):index]
				line = np.poly1d(np.polyfit(section['Close Time'], section['Close'], 2))

				if line.c[0] < float(args['thindown'] * -1/1e17) and row['Close'] < section.iloc[0]['Close']:
					if row['Close'] < section.iloc[-1]['Close']:
						trading = helpers.buy(trading, row['Close Time'], row['Close'], 1.0)
					elif row['Close'] > section.iloc[-1]['Close'] and helpers.predict_change(trading, row['Close'], 1.0, args):
						trading = helpers.sell(trading, row['Close Time'], row['Close'], 1.0)

					# Additional Plotting
					#plot_x = np.linspace(section.iloc[0]['Close Time'], section.iloc[len(section.index)-1]['Close Time'])
					#plt.plot(pandas.to_datetime(plot_x, unit='ms'), line(plot_x))

				elif line.c[0] > float(args['thinup'] * 1/1e17) and row['Close'] > section.iloc[0]['Close']:
					if row['Close'] < section.iloc[-1]['Close']:
						trading = helpers.buy(trading, row['Close Time'], row['Close'], 1.0)
					elif row['Close'] > section.iloc[-1]['Close'] and helpers.predict_change(trading, row['Close'], 1.0, args):
						trading = helpers.sell(trading, row['Close Time'], row['Close'], 1.0)

					# Additional Plotting
					#plot_x = np.linspace(section.iloc[0]['Close Time'], section.iloc[len(section.index)-1]['Close Time'])
					#plt.plot(pandas.to_datetime(plot_x, unit='ms'), line(plot_x))
	except:
		print('ERROR: Unknown Error During Back-Test!')
		sys.exit()

	# Save the trading-data obtained from backtesting.
	if sys.argv[2] is 'F':
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

	# --------------------------------------------------------------------------
	# ANALYSIS
	# --------------------------------------------------------------------------
	'''
	if sys.argv[2] is 'F':
		startDay = datetime.date.fromtimestamp(tradingData.iloc[1]['time'] / 1e3)
		endDay = datetime.date.fromtimestamp(tradingData.iloc[-1]['time'] / 1e3)
		percentChange = helpers.combined_total(
			tradingData.iloc[-1]) / helpers.combined_total(tradingData.iloc[0])

		print('\nRESULTS...\nStart Day: ' + str(startDay) + '\tEnd Day: ' + str(endDay))
		print(str(percentChange) + '% ROI Over ' + str(endDay-startDay) + ' Days')
	'''

	# --------------------------------------------------------------------------
	# PLOT TRADING
	# --------------------------------------------------------------------------

	if sys.argv[2] is 'F' and sys.argv[3] is 'T':
		trading['time'] = pandas.to_datetime(trading['time'], unit='ms')

		bought = pandas.DataFrame(columns=['time', 'price'])
		sold = pandas.DataFrame(columns=['time', 'price'])
		for index, row in trading.iloc[1:].iterrows():
			if row['type'] is 'buy':
				bought = bought.append(row, ignore_index=True)
			elif row['type'] is 'sell':
				sold = sold.append(row, ignore_index=True)

		a, b = bought.as_matrix(['time', 'price']).T
		c, d = sold.as_matrix(['time', 'price']).T

		plt.scatter(a, b, color='red')
		plt.scatter(c, d, color='green')

		df['Close Time'] = pandas.to_datetime(df['Close Time'], unit='ms')
		plt.plot(df['Close Time'], df['Close'], linestyle="dashed")

		plt.show()

	# Return the final wallet total.
	return helpers.combined_total(trading.iloc[-1])



# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------------------

print('\nPROC: Back-Test Historical Data\n')

# Test for valid command usage.
# Follow the specification detailed in the README file.
invalidCommand = False
if len(sys.argv) < 2 or len(sys.argv) > 4:
	invalidCommand = True

if len(sys.argv) >= 3 and sys.argv[2] is not 'T' and sys.argv[2] is not 'F':
	invalidCommand = True

if len(sys.argv) is 4 and sys.argv[3] is not 'T' and sys.argv[3] is not 'F':
	invalidCommand = True

if invalidCommand:
	print('ERROR: Command Usage ->' +
		'\'python3 backtest.py <price-data> [optimize] [plot]\'')
	print('INFO: Follow the specification detailed in the README file!\n')
	sys.exit()

# Get the price-data file used for testing.
try:
	print('IO: Looking For Price Data...')
	df = pandas.read_csv(sys.argv[1])
	print('Found!')
except:
	print('ERROR: No Price Data Found!')
	sys.exit()

# Create DataFrame to store trading data.
# Follow the specification detailed in the README file.
trading = pandas.DataFrame(
	data={
		'type': 'start', 'time': 0,
		'price': 0, 'quantity': 1.0,
		'btc': 0.05, 'eth': 0.0
	}, index=[0]
)

# ------------------------------------------------------------------------------
# RUN TESTING
# ------------------------------------------------------------------------------

# Only run if script is not being used for optimization.
# Customize the constants with what is returned from BayesianOptimization.
# See below and the README file for more info on BayesianOptimization.
if sys.argv[2] is 'F':
	result = backtest(df, trading, {
		'arc': 3.0000, 'thinup': 5.4431, 'thindown': 7.0290,
		'low': 0.9800, 'hi': 1.0106
	})
	print('Final BTC: '+str(result)+'\nPROC: Done!\n')

# ------------------------------------------------------------------------------
# BAYESIAN OPTIMIZATION
# ------------------------------------------------------------------------------

if sys.argv[2] is 'T':
	print ('\nPROC: Optimizing Bot Constants...\n')

	# The bo object initialization needs altering based on your bot.
	# Follow the specification detailed in the README file.
	bo = BayesianOptimization(
		lambda arc, thinup, thindown, low, hi: backtest(
			df, trading, {
				'arc': arc, 'thinup': thinup, 'thindown': thindown,
				'low': low, 'hi': hi
			}
		), {
			'arc': (3, 6), 'thinup': (0, 9), 'thindown': (0, 9),
			'low': (0.9800, 0.9999), 'hi': (1.0001, 1.0200)
		}
	)

	# Adjust below arguments to your liking.
	# Follow the specification detailed in the README file.
	bo.maximize(init_points=10, n_iter=100, kappa=2)

	print('INFO: Optimized Constants\n\t' + bo.res['max'])