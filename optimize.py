from bayes_opt import BayesianOptimization
from back import baye
import pandas, sys

# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def optimize(data):
	try:
		bo = BayesianOptimization(
			lambda arc, thinup, thindown, power, low, hi: baye(
				data[len(data.index)-240:].reset_index(), {
					'arc': arc, 'thinup': thinup,
					'thindown': thindown, 'power': power,
					'low': low, 'hi': hi
				}
			), {
				'arc': (3.0, 3.0), 'thinup': (1.00, 9.99),
				'thindown': (-9.99, -1.00), 'power': (-22, -16),
				'low': (0.9600, 0.9900), 'hi': (1.0001, 1.0100)
			}
		)
		bo.maximize(init_points=50, n_iter=1, kappa=2)
		return bo.res['max']
	except:
		print('\nERROR: Unknown Error During Optimization!\n')
		sys.exit()



# ------------------------------------------------------------------------------



if __name__ == "__main__":

	# --------------------------------------------------------------------------
	# COMMAND USAGE VERIFICATION
	# --------------------------------------------------------------------------

	if len(sys.argv) != 2:
		print('\nERROR: Command Usage -> \'python3 optimize.py <data-file>\'\n')
		sys.exit()

	print('\nPROC: Bayesian Optimization for '+sys.argv[1]+'\n')

	# --------------------------------------------------------------------------
	# SETUP
	# --------------------------------------------------------------------------

	try:
		print('IO: Looking For Data...')
		data = pandas.read_csv(sys.argv[1])
		print('Found!\n')
	except:
		print('\nERROR: Data Not Found!\n')
		sys.exit()

	# Actually optimize it.
	print('\nRESULTS\n\n'+str(optimize(data)))

	print('\nPROC: Done!\n')