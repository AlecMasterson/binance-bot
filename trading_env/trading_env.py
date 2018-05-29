import logging
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.preprocessing import normalize

import helpers

# plt.style.use('dark_background')
mpl.rcParams.update({"font.size": 10, "axes.labelsize": 10, "lines.linewidth": 1, "lines.markersize": 8, "figure.figsize": (30, 15), "axes.xmargin": 0.1, "axes.ymargin": 0.1})
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


class TradingEnv():

    def __init__(self, data_generator, episode_length, trading_fee, time_fee, history_length, s_c1, s_c2, buy_sell_scalar, hold_scalar, timeout_scalar):

        self.s_c1 = s_c1
        self.s_c2 = s_c2
        self.data_generator = data_generator
        self.first_render = True
        self.trading_fee = trading_fee
        self.episode_length = episode_length
        self.action_space = 2
        self.history_length = history_length

        self.time_fee = time_fee
        self.buy_sell_scalar = buy_sell_scalar
        self.hold_scalar = hold_scalar
        self.timeout_scalar = timeout_scalar
        self.observation_shape = self.reset().shape

    def reset(self):

        self.w_c1 = self.s_c1
        self.w_c2 = self.s_c2
        self.total_value = 0
        self.iteration = 0
        self.data_generator.rewind()
        self.total_reward = 0
        self.reward = 0
        self.action = 2
        self.done = False

        self.buy_price = 0
        self.sell_price = 0
        self.last_buysell_value = 0
        self.swap = 0

        self.coin_min_trade = 0.001

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
        self.macd_history = []
        self.upperband_history = []
        self.lowerband_history = []

        self.action_history = []
        self.step_history = []
        self.reward_history = []
        self.total_reward_history = []
        self.total_value_history = []

        for _ in range(self.history_length):
            self.ingest_data()

        observation = self.get_observation()
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
        try:
            self.macd_history.append(float(self.row['macd']))
        except BaseException:
            self.macd_history.append(float(0))
        try:
            self.upperband_history.append(float(self.row['upperband']))
        except BaseException:
            self.upperband_history.append(float(0))
        try:
            self.lowerband_history.append(float(self.row['lowerband']))
        except BaseException:
            self.lowerband_history.append(float(0))

    def get_observation(self):

        # def pad_to_hist(a):
        #     return np.pad(a, (0, self.history_length - len(a)), 'constant')

        # hist_temp = normalize(
        #     np.stack([
        #         [price for price in self.open_history[-self.history_length:]],
        # # [price for price in self.high_history[-self.history_length:]],[price for price in self.low_history[-self.history_length:]],
        #         # [price for price in self.volume_history[-self.history_length:]],
        # #   [price for price in self.QAV_history[-self.history_length:]], [price for price in self.TBAV_history[-self.history_length:]],
        # #   [price for price in self.TQAV_history[-self.history_length:]], [price for price in self.NT_history[-self.history_length:]],
        #         pad_to_hist(np.array([price for price in self.total_value_history[-self.history_length:]])),
        #         pad_to_hist(np.array([price for price in self.macd_history[-self.history_length:]])),
        #         pad_to_hist(np.array([price for price in self.upperband_history[-self.history_length:]])),
        #         pad_to_hist(np.array([price for price in self.lowerband_history[-self.history_length:]]))
        #     ]).T)

        obs = np.array([
        # hist_temp,
        # np.array([
            int(self.w_c1 > self.w_c2),
            int(self.total_value > self.last_buysell_value),
            int(self.open_history[-1] > self.buy_price),
            int(self.open_history[-1] < self.sell_price),
            int(1 if np.poly1d(self.open_history[-5:])[0] >= 0 else -1),
            int(1 if np.poly1d(self.open_history[-25:])[0] >= 0 else -1),
            int(1 if np.poly1d(self.open_history[-100:])[0] >= 0 else -1),
            self.action,
            self.reward
        # ])
        ])

        return obs

    def step(self, action):

        self.action = action
        self.iteration += 1

        if action == 'trade' or action == 0:
            reward = -1 * self.buy_sell_scalar
            if not self.swap:
                self.buy_price = self.open_history[-1]
                self.w_c1, self.w_c2 = helpers.buy_env(self.w_c1, self.w_c2, self.buy_price, self.trading_fee)
                self.last_buysell_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
                self.swap = 1
            else:
                self.sell_price = self.open_history[-1]
                self.w_c1, self.w_c2 = helpers.sell_env(self.w_c1, self.w_c2, self.sell_price, self.trading_fee)
                self.last_buysell_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
                self.swap = 0
        elif action == 'hold' or action == 1:
            try:
                overhold = max(self.action_history[-100:].count('hold'), self.action_history[-100:].count(1), 1)
                temp = (np.tanh(helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1]) - self.last_buysell_value) - (self.time_fee * overhold))
                # reward =  self.time_fee * overhold * self.hold_scalar
                # temp = np.poly1d(self.open_history[-self.history_length:])[0]
                # if self.last_buysell_value == 0:
                #     self.last_buysell_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
                # temp = (helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1]) - self.last_buysell_value)
                reward = 1 if temp >= 0 else -1
                reward = reward * self.hold_scalar

            except BaseException:
                reward = 0
        else:
            reward = -10000

        # Game over logic
        self.total_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
        info = {}
        done = False
        try:
            self.ingest_data()
        except StopIteration:
            done = True
            reward = 1
            reward += self.total_value - self.s_c1
            reward = reward * self.timeout_scalar * 100
            print('\n Out of data', reward)
        if self.iteration >= self.episode_length:
            done = True
            reward = 1
            reward += self.total_value - self.s_c1
            reward = reward * self.timeout_scalar * 100
            print('\n Time out', reward)
        if self.total_value <= (self.s_c1 * 0.01):
            done = True
            reward += np.tanh(self.iteration / self.data_generator.file_length)
            reward = reward * self.timeout_scalar
            print('\n Total Value too low', reward)

        self.done = done

        self.reward = reward
        self.total_reward += reward

        self.reward_history.append(self.reward)
        self.total_reward_history.append(self.total_reward)
        self.total_value_history.append(self.total_value)

        self.step_history.append({'action': action, 'price': self.open_history[-1], 'iteration': self.iteration, 'reward': reward, 'total_reward': self.total_reward})
        self.action_history.append(action)

        info['w_c1'] = self.w_c1
        info['w_c2'] = self.w_c2
        info['total_value'] = self.total_value
        info['reward'] = self.reward
        info['total_reward'] = self.total_reward

        observation = self.get_observation()
        return observation, reward, done, info

    def render(self, window_size=20, savefig=False, filename='myfig', mode='human'):
        """Matlplotlib rendering of each step.
        Args:
            savefig (bool): Whether to save the figure as an image or not.
            filename (str): Name of the image file.
        """
        if mode == 'human':
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

        f, ax = plt.subplots()
        # f.canvas.mpl_connect('close_event', self.handle_close)
        ax.plot([x['iteration'] for x in self.step_history], [x['price'] for x in self.step_history], color='black', label='Price')

        ymin, ymax = ax.get_ylim()
        yrange = ymax - ymin
        for i in self.step_history:
            itera, act, p = i['iteration'], i['action'], i['price']
            # if (act == 'sell' or act == 1):
            #     ax.scatter(itera + 0.5, p + 0.03 * yrange, color='red', marker='v')
            if (act == 'trade' or act == 0):
                ax.scatter(itera + 0.5, p - 0.03 * yrange, color='blue', marker='^')

        if plot_reward:
            extras['reward'] = self.reward_history

        if plot_total_reward:
            extras['total_reward'] = self.total_reward_history

        if plot_total_value:
            extras['total_value'] = self.total_value_history

        for name, l in extras.items():
            nax = ax.twinx()
            nax.plot([x['iteration'] for x in self.step_history], np.pad(l, (self.history_length - 1, 0), 'constant', constant_values=(0)), label=name, c=np.random.rand(3,))
        nax.legend()

        f.tight_layout()

        if savefig:
            print('Saving', os.path.dirname(os.path.dirname(__file__)) + 'agents/training_images/' + filename)
            plt.savefig(os.path.dirname(os.path.dirname(__file__)) + '/agents/training_images/' + filename, dpi=320)

        # f.tight_layout()
        # plt.show(block=False)
