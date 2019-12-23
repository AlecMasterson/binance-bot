from collections import deque
import sys, os, json
from copy import deepcopy
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'scripts'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'agents'))
import utilities, helpers, signals, Backtest, Plot

from termcolor import colored
import numpy as np
from tensorforce.agents import Agent as tf_agent
from tensorforce.agents import DQNAgent


class Agent:

    windows = {}
    window_length = 10
    coinpairs = []
    a_counts = []

    def __init__(self, coinpairs):
        """Initializes Agent brain
        
        Args:
            coinpairs ([string]): coinpair strings
        """

        self.coinpairs = coinpairs
        self.reset()

        # Loads brain settings and network config from files
        with open('binance-bot/agents/tf_configs/ppo.json', 'r') as fp:
            agent_config = json.load(fp=fp)
        with open('binance-bot/agents/tf_configs/dqn_relu_network.json', 'r') as fp:
            network_spec = json.load(fp=fp)

        # Creates brain from loaded configs and specifies I/O as state/actions
        self.brain = tf_agent.from_spec(
            spec=agent_config,
            kwargs={
                'states': {
                    'type': 'float',
                    'shape': (len(self.coinpairs) * self.window_length * 17,)
                },
                'actions': {
                    'type': 'int',
                    'num_actions': len(self.coinpairs) + 1
                },
                'network': network_spec
            }
        )

    def reset(self):
        """Resets the agent for a new episode... basically just forgets the windows right now
        """

        for coinpair in self.coinpairs:
            self.windows[coinpair] = deque(maxlen=self.window_length)
        self.a_counts = [0 for c in range(len(self.coinpairs) + 1)]

    def remember(self, data):
        """Takes the data for the new epoch and stores it
        
        Args:
            data ({dataframes}): candle info
        """

        if len(self.windows[self.coinpairs[0]]) == 0:        #fine dining and breathing
            for _ in range(self.window_length + 1):
                for k in data:
                    if k != 'BALANCE':
                        self.windows[k].append(data[k])
        for k in data:
            if k != 'BALANCE':
                self.windows[k].append(data[k])

    def consider(self):
        """Transforms the windows into data that would fit into the brain's expected state format
        
        Returns:
            [floats]: all the more number-y values in the candles (raw for now)
        """

        return [d[n] for k in self.windows for d in self.windows[k] for n in d if n not in ('INTERVAL', 'OPEN_TIME', 'IGNORE')]

    def act(self, state):
        """ Given a state, return an action
        
        Args:
            state (dict{dataframes}): candle info
        
        Returns:
            {bool}: A dict with {coinpair: bool} for whether to buy
        """

        self.remember(state)
        # print(self.consider(), len(self.consider()))
        action = self.brain.act(self.consider())
        self.a_counts[action] += 1
        actions = [False] * len(self.coinpairs)
        try:        # if the action maps to one of the coinpairs' index then mark it as true, else hold
            actions[action] = True
        except:
            pass
        actions = self.map_actions(actions)
        return actions

    def act_random(self):
        """Like the brain.act but does so randomly with a 1/1000 chance of buying
        
        Returns:
            [bool]: action bools
        """

        return np.random.choice([True, False], len(self.coinpairs), p=[0.001, 0.999]).tolist()

    def map_actions(self, actions):
        """Combines the coinpairs to the actions the agent has creates by index resulting in {self.coinpairs[0]: actions[0], and so on}
        
        Args:
            actions ([bools]): list of actions from brain or random
        
        Returns:
            {coinpair: action}: the zipped together coinpairs and their actions
        """

        return dict(zip(self.coinpairs, actions))


def prep_data(coinpairs):
    """loads data from files... basically helper magic
    
    Args:
        coinpairs ([str]): coinpairs
    
    Returns:
        {dataframe}: dict of dataframes for coinpairs
    """

    data = {}
    for coinpair in coinpairs:
        temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
        if temp_data is None: return False
        data[coinpair] = temp_data
    return data


if __name__ == '__main__':

    ### Agent/Env initialization ###
    coinpairs = ['ADABTC']
    data = prep_data(coinpairs)
    print(list(data['ADABTC'].columns.values))
    env = Backtest.Backtest(data, utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.BACKTEST_CANDLE_INTERVAL, utilities.STARTING_BALANCE, utilities.MAX_POSITIONS, 24)
    agent = Agent(coinpairs)

    ### Training metrics ###
    ## global metrics ##
    episode_history = deque(maxlen=100)
    steps = 0
    ## episode metrics ##
    g_rewards = []
    g_actions = []
    g_balances = []

    ### Training loop ###
    for x in range(1, 10000 + 1):

        ## reset ##
        done = False
        state, response, done, _ = env.reset()
        agent.reset()
        ep_rewards = []

        ## episode loop ##
        while not done:
            steps += 1
            actions = agent.act(state)
            state, response, done, _ = env.step(actions)
            reward = response['POTENTIAL']
            ep_rewards += [reward]
            if not done:
                agent.brain.observe(reward=reward, terminal=False)
        agent.brain.observe(reward=reward, terminal=True)

        g_rewards += [np.sum(ep_rewards)]
        g_actions += [agent.a_counts]
        g_balances += [response['BALANCE']]

        color = 'green' if g_balances[-1] > 1 else 'red'
        print(colored('episode report #:{:>10} | balance:{:>10.5} | reward:{:>15.10} | actions: {}'.format(x, g_balances[-1], g_rewards[-1], g_actions[-1]), color))

        if x % 10 == 0:
            color = 'green' if np.mean(g_balances[-10:]) > 1 else 'red'
            print(colored('training report | steps:{:>15} | avgn balance:{:>10.5} | avgn reward:{:>15.10}'.format(steps, np.mean(g_balances[-10:]), np.mean(g_rewards[-10:])), color))
