import logging
import os
import sys
from collections import deque
from itertools import chain
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.preprocessing import minmax_scale

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
    }
)


class TradingEnv():

    def __init__(self, data_generator, episode_length, trading_fee, time_fee, history_length, s_c1, s_c2, buy_sell_scalar, hold_scalar, timeout_scalar, temporal_window_size):

        self.s_c1 = s_c1
        self.s_c2 = s_c2
        self.data_generator = data_generator
        self.first_render = True
        self.trading_fee = trading_fee
        self.episode_length = episode_length
        self.action_space = 2
        self.history_length = history_length
        self.temporal_window_size = temporal_window_size
        self.temporal_window = deque(maxlen=self.temporal_window_size)

        self.time_fee = time_fee
        self.buy_sell_scalar = buy_sell_scalar
        self.hold_scalar = hold_scalar
        self.timeout_scalar = timeout_scalar
        self.over_trade_threshold = 100
        self.over_hold_threshold = 10000
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
        self.sell_price = 1
        self.last_buysell_value = 1
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
        self.swap_history = []
        self.step_history = []
        self.reward_history = []
        self.total_reward_history = []
        self.total_value_history = []
        [self.temporal_window.append([0] * 21) for _ in range(self.temporal_window.maxlen + 1)]

        for _ in range(self.history_length):
            self.ingest_data()

        observation = self.get_observation()
        return observation

    def set_generator(self, gen):
        self.data_generator = gen

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

        def sig(x):
            return 1 / (1 + math.exp(-x))

        obs = np.array([])

        obs = np.append(obs, [self.action == 0])
        obs = np.append(obs, [self.action == 1])
        obs = np.append(obs, [self.swap == 0])
        obs = np.append(obs, [self.swap == 1])
        try:
            obs = np.append(obs, sig(self.action_history[::-1].index(0)))
        except:
            obs = np.append(obs, [1])
        try:
            obs = np.append(obs, sig(self.action_history[::-1].index(1)))
        except:
            obs = np.append(obs, [1])
        # obs = np.append(obs, [self.action_history[-self.over_trade_threshold:].count(0) / self.over_trade_threshold])
        obs = np.append(obs, [self.action_history[-self.over_hold_threshold:].count(1) / self.over_hold_threshold])
        obs = np.append(obs, [self.buy_price / self.open_history[-1]])
        obs = np.append(obs, [self.sell_price / self.open_history[-1]])
        obs = np.append(obs, [helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])])

        for l in [
            self.open_history, self.high_history, self.low_history, self.volume_history, self.QAV_history, self.TBAV_history, self.TQAV_history, self.NT_history, self.macd_history,
            self.upperband_history, self.lowerband_history
        ]:
            obs = np.append(obs, [sig(price) for price in l[-self.history_length:]])

        self.temporal_window.append(obs)
        obs = np.array(list(chain.from_iterable(self.temporal_window)))
        return np.reshape(obs, [1, obs.shape[0]])

    def step(self, action):

        self.action = action
        self.iteration += 1
        done = False
        reward = 0

        if action == 0:
            if not self.swap:
                self.buy_price = self.open_history[-1]
                self.w_c1, self.w_c2 = helpers.buy_env(self.w_c1, self.w_c2, self.buy_price, self.trading_fee)
                reward = self.last_buysell_value
                self.last_buysell_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
                reward = self.last_buysell_value - reward
                self.swap = 1
            else:
                self.sell_price = self.open_history[-1]
                # reward = np.arctanh((self.sell_price - (self.buy_price * 1.01))) * self.buy_sell_scalar
                self.w_c1, self.w_c2 = helpers.sell_env(self.w_c1, self.w_c2, self.sell_price, self.trading_fee)
                reward = self.last_buysell_value
                self.last_buysell_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
                reward = self.last_buysell_value - reward
                self.swap = 0
            reward = np.where(reward > 0, reward, 0)
            # print(action, reward)
        # elif action == 1:
        #     try:
        #         # reward = ((helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1]) / self.last_buysell_value) - 1.0) * 0.1 * self.hold_scalar
        #         reward -= np.arctanh((self.action_history[-self.over_hold_threshold:][::-1].index(0) / self.over_hold_threshold)) * 0.000001 * self.hold_scalar
        #         # reward = np.where(reward > 0, 1.0, 0.0)

        #     except Exception as e:
        #         # print(e)
        #         reward -= np.arctanh((self.action_history[-self.over_hold_threshold:].count(1) / self.over_hold_threshold)) * 0.000001 * self.hold_scalar
        #over act
        # if self.action_history[-self.over_hold_threshold:].count(1) >= self.over_hold_threshold:
        #     reward = -100.0
        #     done = True
        # if self.action_history[-self.over_trade_threshold:].count(0) >= self.over_trade_threshold:
        #     reward = -100.0
        #     done = True

        # Game over logic
        self.total_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
        info = {}
        try:
            self.ingest_data()
        except:
            done = True
            # reward = 1.0
            # reward += self.total_value - self.s_c1
            # reward *= self.timeout_scalar
            # reward = np.where(reward > 0, reward, reward * 0.01)
            # print('STOPPED: out of data')
        if self.iteration >= self.episode_length:
            done = True
            # reward = 1.0
            # reward += self.total_value - self.s_c1
            # reward *= self.timeout_scalar
            # reward = np.where(reward > 0, reward, reward * 0.01)
            # print('STOPPED: time out')
        if self.total_value <= (self.s_c1 * 0.001):
            done = True
            # reward = -1.0
            # reward += np.tanh(self.iteration / self.data_generator.file_length)
            # reward *= self.timeout_scalar
            # print('STOPPED: total value too low')

        # if done:
        #     reward += -1000000.0 if self.action_history[:].count(0) == 0 else 0.1
        #     reward += -1000000.0 if self.action_history[:].count(1) == 0 else 0.1

        # print(action, reward)
        self.done = done

        self.reward = reward
        self.total_reward += reward

        self.reward_history.append(self.reward)
        self.total_reward_history.append(self.total_reward)
        self.total_value_history.append(self.total_value)

        self.step_history.append({'action': action, 'price': self.open_history[-1], 'iteration': self.iteration, 'reward': reward, 'total_reward': self.total_reward})
        self.action_history.append(action)
        self.swap_history.append(self.swap)

        info['action'] = action
        info['w_c1'] = self.w_c1
        info['w_c2'] = self.w_c2
        info['total_value'] = self.total_value
        info['reward'] = self.reward
        info['total_reward'] = self.total_reward
        info['done'] = done
        info['iteration'] = self.iteration

        observation = self.get_observation()
        return observation, reward, done, info

    def close(self):
        #TODO something
        return -1