import random
import shutil
import sys
import argparse
from collections import deque
from itertools import chain
from os import environ
from os.path import dirname
import pandas as pd
from time import time
from datetime import datetime
from tqdm import tqdm
from keras_tqdm import TQDMCallback
import termplot

import numpy as np
from sklearn.preprocessing import minmax_scale
from keras.models import Sequential, Model
from keras.layers import Flatten, Dense, Conv1D, Input, Reshape, Dropout, LeakyReLU, GRU, Concatenate
from keras.optimizers import Adam, RMSprop, Nadam, Adadelta
from keras.regularizers import l1_l2, l1, l2
from keras.utils import plot_model
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
# from keras.layers.merge import concatenate
from nalu import NALU
from NoisyDense import NoisyDense

sys.path.append(dirname(sys.path[0]))

from trading_env.csvstream import CSVStreamer
from trading_env.trading_env import TradingEnv

environ["CUDA_VISIBLE_DEVICES"] = "-1"

EPISODES = 1000000
batch_size = 2**8
lera = 0.000001
el = 10e7
hl = 1
bss = 1
hs = 1
ts = 20
# data_csvs = ['data/history/ADABTC.csv', 'data/history/BNBBTC.csv', 'data/history/EOSBTC.csv', 'data/history/ICXBTC.csv', 'data/history/LTCBTC.csv', 'data/history/XLMBTC.csv']

data_csvs = ['data/history/ADABTC.csv']


class DQNAgent:

    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=500_000)
        self.input_memory_size = 20
        self.input_memory = deque(maxlen=self.input_memory_size)
        self.gamma = 0.999        # discount rate
        self.epsilon = 2.0        # exploration rate
        self.epsilon_min = 0.0000001
        self.epsilon_decay = 0.95
        self.model = self._build_model()
        self.random_holds = 0
        self.random_trades = 0
        self.n_steps = 0

    def _build_model(self):

        input = Input(shape=(self.input_memory_size, self.state_size))

        nalu = NALU(max(int(self.state_size * 10), 10), mode='NALU')(input)
        nalu = NALU(max(int(self.state_size * 5), 10), mode='NALU')(nalu)
        nalu = NALU(max(int(self.state_size * 3), 10), mode='NALU')(nalu)
        nalu = GRU(max(int(self.state_size * 5), 10), activation='tanh', return_sequences=False)(nalu)

        rnn = Dense(max(int(self.state_size * 10), 10), activation='tanh')(input)
        rnn = Dense(max(int(self.state_size * 5), 10), activation='tanh')(rnn)
        rnn = Dense(max(int(self.state_size * 3), 10), activation='tanh')(rnn)
        rnn = GRU(max(int(self.state_size * 5), 10), activation='tanh', return_sequences=False)(rnn)

        c = Concatenate()([nalu, rnn])

        densenet = Dense(max(int(self.state_size * 10), 10), activation='tanh')(c)
        # densenet = Dense(max(int(self.state_size * 5), 10), activation='tanh')(densenet)
        # densenet = Dropout(rate=0.05)(densenet)
        densenet = Dense(max(int(self.state_size * 5), 10), activation='tanh')(densenet)
        densenet = Dense(max(int(self.state_size * 1), 10), activation='tanh')(densenet)

        # output = NoisyDense(self.action_size, activation='linear', sigma_init=0.02, name='fuzzyout')(densenet)
        output = Dense(self.action_size, activation='linear')(densenet)
        brain = Model(inputs=input, outputs=output)
        self.compile_model(brain, lera)
        print(brain.summary())
        return brain

    def compile_model(self, model, lr):
        model.compile(optimizer=Adadelta(lr=lr), loss='mse', metrics=['mae'])

    def fine_dining_and_breathing(self, obs):
        [self.input_memory.append(obs) for _ in range(self.input_memory_size)]

    def consider(self, single_obs):
        self.input_memory.append(single_obs)
        return np.array(self.input_memory).reshape(1, self.input_memory_size, self.state_size)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def predict(self, state):
        return self.model.predict([state])[0]

    def act(self, state):
        self.n_steps += 1
        if np.random.rand() <= self.epsilon:
            if np.random.choice(2, 1, p=[0.001, 0.999])[0] == 0 or self.epsilon < 0.001:
                self.random_trades += 1
                return 0
            self.random_holds += 1
            return 1
        act_values = self.predict(state)
        return int(np.argmax(act_values))

    def resetENV(self):
        self.random_trades = 0
        self.random_holds = 0
        self.n_steps = 0

    def replay_all(self, batch_size):
        x = []
        y = []
        # minibatch = [x for x in self.memory if x[1] == 0][-batch_size:] + [x for x in self.memory if x[1] == 1][-batch_size:] + [x for x in self.memory if x[2] <= -1][-batch_size:] + random.sample(self.memory, batch_size)
        # minibatch = random.sample(minibatch, batch_size)
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in tqdm(minibatch, desc='Building training set'):
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(self.predict(next_state)))
            target_f = self.predict(state)
            target_f[action] = target
            x += [state]
            y += [[target_f]]
        return self.model.fit(
            np.array(x).reshape(batch_size, self.input_memory_size, self.state_size),
            np.array(y).reshape(batch_size, self.action_size),
            epochs=64,
            batch_size=16,
            shuffle=True,
            verbose=0,
            callbacks=[TQDMCallback(metric_format="{name}: {value:e}"), EarlyStopping(monitor='loss', min_delta=0, patience=10, verbose=0)])

    def update_epsilon(self, denom):
        self.epsilon = self.epsilon * self.epsilon_decay if self.epsilon > self.epsilon_min else self.epsilon_min * 10.0

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


