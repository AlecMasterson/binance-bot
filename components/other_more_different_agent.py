from collections import deque
import sys, os
from copy import deepcopy
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'scripts'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
import utilities, helpers, signals
from Backtest import Backtest

import numpy as np
from tensorforce.agents import DQNAgent


class Agent:

    data = {}
    saved_data = {}
    windows = {}
    i = 0
    coinpairs = []

    def __init__(self, coinpairs):
        self.coinpairs = coinpairs
        for coinpair in self.coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            if temp_data is None: return 1

            self.saved_data[coinpair] = temp_data[temp_data['INTERVAL'] == utilities.BACKTEST_CANDLE_INTERVAL_STRING].sort_values(by=['OPEN_TIME']).reset_index(drop=True)
            self.windows[coinpair] = deque(maxlen=1)

        self.data = deepcopy(self.saved_data)
        self.backtest = Backtest(self.step)
        # Create a Proximal Policy Optimization agent
        self.brain = DQNAgent(states=dict(type='float', shape=(len(self.coinpairs)*18,)), actions=dict(type='int', num_actions=3), network=[dict(type='dense', size=64), dict(type='dense', size=64)])

    def reset(self):
        for coinpair in self.coinpairs:
            self.windows[coinpair] = deque(maxlen=1)
        self.data = deepcopy(self.saved_data)
        self.backtest.reset()

    def run(self):
        return self.backtest.backtest(self.data)

    def step(self, data):
        self.remember(data)
        # print(self.consider().shape)
        action = self.brain.act(self.consider())
        actions = [False]*len(self.coinpairs)
        actions[action] = True
        actions = self.map_actions(actions)
        self.brain.observe(reward=0, terminal=False)
        return actions

    def remember(self, data):
        for k in data:
            self.windows[k].append(data[k])

    def consider(self):
        return [d[n] for k in self.windows for d in self.windows[k] for n in d if n != 'INTERVAL']

    def act_random(self):
        return np.random.choice([True, False], 3, p=[0.001, 0.999]).tolist()

    def map_actions(self, actions):
        return dict(zip([k for k in self.windows], actions))


if __name__ == '__main__':
    agent = Agent(['ADABTC', 'XMRBTC'])
    for x in range(10):
        result = agent.run()
        print(result, len(agent.consider()))
        agent.brain.observe(reward=(result - utilities.STARTING_BALANCE), terminal=True)
        agent.reset()

