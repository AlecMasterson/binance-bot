import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
# import line_profiler

import helpers

# plt.style.use('dark_background')
mpl.rcParams.update({"font.size": 10, "axes.labelsize": 10, "lines.linewidth": 1, "lines.markersize": 8, "figure.figsize": (13, 5), "axes.xmargin": 0.1, "axes.ymargin": 0.1})
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


class TradingEnv():

    def __init__(self, data_generator, episode_length, trading_fee, time_fee, history_length, s_c1, s_c2):
        """Initialisation function

        Args:
            data_generator: A data
                generator object yielding a 1D array of closing prices.
            episode_length (int): number of steps to play the game for (in hours)
            trading_fee (float): penc2y for trading (percentage)
            time_fee (float): time fee applied directly to reward (of debatable usage)
            history_length (int): number of historical states to stack in the
                observation vector.
        """

        self.s_c1 = s_c1
        self.s_c2 = s_c2
        self.data_generator = data_generator
        self.first_render = True
        self.trading_fee = trading_fee
        self.time_fee = time_fee
        self.episode_length = episode_length
        self.action_space = 3
        self.history_length = history_length

    def reset(self):
        """Reset the trading environment. Reset rewards, data generator...

        Returns:
            observation (numpy.array): observation of the state
        """
        self.w_c1 = self.s_c1
        self.w_c2 = self.s_c2
        self.total_value = 0
        self.iteration = 0
        self.data_generator.rewind()
        self.total_reward = 0
        self.reward = 0

        self.buy_price = 0
        self.sell_price = 0

        self.open_history = []
        self.close_history = []
        self.high_history = []
        self.low_history = []
        self.volume_history = []
        self.QAV_history = []
        self.TBAV_history = []
        self.TQAV_history = []
        self.time_history = []
        self.NT_history = []

        self.action_history = []
        self.reward_history = []
        self.total_reward_history = []
        self.total_value_history = []

        for _ in range(self.history_length):
            self.ingest_data()

        observation = self.get_observation()
        self.action = 'hold'
        return observation

    def ingest_data(self):
        self.row = self.data_generator.next()
        self.open_history.append(float(self.row['Open']))
        self.close_history.append(float(self.row['Close']))
        self.high_history.append(float(self.row['High']))
        self.low_history.append(float(self.row['Low']))
        self.volume_history.append(float(self.row['Volume']))
        self.QAV_history.append(float(self.row['Quote Asset Volume']))
        self.TBAV_history.append(float(self.row['Taker Base Asset Volume']))
        self.TQAV_history.append(float(self.row['Take Quote Asset Volume']))
        self.time_history.append(self.row['Open Time'])
        self.NT_history.append(float(self.row['Number Trades']))

    def step(self, action):
        """Take an action (buy/sell/hold) and computes the immediate reward.

        Args:
            action (string): Action to be taken.

        Returns:
            tuple:
                - observation (dictionary): Agent's observation of the current environment.
                - done (bool): Whether the episode has ended, in which case further step() calls will return undefined results.
                - info (dict): Contains auxiliary information
        """

        self.action = action
        self.iteration += 1
        done = False

        w_prev = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])

        if action == 'buy':
            self.buy_price = self.open_history[-1]
            self.w_c1, self.w_c2 = helpers.buy_env(self.w_c1, self.w_c2, self.buy_price, self.trading_fee)
            reward = helpers.combined_total_env(self.w_c1, self.w_c2, self.sell_price) - w_prev
        elif action == 'sell':
            self.sell_price = self.open_history[-1]
            self.w_c1, self.w_c2 = helpers.sell_env(self.w_c1, self.w_c2, self.sell_price, self.trading_fee)
            reward = helpers.combined_total_env(self.w_c1, self.w_c2, self.buy_price) - w_prev
        elif action == 'hold':
            reward = helpers.combined_total_env(self.w_c1, self.w_c2, self.buy_price) - self.time_fee
        else:
            reward = -10000
            print("UNSUPPORTED ACTION")

        self.reward = reward
        self.total_reward += reward
        self.total_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])

        self.reward_history.append(self.reward)
        self.total_reward_history.append(self.total_reward)
        self.total_value_history.append(self.total_value)

        self.action_history.append({'action': action, 'price': self.open_history[-1], 'iteration': self.iteration, 'reward': reward, 'total_reward': self.total_reward})

        # Game over logic
        info = {}
        try:
            self.ingest_data()
        except StopIteration:
            done = True
            info['status'] = 'No more data.'
        if self.iteration >= self.episode_length:
            done = True
            info['status'] = 'Time out.'

        info['w_c1'] = self.w_c1
        info['w_c2'] = self.w_c2
        info['total_value'] = self.total_value
        info['reward'] = self.reward
        info['total_reward'] = self.total_reward

        observation = self.get_observation()
        return observation, done, info

    def get_observation(self):
        """Concatenate all necessary elements to create the observation.

        Returns:
            dict: actionable environment variables.
        """
        return {'open_history': [price for price in self.open_history[-self.history_length:]],
                'close_history': [price for price in self.close_history[-self.history_length:]],
                'high_history': [price for price in self.high_history[-self.history_length:]],
                'low_history': [price for price in self.low_history[-self.history_length:]],
                'volume_history': [price for price in self.volume_history[-self.history_length:]],
                'QAV_history': [price for price in self.QAV_history[-self.history_length:]],
                'TBAV_history': [price for price in self.TBAV_history[-self.history_length:]],
                'TQAV_history': [price for price in self.TQAV_history[-self.history_length:]],
                'NT_history': [price for price in self.NT_history[-self.history_length:]],
                'w_c1': self.w_c1,
                'w_c2': self.w_c2,
                'total_value': self.total_value
        }

    def render(self, window_size=20, savefig=False, filename='myfig', mode='human'):
        """Matlplotlib rendering of each step.
        Args:
            savefig (bool): Whether to save the figure as an image or not.
            filename (str): Name of the image file.
        """
        if mode != 'human':
            if self.first_render:
                self.f, self.ax = plt.subplots()
                self.first_render = False
                # self.f.canvas.mpl_connect('close_event', self.handle_close)

            # Plot latest iteration
            self.ax.plot([self.iteration + 0.2, self.iteration + 0.8], [self.open_history[-1], self.open_history[-1]], color='black')
            ymin, ymax = self.ax.get_ylim()
            yrange = ymax - ymin
            if (self.action == 2):
                self.ax.scatter(self.iteration + 0.5, self.open_history[-1] + 0.03 * yrange, color='red', marker='v')
            elif (self.action == 1):
                self.ax.scatter(self.iteration + 0.5, self.open_history[-1] - 0.03 * yrange, color='green', marker='^')
            plt.suptitle('Iteration: {}, Total Reward: {}, Current Reward: {}, Current Price: {}, Total Value: {}, Action: {}'.format(self.iteration, self.total_reward, self.reward,
                                                                                                                                      self.open_history[-1], self.total_value, self.action))
            self.f.tight_layout()
            plt.xticks(range(self.iteration)[::5])
            plt.xlim([max(0, self.iteration - window_size), self.iteration + 0.5])
            plt.subplots_adjust(top=0.9)
            plt.pause(0.000001)

            for l in self.ax.get_lines():
                xval = l.get_xdata()[0]
                if (xval < self.ax.get_xlim()[0]):
                    l.remove()

            if savefig:
                plt.savefig(filename)

    def final_render(self, savefig=False, filename='myfig', plot_reward=False, plot_total_reward=False, plot_total_value=False, extras={}):
        """Matlplotlib rendering after bot has finished.
        Args:
            savefig (bool): Whether to save the figure as an image or not.
            filename (str): Name of the image file.
            extra (dict(list)): A dictionary of lists to plot on top of the trade history
        """
        f, ax = plt.subplots()
        # f.canvas.mpl_connect('close_event', self.handle_close)

        ax.plot(list(range(-1 * self.history_length, self.iteration - 1)), self.open_history, color='black', label='Price')

        ymin, ymax = ax.get_ylim()
        yrange = ymax - ymin
        for i in self.action_history:
            itera, act, p = i['iteration'], i['action'], i['price']
            if (act == 2):
                ax.scatter(itera + 0.5, p + 0.03 * yrange, color='red', marker='v')
            elif (act == 1):
                ax.scatter(itera + 0.5, p - 0.03 * yrange, color='green', marker='^')

        if plot_reward:
            extras['reward'] = self.rewa

        for name, l in extras.items():
            nax = ax.twinx()
            nax.plot(list(range(-1 * self.history_length, self.iteration - 1)), np.pad(l, (self.history_length - 1, 0), 'constant', constant_values=(0)), label=name)

        if savefig:
            plt.savefig(filename)

        f.tight_layout()
        plt.show()