def train():
    generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
    env = TradingEnv(data_generator=generator, episode_length=el, trading_fee=0.01, time_fee=0.001, history_length=hl, s_c1=1, s_c2=0, buy_sell_scalar=bss, hold_scalar=hs, timeout_scalar=ts)
    state_size = env.observation_shape[1]
    action_size = env.action_space
    agent = DQNAgent(state_size, action_size)
    done = False
    total_steps = 0
    performance = []
    # trade_indexes = [2181, 3254, 5064, 5332, 9021, 10362, 14000, 14990, 16196, 17470, 21560, 28065, 36715, 38000, 41000, 41745, 45433, 47000, 52876, 53278, 55000]
    # level = 0
    # best_value = 0
    try:
        agent.load('./agents/save/dqn.h5')
        agent.epsilon = 0.01
        print('SUCCESSFULLY LOADED')
    except:
        print('FAILED TO LOAD')
        pass

    for e in range(EPISODES):
        generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
        env.set_generator(generator)
        obs = env.reset()
        #overwrite memory
        agent.fine_dining_and_breathing(obs)
        state = agent.consider(obs)

        print("\n\nepisode: {:6}/{:6}|e: {:3.2}|source: {}".format(e, EPISODES, agent.epsilon, generator.filename))
        pbar = tqdm(total=generator.file_length, desc='Running episode')
        while not done:
            action = agent.act(state)
            new_obs, reward, done, _ = env.step(action)
            next_state = agent.consider(new_obs)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            pbar.update(1)
        pbar.close()

        color = "\033[0;32m" if (env.action_history[:].count(0) > agent.random_trades) and (env.total_value >= 1.0) else "\033[0;0m"
        color = "\033[0;31m" if (env.action_history[:].count(0) > agent.random_trades) and (env.total_value <= 1.0) else color
        total_steps += env.iteration
        # |noise: t({:.2})/h({:.2})
        print("{}steps: {:5}|memory: {:12,}|total reward: {:10.8}|total value: {:5.3}|trade: {:2}|hold: {:5}|random: t({})/h({}) \033[0;0m".format(
            color, env.iteration, len(agent.memory),
            # agent.model.get_layer('fuzzyout').get_weights()[1][0][0],
            # agent.model.get_layer('fuzzyout').get_weights()[1][1][0],
             float(env.total_reward), float(env.total_value), env.action_history[:].count(0), env.action_history[:].count(1), agent.random_trades, agent.random_holds))
        # Plot the relative trade locations
        try:
            print('\n Trades:')
            termplot.plot(list(np.histogram([e for e, x in enumerate(env.action_history) if x == 0], bins=100)[0]), plot_height=10, plot_char='*')
        except:
            pass

        if len(agent.memory) >= 10_000:
            history = agent.replay_all(batch_size)
        agent.resetENV()
        performance += [env.total_reward]
        try:
            print('\n Reward:')
            termplot.plot(performance[-150:], plot_height=10, plot_char='=')
        except Exception as ex:
            print(ex)

        done = False
        if e % 1 == 0:
            print('\nSAVING')
            print('LAST PREDICTION', agent.predict(state))
            agent.update_epsilon(total_steps)
            agent.save('./agents/save/dqn.h5')
            print('\n')


