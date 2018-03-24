import sys, pandas, math, helpers
import numpy as np
from bayes_opt import BayesianOptimization

# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def backtest(df, trading, args):
	try:
		# TODO: Insert your own bot here...
		# Follow the specification detailed in the README file.
	except:
		print('ERROR: Unknown Error!')
		sys.exit()

	# Save the trading-data obtained from backtesting.
	save_trading_data(trading)

	# Return the final wallet total.
	return helpers.combined_total(trading.iloc[-1])



# ------------------------------------------------------------------------------



# ------------------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------------------

print('\nPROC: Back-Test Historical Data\n')

# Test for valid command usage.
# Follow the specification detailed in the README file.
if len(sys.argv) is not 2:
	print('ERROR: Command Usage ->' +
		'\'python3 backtest.py <price-data> <optimize>\'')
	sys.exit()

# Get the price-data file used for testing.
df = get_price_data(sys.argv[1])

# Create DataFrame to store trading data.
# Follow the specification detailed in the README file.
trading = pandas.DataFrame(
	data={
		'type': 'start', 'time': 0,
		'price': 0, 'quantity': 1.0,
		'btc': 0.05, 'eth': 0.0
	}, index=[0]
)

# Only run if script is not being used for optimization.
# Customize the constants with what is returned from BayesianOptimization.
# See below and the README file for more info on BayesianOptimization.
if not optimize:
backtest(df, trading, {
	'arc': 7.4907, 'thin': 2.0637, 'hi': 1.0011, 'low': 0.9944
})

print('\nPROC: Done!')

# ------------------------------------------------------------------------------
# BAYESIAN OPTIMIZATION
# ------------------------------------------------------------------------------

if optimize:
	print ('\nPROC: Optimizing Bot Constants...\n')

	# The bo object initialization needs altering based on your bot.
	# Follow the specification detailed in the README file.
	bo = BayesianOptimization(
		lambda arc, thin, low, hi: backtest(
			df, trading, {'arc': arc, 'thin': thin, 'low': low, 'hi': hi}
		), {
			'arc': (3, 9), 'thin': (0, 9),
			'low': (0.9800, 0.9999), 'hi': (1.0001, 1.0200)
		}
	)

	# Adjust below arguments to your liking.
	# Follow the specification detailed in the README file.
	bo.maximize(init_points=10, n_iter=500, kappa=2)

	print('INFO: Optimized Constants\n\t' + bo.res['max'])