import logging
import os
import sys
from collections import deque
from itertools import chain
import math

# import matplotlib as mpl
# import matplotlib.pyplot as plt
import numpy as np
# import seaborn as sns
from sklearn.preprocessing import minmax_scale

import helpers


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
        self.buy_index = 0
        self.sell_price = 1
        self.sell_index = 0
        self.swap = 0

        self.coin_min_trade = 0.1
        self.over_trade_threshold = 10
        self.over_hold_threshold = 10000

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

        self.action_history = [self.action]
        self.swap_history = [self.swap]
        self.reward_history = []
        self.total_reward_history = []
        self.total_value_history = []

        for _ in range(self.history_length):
            self.ingest_data()

        return self.get_observation()

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

        # obs = np.append(obs, [self.action == 0])
        # obs = np.append(obs, [self.action == 1])
        # obs = np.append(obs, [self.swap == 0])
        # obs = np.append(obs, [self.swap == 1])
        # obs = np.append(obs, [self.reward])
        # rat = np.average(self.reward_history[-10:])
        # obs = np.append(obs, [rat if not np.isnan(rat) else 0])
        # rat = np.average(self.reward_history[-100:])
        # obs = np.append(obs, [rat if not np.isnan(rat) else 0])

        try:
            obs = np.append(obs, [((self.open_history[-1] / self.sell_price) - self.sell_price) - 1])
        except:
            obs = np.append(obs, [0])
        try:
            obs = np.append(obs, [((self.open_history[-1] / self.buy_price) - self.buy_price) - 1])
        except:
            obs = np.append(obs, [0])
        # for l in [
        #     self.open_history, self.high_history, self.low_history, self.volume_history, self.QAV_history, self.TBAV_history, self.TQAV_history, self.NT_history, self.macd_history,
        #     self.upperband_history, self.lowerband_history
        # ]:
        for l in [self.open_history, self.action_history, self.swap_history]:
            obs = np.append(obs, l[-self.history_length:])

        return np.reshape(obs, [1, obs.shape[0]])

    def step(self, action):
        if action == 0:
            if not self.swap:
                self.buy_price = self.open_history[-1]
                reward = -self.trading_fee + ((self.buy_price - self.sell_price) / self.sell_price) * -1
                self.w_c1, self.w_c2 = helpers.buy_env(self.w_c1, self.w_c2, self.buy_price, self.trading_fee)
                self.swap = 1
                self.buy_index = self.iteration
            else:
                self.sell_price = self.open_history[-1]
                reward = -self.trading_fee + ((self.sell_price - self.buy_price) / self.buy_price)
                self.w_c1, self.w_c2 = helpers.sell_env(self.w_c1, self.w_c2, self.sell_price, self.trading_fee)
                self.swap = 0
                self.sell_index = self.iteration
            reward *= self.buy_sell_scalar
        else:
            try:
                reward = ((self.open_history[-1] - self.open_history[-2]) / self.open_history[-2]) * (1 if self.swap == 1 else -1)
            except:
                reward = 0

        # Game over logic
        self.total_value = helpers.combined_total_env(self.w_c1, self.w_c2, self.open_history[-1])
        try:
            self.ingest_data()
        except:
            self.done = True
        if self.iteration >= self.episode_length:
            self.done = True

        # if action == 1 and len([x for x in self.action_history[-self.over_hold_threshold:] if x == 0]) == 0:
        #     # print('Over hold')
        #     reward = -2 * self.timeout_scalar
        #     # self.done = True
        # if action == 0 and len([x for x in self.action_history[-self.over_trade_threshold:] if x == 0]) >= 1:
        #     # print('Over trade')
        #     reward = -2 * self.timeout_scalar
        #     # self.done = True
        if self.total_value <= (self.s_c1 * self.coin_min_trade):
            reward = -1 * self.timeout_scalar
            self.done = True

        if self.done:
            reward += (self.total_value - self.s_c1)*self.timeout_scalar
        else:
            reward += 0.00001

        self.reward = reward
        self.total_reward += reward
        self.action = action
        self.iteration += 1

        self.reward_history.append(self.reward)
        self.total_reward_history.append(self.total_reward)
        self.total_value_history.append(self.total_value)

        self.action_history.append(action)
        self.swap_history.append(self.swap)

        return self.get_observation(), self.reward, self.done, {}