def test():

    generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
    env = TradingEnv(data_generator=generator, episode_length=el, trading_fee=0.01, time_fee=0.001, history_length=hl, s_c1=1, s_c2=0, buy_sell_scalar=bss, hold_scalar=hs, timeout_scalar=ts)
    state_size = env.observation_shape[1]
    action_size = env.action_space
    agent = DQNAgent(state_size, action_size)
    done = False
    total_steps = 0
    trade_act_values = []
    hold_act_values = []

    agent.load('./agents/save/dqn.h5')
    agent.epsilon = 0.0

    obs = env.reset()
    #overwrite memory
    agent.fine_dining_and_breathing(obs)
    state = agent.consider(obs)
    print("source: {}".format(generator.filename))
    pbar = tqdm(total=generator.file_length, desc='Running episode')
    while not done:
        act_values = agent.model.predict([state])[0]
        trade_act_values.append(act_values[0])
        hold_act_values.append(act_values[1])
        if env.iteration == 10:
            act_values = [1, 0]
        action = int(np.argmax(act_values))
        new_obs, _, done, _ = env.step(action)
        next_state = agent.consider(new_obs)
        state = next_state
        pbar.update(1)
        # if env.iteration >= 10000:        #and len([x for x in env.action_history if x == 0]) == 0:
        #     done = True
    pbar.close()

    color = "\033[0;32m" if (env.action_history[:].count(0) > agent.random_trades) and (env.total_value >= 1.0) else "\033[0;0m"
    color = "\033[0;31m" if (env.action_history[:].count(0) > agent.random_trades) and (env.total_value <= 1.0) else color
    total_steps += env.iteration
    print("{}steps: {:5}|memory: {:9,}|total reward: {:10.8}|total value: {:5.3}|trade: {:2}|hold: {:5}|random: t({})/h({}) \033[0;0m".format(color, env.iteration, len(agent.memory), float(env.total_reward), float(env.total_value),
                                                                                                                                              env.action_history[:].count(0), env.action_history[:].count(1), agent.random_trades, agent.random_holds))

    try:
        pd.DataFrame.from_dict(
            data={
                'action': env.action_history[1:],
                'swap': env.swap_history[1:],
                'reward': env.reward_history,
                'total_reward': env.total_reward_history,
                'total_value': env.total_value_history,
                'open': env.open_history,
                'trade_act_values': trade_act_values,
                'hold_act_values': hold_act_values
            }
        ).to_csv('./agents/save/dqn_run.csv')
    except:
        print("Didn't finish")
        pad = len(env.open_history[:-1]) - len(trade_act_values) + 1
        pd.DataFrame.from_dict(
            data={
                'action': env.action_history[1:],
                'swap': env.swap_history[1:],
                'reward': env.reward_history,
                'total_reward': env.total_reward_history,
                'total_value': env.total_value_history,
                'open': env.open_history[pad:],
                'trade_act_values': trade_act_values,
                'hold_act_values': hold_act_values
            }
        ).to_csv('./agents/save/dqn_run.csv')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action="store_true", default=False)
    parser.add_argument('--test', action="store_true", default=False)
    args = parser.parse_args()
    print(args)
    if args.train:
        train()
    if args.test:
        test()
