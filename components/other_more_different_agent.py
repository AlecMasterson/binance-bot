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
    window_length = 10
    coinpairs = []
    balance = utilities.STARTING_BALANCE
    a_counts = []

    def __init__(self, coinpairs):
        self.coinpairs = coinpairs
        for coinpair in self.coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            if temp_data is None: return 1

            self.data[coinpair] = temp_data[temp_data['INTERVAL'] == utilities.BACKTEST_CANDLE_INTERVAL_STRING].sort_values(by=['OPEN_TIME']).reset_index(drop=True)
            self.windows[coinpair] = deque(maxlen=self.window_length)

        self.backtest = Backtest(self.step, self.data)
        self.i = 0
        self.a_counts = [0 for c in range(len(self.coinpairs) + 1)]

        with open('binance-bot/agents/tf_configs/ppo.json', 'r') as fp:
            agent_config = json.load(fp=fp)
        with open('binance-bot/agents/tf_configs/dqn_relu_network.json', 'r') as fp:
            network_spec = json.load(fp=fp)
        self.brain = tf_agent.from_spec(
            spec=agent_config,
            kwargs={
                'states': {
                    'type': 'float',
                    'shape': (len(self.coinpairs) * self.window_length * 18,)
                },
                'actions': {
                    'type': 'int',
                    'num_actions': len(self.coinpairs) + 1
                },
                'network': network_spec
            }
        )

    def reset(self):
        self.i = 0
        for coinpair in self.coinpairs:
            self.windows[coinpair] = deque(maxlen=self.window_length)
        self.backtest.reset()
        self.a_counts = [0 for c in range(len(self.coinpairs) + 1)]

    def run(self):
        return self.backtest.backtest()

    def step(self, data):
        self.i += 1
        self.remember(data)
        # print(len(self.consider()), self.consider())
        # if self.i == 1:
        #     print(data)
        #     print(self.windows)
        action = self.brain.act(self.consider())
        actions = [False] * len(self.coinpairs)
        try:
            actions[action] = True
        except:
            pass
        self.a_counts[action] += 1
        actions = self.map_actions(actions)
        reward = data['BALANCE'] - self.balance
        # print('old balance: {:>10.3} | new balance: {:>10.3} | reward: {:>10.3}'.format(self.balance, data['BALANCE'], reward))
        self.balance = data['BALANCE']
        if self.i <= 1440:
            self.brain.observe(reward=reward, terminal=False)
        return actions

    def remember(self, data):
        if self.i == 1:
            # print("fine dining and breathing")
            for _ in range(self.window_length+1):
                for k in data:
                    if k != 'BALANCE':
                        self.windows[k].append(data[k])
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
    for x in range(1, 1000 + 1):
        result = agent.run()
        reward = (result - utilities.STARTING_BALANCE) * 10
        print('epoch:{:>5} | balance: {:>10.3} | reward: {:>10.3} | actions: {}'.format(x, result, reward, agent.a_counts))
        agent.brain.observe(reward=reward, terminal=True)
        agent.reset()
