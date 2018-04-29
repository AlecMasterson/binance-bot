"""
The aim of this file is to give a standalone example of how an environment  runs.
"""

import sys
from os.path import dirname
sys.path.append(dirname(sys.path[0]))

import numpy as np
import time
import helpers

import GPy
import GPyOpt

from trading_env.trading_env import TradingEnv
from trading_env.csvstream import CSVStreamer

generator = CSVStreamer('data_1_hour/ADAETH.csv')
# generator = RandomCSV('data/ADABTC.csv')

episode_length = 100000
trading_fee = 0.001
time_fee = 0
renderwindr = 20
s_c1 = 1
s_c2 = 0
actions = ['hold', 'buy', 'sell']


def decide_action(obs, para_upper, para_lower):
    # return 'hold'
    y = obs['open_history']
    x = range(0, len(y))
    p = np.polyder(np.poly1d(np.polyfit(x, y, 2))).c[0]
    if p <= para_upper:
        return 'sell'
    elif p >= para_lower:
        return 'buy'
    else:
        return 'hold'


# hist_n=3, para_upper=0.000001, para_lower=-0.000001
def run_bot(params):
    # print(params)

    para_upper, para_lower = params[0][0], params[0][1]
    hist_n = 3

    rewards = []
    total_rewards = []
    total_value = []
    done = False

    environment = TradingEnv(data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=hist_n, s_c1=s_c1, s_c2=s_c2)

    # environment.render(window_size=renderwindr)
    observation = environment.reset()
    while not done:
        action = decide_action(observation, para_upper, para_lower)
        observation, done, info = environment.step(action)
        # environment.render(window_size=renderwindr)
        # time.sleep(0.001)

    # 'Reward': rewards, 'Total reward': total_rewards,
    # environment.final_render(extras={'Total value': total_value})
    print(hist_n, para_upper, para_lower, info['total_value'])

    return -1 * info['total_value']


# -3.44645752e-06  3.51521520e-06
def optimize():
    bounds = [{
        'name': 'para_upper',
        'type': 'continuous',
        'domain': (-0.00005, -0.0),
        'dimensionality': 1
    }, {
        'name': 'para_upper',
        'type': 'continuous',
        'domain': (0.0, 0.00005),
        'dimensionality': 1
    }]

    opt = GPyOpt.methods.BayesianOptimization(run_bot, bounds, verbosity=True, Initial_design_numdata=50, Initial_design_type='latin', num_cores=4)

    # Run the optimization
    max_iter = 10000        # evaluation budget
    max_time = 60        # time budget
    eps = 1e-8        # Minimum allows distance between the las two observations

    opt.run_optimization(max_iter, max_time, eps)

    print(opt.x_opt)
    opt.plot_convergence()
    print('done')

optimize()
# print(run_bot([[-3.44645752e-06, 3.51521520e-06]]))