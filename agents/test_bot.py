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
from trading_env.tenv.envs.gens.random import RandomWalk

generator = RandomWalk(val=100, multiplier=22, bias=2)
# generator = SineSignal(period_1=3, period_2=5, epsilon=1, bias=0.0)

episode_length = 200
trading_fee = 0.2
time_fee = 0
# history_length number of historical states in the observation vector.
history_length = 6

environment = TradingEnv(data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=history_length)

environment.render()
while True:
    # action = input("Action: Buy (b) / Sell (s) / Hold (enter): ")
    # if action == 'b':
    #     action = 'buy'
    # elif action == 's':
    #     action = 'sell'
    # else:
    #     action = 'hold'
    action = np.random.choice(a=['buy', 'sell', 'hold'], size=1, p=[0.05, 0.05, 0.9])
    print(action)
    environment.step(action)
    environment.render()
    time.sleep(0.1)
