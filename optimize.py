from bayes_opt import BayesianOptimization
from back import baye
import pandas, sys

# ------------------------------------------------------------------------------
# COMMAND USAGE VERIFICATION
# ------------------------------------------------------------------------------

if len(sys.argv) != 2:
	print('\nERROR: Command Usage -> \'python3 optimize.py <data-file>\'\n')
	sys.exit()

print('\nPROC: Bayesian Optimization for '+sys.argv[1]+'\n')

# ------------------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------------------

try:
	print('IO: Looking For Data...')
	data = pandas.read_csv(sys.argv[1])
	print('Found!')
except:
	print('\nERROR: Data Not Found!\n')
	sys.exit()

# ------------------------------------------------------------------------------
# OPTIMIZATION
# ------------------------------------------------------------------------------

try:
	bo = BayesianOptimization(
		lambda arc, thinup, thindown, power, low, hi: baye(
			data, {
				'arc': arc, 'thinup': thinup, 'thindown': thindown, 'power': power,
				'low': low, 'hi': hi
			}
		), {
			'arc': (3.0, 3.0), 'thinup': (1.00, 9.99), 'thindown': (-9.99, -1.00), 'power': (-22, -16),
			'low': (0.9600, 0.9900), 'hi': (1.0001, 1.0100)
		}
	)
	bo.maximize(init_points=100, n_iter=15, kappa=2)
except Exception as e:
	print(e)
	print('\nERROR: Unknown Error During Optimization!\n')
	sys.exit()

print('\nPROC: Done!\n')