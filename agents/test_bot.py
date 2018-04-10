"""
The aim of this file is to give a standalone example of how an environment  runs.
"""

import sys
from os.path import dirname
sys.path.append(dirname(sys.path[0]))

import numpy as np
import time

from trading_env.tenv.envs.trading_env import TradingEnv
from trading_env.tenv.envs.gens.deterministic import SineSignal
from trading_env.tenv.envs.gens.random import RandomCSV
from trading_env.tenv.envs.gens.csvstream import CSVStreamer

# generator = CSVStreamer('data/ADABTC.csv')
generator = RandomCSV('data/ADABTC.csv')

episode_length = 10000
trading_fee = 0.2
time_fee = 0
history_length = 6
done = False
renderwindr = 24 * 7

environment = TradingEnv(
    data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=history_length)

environment.render(window_size=renderwindr)
while not done:
    action = np.random.choice(a=['buy', 'sell', 'hold'], size=1, p=[0.05, 0.05, 0.9])
    # print(action)
    _, _, done, _ = environment.step(action)
    environment.render(window_size=renderwindr)
    # time.sleep(0.001)
