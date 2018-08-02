import random
import shutil
import sys
from collections import deque
from itertools import chain
from os import environ
from os.path import dirname
from time import time
from datetime import datetime

import numpy as np

sys.path.append(dirname(sys.path[0]))

from trading_env.csvstream import CSVStreamer
from trading_env.trading_env import TradingEnv

data_csvs = ['data/history/ADABTC.csv', 'data/history/BNBBTC.csv', 'data/history/EOSBTC.csv', 'data/history/ICXBTC.csv', 'data/history/LTCBTC.csv', 'data/history/XLMBTC.csv']

generator = CSVStreamer(data_csvs[0])
env = TradingEnv(
    data_generator=generator, episode_length=10e6, trading_fee=0.01, time_fee=0.001, history_length=1, s_c1=1, s_c2=0, buy_sell_scalar=1, hold_scalar=11000, timeout_scalar=1, temporal_window_size=1)

loa = [1] * generator.file_length
ti = [1252, 1511, 1839, 1933, 3910, 4227, 8834, 10209, 16195, 17072, 22000, 23271, 24000, 24727, 27130, 28130, 36760, 37730]
for i in ti:
    loa[i] = 0

done = False

while not done:
    action = loa[env.iteration]
    _, reward, done, info = env.step(action)
    # print(info)

print('REWARD', env.total_reward, 'VALUE', env.total_value)
