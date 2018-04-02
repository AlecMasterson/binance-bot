from bayes_opt import BayesianOptimization
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
	# TODO: Manually edit this to accommodate your unique bot.
	# arg1... are the arguments that are passed into your function 'fun'.
	# (0, 1) are the min/max of each argument's search area.
	bo = BayesianOptimization(
		lambda arg1, arg2, arg3: fun(
			data, {
				'arg1': arg1, 'arg2': arg2, 'arg3': arg3
			}
		), {
			'arg1': (0, 1), 'arg2': (0, 1), 'arg3': (0, 1)
		}
	)

	# TODO: Manually edit this to accommodate your unique bot.
	bo.maximize(init_points=10, n_iter=15, kappa=2)
except:
	print('\nERROR: Unknown Error During Optimization!\n')
	sys.exit()

print('\nPROC: Done!\n')