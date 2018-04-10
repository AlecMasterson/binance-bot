import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import gym
from gym import error, spaces, utils
from gym.utils import seeding

# plt.style.use('dark_background')
sns.set_style(
    "ticks", {
        'axes.axisbelow': True,
        'axes.edgecolor': '.8',
        'axes.facecolor': 'white',
        'axes.grid': False,
        'axes.labelcolor': '.15',
        'axes.linewidth': 1,
        'figure.facecolor': 'white',
        'grid.color': '.8',
        'lines.solid_capstyle': u'round',
        'text.color': '.15',
        'xtick.color': '.15',
        'xtick.direction': u'out',
        'ytick.color': '.15',
        'ytick.direction': u'out'
    })
sns.despine(offset=10, trim=True)
mpl.rcParams.update({"font.size": 10, "axes.labelsize": 10, "lines.linewidth": 1, "lines.markersize": 8, "figure.figsize": (13, 5), "axes.xmargin": 0.1, "axes.ymargin": 0.1})

HOLD = np.array([1, 0, 0])
BUY = np.array([0, 1, 0])
SELL = np.array([0, 0, 1])


class TradingEnv(gym.Env):

    def __init__(self, data_generator, episode_length=(30 * 24), trading_fee=0.1, time_fee=0, history_length=2):
        """Initialisation function

        Args:
            data_generator: A data
                generator object yielding a 1D array of closing prices.
            episode_length (int): number of steps to play the game for (in hours)
            trading_fee (float): penalty for trading (percentage)
            time_fee (float): time fee (of debatable usage)
            history_length (int): number of historical states to stack in the
                observation vector.
        """

        self._data_generator = data_generator
        self._first_render = True
        self._trading_fee = trading_fee
        self._time_fee = time_fee
        self._episode_length = episode_length
        self.action_space = spaces.Discrete(3)
        self._prices_history = []
        self._history_length = history_length
        self.action_history = []
        self.reset()

    def reset(self):
        """Reset the trading environment. Reset rewards, data generator...

        Returns:
            observation (numpy.array): observation of the state
        """
        self.wbtc = 1
        self.walt = 0
        self.action_history = []
        self._iteration = 0
        self._data_generator.rewind()
        self._total_reward = 0
        self._entry_price = 0
        self._exit_price = 0
        self.reward = 0
        self._closed_plot = False

        for _ in range(self._history_length):
            self._prices_history.append(self._data_generator.next())

        observation = self._get_observation()
        self.state_shape = observation.shape
        self._action = 'hold'
        return observation

    def step(self, action):
        """Take an action (buy/sell/hold) and computes the immediate reward.

        Args:
            action (numpy.array): Action to be taken, one-hot encoded.

        Returns:
            tuple:
                - observation (numpy.array): Agent's observation of the current environment.
                - reward (float) : Amount of reward returned after previous action.
                - done (bool): Whether the episode has ended, in which case further step() calls will return undefined results.
                - info (dict): Contains auxiliary diagnostic information (helpful for debugging)

        """

        self._action = action
        self._iteration += 1
        done = False
        info = {}
        reward = -self._time_fee
        if action == 'buy':
            reward += 0
            self._entry_price = self._prices_history[-1]
        elif action == 'sell':
            reward += 0
            self._exit_price = self._prices_history[-1]

        self.reward = reward
        self._total_reward += reward

        self.action_history.append({'action': action, 'price': self._prices_history[-1], 'iteration': self._iteration, 'reward': reward, 'total_reward': self._total_reward})

        # Game over logic
        try:
            self._prices_history.append(self._data_generator.next())
        except StopIteration:
            done = True
            info['status'] = 'No more data.'
        if self._iteration >= self._episode_length:
            done = True
            info['status'] = 'Time out.'
        if self._closed_plot:
            info['status'] = 'Closed plot'

        observation = self._get_observation()
        return observation, reward, done, info

    def _handle_close(self, evt):
        self._closed_plot = True

    def render(self, savefig=False, filename='myfig'):
        """Matlplotlib rendering of each step.
        Args:
            savefig (bool): Whether to save the figure as an image or not.
            filename (str): Name of the image file.
        """
        if self._first_render:
            self._f, self._ax = plt.subplots()
            self._ax = [self._ax]
            self._first_render = False
            self._f.canvas.mpl_connect('close_event', self._handle_close)

        # Plot latest iteration
        self._ax[-1].plot([self._iteration + 0.2, self._iteration + 0.8], [self._prices_history[-1], self._prices_history[-1]], color='black')
        ymin, ymax = self._ax[-1].get_ylim()
        yrange = ymax - ymin
        if (self._action == 'sell'):
            self._ax[-1].scatter(self._iteration + 0.5, self._prices_history[-1] + 0.03 * yrange, color='red', marker='v')
        elif (self._action == 'buy'):
            self._ax[-1].scatter(self._iteration + 0.5, self._prices_history[-1] - 0.03 * yrange, color='green', marker='^')
        plt.suptitle('Iteration: {}, Total Reward: {}, Current Reward: {}, Current Price: {}, Action: {}'.format(self._iteration, self._total_reward, self.reward, self._prices_history[-1], self._action))
        self._f.tight_layout()
        plt.xticks(range(self._iteration)[::5])
        plt.xlim([max(0, self._iteration - 20), self._iteration + 0.5])
        plt.subplots_adjust(top=0.9)
        plt.pause(0.01)
        if savefig:
            plt.savefig(filename)

    def _get_observation(self):
        """Concatenate all necessary elements to create the observation.

        Returns:
            numpy.array: observation array.
        """
        return (np.array([price for price in self._prices_history[-self._history_length:]]) + np.array([self._entry_price]))

    @staticmethod
    def random_action_fun():
        """The default random action for exploration.
        We hold 80% of the time and buy or sell 10% of the time each.

        Returns:
            numpy.array: array with a 1 on the action index, 0 elsewhere.
        """
        return np.random.multinomial(1, [0.8, 0.1, 0.1])
