from collections import deque
import sys, os, json
from copy import deepcopy
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'scripts'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'agents'))
import utilities, helpers, signals, Backtest, Plot

import numpy as np
from tensorforce.agents import Agent as tf_agent
from tensorforce.agents import DQNAgent


weird_data_prep_args = (utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.BACKTEST_CANDLE_INTERVAL, 24)

class Agent:

    windows = {}
    i = 0
    window_length = 10
    coinpairs = []
    balance = utilities.STARTING_BALANCE
    a_counts = []
    caw = []

    def __init__(self, coinpairs):
        self.coinpairs = coinpairs
        self.reset()

        with open('binance-bot/agents/tf_configs/ppo.json', 'r') as fp:
            agent_config = json.load(fp=fp)
        with open('binance-bot/agents/tf_configs/dqn_relu_network.json', 'r') as fp:
            network_spec = json.load(fp=fp)
        self.brain = tf_agent.from_spec(
            spec=agent_config,
            kwargs={
                'states': {
                    'type': 'float',
                    'shape': (len(self.coinpairs) * self.window_length * 19,)
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
        self.a_counts = [0 for c in range(len(self.coinpairs) + 1)]
        self.caw = [0 for c in range(len(self.coinpairs) + 1)]

    def remember(self, data):
        if self.i == 1:        #fine dining and breathing
            for _ in range(self.window_length + 1):
                for k in data:
                    if k != 'BALANCE':
                        self.windows[k].append(data[k])
        for k in data:
            if k != 'BALANCE':
                self.windows[k].append(data[k])

    def consider(self):
        return [d[n] for k in self.windows for d in self.windows[k] for n in d if n != 'INTERVAL']

    def act(self, state):
        self.i += 1
        self.remember(state)
        # print(self.consider(), len(self.consider()))
        action = self.brain.act(self.consider())
        actions = [False] * len(self.coinpairs)
        try:
            actions[action] = True
        except:
            pass
        actions = self.map_actions(actions)
        self.a_counts[action] += 1
        # print('old balance: {:>10.3} | new balance: {:>10.3} | reward: {:>10.3}'.format(self.balance, data['BALANCE'], reward))
        return actions

    def act_random(self):
        return np.random.choice([True, False], 3, p=[0.001, 0.999]).tolist()

    def map_actions(self, actions):
        return dict(zip([k for k in self.windows], actions))


def prep_data(coinpairs):
    data = {}
    for coinpair in coinpairs:
        temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
        temp_data = Backtest.format_data(temp_data, *weird_data_prep_args)
        if temp_data is None: return False
        data[coinpair] = temp_data
    return data


if __name__ == '__main__':
    reward_history = deque([0] * 10, maxlen=10)

    coinpairs = ['ADABTC']

    env = Backtest.Backtest(prep_data(coinpairs))
    agent = Agent(coinpairs)

    for x in range(1, 1000 + 1):

        done = False
        state, response, done, _ = env.reset(*weird_data_prep_args, utilities.MAX_POSITIONS)
        agent.reset()
        i = 0
        while not done:
            i+=1
            print(x, i)
            actions = agent.act(state)
            state, response, done, _ = env.step(actions)
            if not done:
                agent.brain.observe(reward=0, terminal=False)

        reward = (response['BALANCE'] - utilities.STARTING_BALANCE)
        reward_history.append(reward)
        print(
            'epoch:{:>5} | balance: {:>10.5} | reward: {:>10.5} | avgn reward: {:>10.5} | actions: {}'.format(
                x, response['BALANCE'], reward,
                sum(reward_history) / reward_history.maxlen, agent.a_counts
            )
        )
        agent.brain.observe(reward=reward, terminal=True)
