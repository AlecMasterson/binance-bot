import sys, pandas, math, helpers
import numpy as np
from bayes_opt import BayesianOptimization

# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def backtest(df, trading, args):
	try:
		# Insert your own bot here.
	except:
		print('ERROR: Unknown Error!')

	# --------------------------------------------------------------------------
	# SAVE BACKTEST TRADING DATA
	# --------------------------------------------------------------------------

	# Save the trading-data obtained from backtesting.
	# Use analyze.py following the specification in the README file to obtain info.
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

	return 0

# ------------------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------------------

print('\nPROC: Back-Test Historical Data\n')

# Test for valid command usage.
if len(sys.argv) is not 2:
	print('ERROR: Command Usage -> \'python3 backtest.py <price-data>\'')
	sys.exit()

# Get the price-data file used for testing.
try:
	print('IO: Looking For Price Data...')
	df = pandas.read_csv(sys.argv[1])
	print('Found!')
except:
	print('ERROR: No Price Data Found!')
	sys.exit()

# Create DataFrame to store trading data during testing.
# Follow the specification detailed in the README file.
trading = pandas.DataFrame(
	data={
		'type': 'start', 'time': 0,
		'price': 0, 'quantity': 1.0,
		'btc': 0.05, 'eth': 0.0
	}, index=[0]
)

# ------------------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------------------

# Customize with constants returned from BayesianOptimization.
args = {'arc': 7.4907, 'thin': 2.0637, 'hi': 1.0011, 'low': 0.9944}

backtest(df, trading, args)

print('\nPROC: Done!')

# ------------------------------------------------------------------------------
# BAYESIAN OPTIMIZATION
# ------------------------------------------------------------------------------

# Change to True if you would like to optimize the constants in args.
# The bo object initialization needs altering based on your bot.
# Follow specification in the README file.
if False:
	print ('\nPROC: Optimizing...\n')
	bo = BayesianOptimization(
		lambda arc, thin, low, hi: backtest(
			df, trading, {'arc': arc, 'thin': thin, 'low': low, 'hi': hi}
		), {
			'arc': (3, 9), 'thin': (0, 9),
			'low': (0.985, 0.999), 'hi': (1.0001, 1.01)
		}
	)
	bo.maximize(init_points=10, n_iter=500, kappa=2)
	print('INFO: Optimized Constants\n\t' + bo.res['max'])