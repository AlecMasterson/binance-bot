from collections import deque
import sys, os, json
from copy import deepcopy
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'scripts'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'agents'))
import utilities, helpers, signals
from Backtest import Backtest

import numpy as np
from tensorforce.agents import Agent as tf_agent
from tensorforce.agents import DQNAgent


class Agent:

    data = {}
    saved_data = {}
    windows = {}
    i = 0
    coinpairs = []
    balance = 0

    def __init__(self, coinpairs):
        self.coinpairs = coinpairs
        for coinpair in self.coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            if temp_data is None: return 1

            self.data[coinpair] = temp_data[temp_data['INTERVAL'] == utilities.BACKTEST_CANDLE_INTERVAL_STRING].sort_values(by=['OPEN_TIME']).reset_index(drop=True)
            self.windows[coinpair] = deque(maxlen=1)

        self.backtest = Backtest(self.step, self.data)
        self.i = 0

        with open('binance-bot/agents/tf_configs/dqn_relu_network.json', 'r') as fp:
            agent_config = json.load(fp=fp)
        with open('binance-bot/agents/tf_configs/dqn_relu_network.json', 'r') as fp:
            network_spec = json.load(fp=fp)
        # self.brain = tf_agent.from_spec(
        #     spec=agent_config, kwargs={
        #         'states': {
        #             'type': 'float',
        #             'shape': (len(self.coinpairs) * 18,)
        #         },
        #         'actions': {
        #             'type': 'int',
        #             'num_actions': len(self.coinpairs) + 1
        #         },
        #         'network': network_spec
        #     }
        # )
        # self.brain = tf_agent.from_spec(spec=agent_config, kwargs=dict(states=np.array(len(self.coinpairs) * 18,), actions=np.array(len(self.coinpairs) + 1,), network=network_spec))
        self.brain = DQNAgent(
            states=dict(type='float', shape=(len(self.coinpairs) * 18,)),
            actions=dict(type='int', num_actions=len(self.coinpairs) + 1),
            network=[dict(type='dense', size=64), dict(type='dense', size=64)]
        )

    def reset(self):
        self.i = 0
        for coinpair in self.coinpairs:
            self.windows[coinpair] = deque(maxlen=1)
        self.backtest.reset()

    def run(self):
        return self.backtest.backtest()

    def step(self, data):
        self.i += 1
        self.remember(data)
        action = self.brain.act(self.consider())
        actions = [False] * len(self.coinpairs)
        try:
            actions[action] = True
        except:
            pass
        actions = self.map_actions(actions)
        # reward = (data['BALANCE'] - self.balance)/10.0
        # self.balance = data['BALANCE']
        # print(self.balance, reward)
        if self.i <= 1440:
            self.brain.observe(reward=0, terminal=False)
        return actions

    def remember(self, data):
        for k in data:
            if k != 'BALANCE':
                self.windows[k].append(data[k])

    def consider(self):
        return [d[n] for k in self.windows for d in self.windows[k] for n in d if n != 'INTERVAL']

    def act_random(self):
        return np.random.choice([True, False], 3, p=[0.001, 0.999]).tolist()

    def map_actions(self, actions):
        return dict(zip([k for k in self.windows], actions))


if __name__ == '__main__':
    agent = Agent(['ADABTC'])
    for x in range(10):
        result = agent.run()
        print(x, result)
        agent.brain.observe(reward=(result - utilities.STARTING_BALANCE), terminal=True)
        agent.reset()