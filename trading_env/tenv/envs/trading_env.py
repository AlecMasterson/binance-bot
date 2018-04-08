import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import gym
from gym import error, spaces, utils
from gym.utils import seeding

plt.style.use('dark_background')
mpl.rcParams.update({"font.size": 15, "axes.labelsize": 15, "lines.linewidth": 1, "lines.markersize": 8})

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
        self.reset()

    def reset(self):
        """Reset the trading environment. Reset rewards, data generator...

        Returns:
            observation (numpy.array): observation of the state
        """
        self._iteration = 0
        self._data_generator.rewind()
        self._total_reward = 0
        self._total_pnl = 0
        self._entry_price = 0
        self._exit_price = 0
        self._closed_plot = False

        for _ in range(self._history_length):
            self._prices_history.append(self._data_generator.next())

        observation = self._get_observation()
        self.state_shape = observation.shape
        self._action = HOLD
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
            self._entry_price = 0
        if action == 'sell':
            reward += 0
            self._exit_price = 0

        self._total_reward += reward

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

    def render(self, savefig=False, filename='myfig'):        # Stole this.... need to figure out... dunno what I want to do here
        """Matlplotlib rendering of each step.

        Args:
            savefig (bool): Whether to save the figure as an image or not.
            filename (str): Name of the image file.
        """
        if self._first_render:
            self._f, self._ax = plt.subplots(len(self._spread_coefficients) + int(len(self._spread_coefficients) > 1), sharex=True)
            if len(self._spread_coefficients) == 1:
                self._ax = [self._ax]
            self._f.set_size_inches(12, 6)
            self._first_render = False
            self._f.canvas.mpl_connect('close_event', self._handle_close)
        if len(self._spread_coefficients) > 1:
            # TODO: To be checked
            for prod_i in range(len(self._spread_coefficients)):
                bid = self._prices_history[-1][2 * prod_i]
                ask = self._prices_history[-1][2 * prod_i + 1]
                self._ax[prod_i].plot([self._iteration, self._iteration + 1], [bid, bid], color='white')
                self._ax[prod_i].plot([self._iteration, self._iteration + 1], [ask, ask], color='white')
                self._ax[prod_i].set_title('Product {} (spread coef {})'.format(prod_i, str(self._spread_coefficients[prod_i])))

        # Spread price
        prices = self._prices_history[-1]
        bid, ask = calc_spread(prices, self._spread_coefficients)
        self._ax[-1].plot([self._iteration, self._iteration + 1], [bid, bid], color='white')
        self._ax[-1].plot([self._iteration, self._iteration + 1], [ask, ask], color='white')
        ymin, ymax = self._ax[-1].get_ylim()
        yrange = ymax - ymin
        if (self._action == self._actions['sell']).all():
            self._ax[-1].scatter(self._iteration + 0.5, bid + 0.03 * yrange, color='orangered', marker='v')
        elif (self._action == self._actions['buy']).all():
            self._ax[-1].scatter(self._iteration + 0.5, ask - 0.03 * yrange, color='lawngreen', marker='^')
        plt.suptitle('Cumulated Reward: ' + "%.2f" % self._total_reward + ' ~ ' + 'Cumulated PnL: ' + "%.2f" % self._total_pnl + ' ~ ' + 'Position: ' +
                     ['flat', 'long', 'short'][list(self._position).index(1)] + ' ~ ' + 'Entry Price: ' + "%.2f" % self._entry_price)
        self._f.tight_layout()
        plt.xticks(range(self._iteration)[::5])
        plt.xlim([max(0, self._iteration - 80.5), self._iteration + 0.5])
        plt.subplots_adjust(top=0.85)
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
