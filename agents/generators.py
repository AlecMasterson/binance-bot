"""
In this example we show how a random generator is coded.
All generators inherit from the DataGenerator class
The class yields tuple (bid_price,ask_price)
"""
import sys
from os.path import dirname
sys.path.append(dirname(sys.path[0]))

import numpy as np
from trading_env.tenv.envs.gens.random import RandomWalk
from trading_env.tenv.envs.gens.deterministic import SineSignal

time_series_length = 10
# mygen = RandomWalk(val=123, bias=2)
# mygen = SineSignal(period_1=3, period_2=5, epsilon=1, bias=0.0)
mygen = SineSignal(3, 5, 1, 0)
prices_time_series = [next(mygen) for _ in range(time_series_length)]
print(prices_time_series)
