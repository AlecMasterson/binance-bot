import random
import shutil
import sys
from collections import deque
from itertools import chain
from os import environ
from os.path import dirname
from time import time
from datetime import datetime

import numpy as np
from keras.models import Sequential, Model
from keras.layers import Flatten, Dense, Conv1D, Input, Reshape, Dropout, LeakyReLU
from keras.optimizers import Adam, RMSprop, Nadam
from keras.utils import plot_model
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau
from keras.layers.merge import concatenate
from NoisyDense import NoisyDense

sys.path.append(dirname(sys.path[0]))

from trading_env.csvstream import CSVStreamer
from trading_env.trading_env import TradingEnv

# environ["CUDA_VISIBLE_DEVICES"] = "-1"

EPISODES = 10000000
batch_size = 8
# data_csvs = ['data/history/ADABTC.csv', 'data/history/BNBBTC.csv', 'data/history/EOSBTC.csv', 'data/history/ICXBTC.csv', 'data/history/LTCBTC.csv', 'data/history/XLMBTC.csv']
data_csvs = ['data/history/ADABTC.csv']


class DQNAgent:

    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=1000000)
        self.gamma = 0.98        # discount rate
        self.epsilon = 1.0        # exploration rate
        self.epsilon_start = 1.0
        self.epsilon_min = 0.0000000
        self.epsilon_decay = 0.7
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.callbacks = [
            ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=10, verbose=1, mode='auto', min_delta=0.0001, cooldown=25, min_lr=0.0001),
            TensorBoard(log_dir='./TBlogs/' + datetime.now().strftime("%Y%m%d-%H%M%S"), histogram_freq=0, batch_size=64, write_graph=True, write_grads=True, write_images=True)
        ]

    def _build_model(self):

        simple_input = Input(shape=(self.state_size,))
        simple_output = Dense(max(int(self.state_size * 4), 10))(simple_input)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(max(int(self.state_size * 3), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dropout(0.01)(simple_output)
        simple_output = Dense(max(int(self.state_size * 3), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dropout(0.01)(simple_output)
        simple_output = Dense(max(int(self.state_size * 2), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(max(int(self.state_size * 2), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(max(int(self.state_size * 2), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(max(int(self.state_size * 2), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(max(int(self.state_size * 1), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = NoisyDense(self.action_size, activation='linear', sigma_init=0.02, name='output')(simple_output)
        brain = Model(inputs=simple_input, outputs=simple_output)
        brain.compile(optimizer=Adam(lr=self.learning_rate), loss='mae', metrics=['mae'])
        print(brain.summary())
        plot_model(brain, show_shapes=True, to_file='brain.png')
        return brain

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                # print('next_state', next_state, type(next_state), next_state.shape)
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0, callbacks=[])

    def update_epsilon(self, denom):
        self.epsilon = self.epsilon_start / denom

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


if __name__ == "__main__":
    el = 10e6
    hl = 1
    bss = 1
    hs = 1
    ts = 10000

    # generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
    generator = CSVStreamer(data_csvs[0])
    env = TradingEnv(data_generator=generator, episode_length=el, trading_fee=0.01, time_fee=0.001, history_length=hl, s_c1=1, s_c2=0, buy_sell_scalar=bss, hold_scalar=hs, timeout_scalar=ts)
    state_size = env.observation_shape[0]
    action_size = env.action_space
    agent = DQNAgent(state_size, action_size)
    done = False
    total_steps = 0

    # try:
    #     agent.load('./agents/save/dqn.h5')
    #     # agent.epsilon = 1.0
    #     # agent.epsilon_decay = 0.5
    #     print('SUCCESSFULLY LOADED')
    # except:
    #     print('FAILED TO LOAD')
    #     pass

    while len(agent.memory) < 10000:        # prep memory buffer
        generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
        env = TradingEnv(data_generator=generator, episode_length=el, trading_fee=0.01, time_fee=0.001, history_length=hl, s_c1=1, s_c2=0, buy_sell_scalar=bss, hold_scalar=hs, timeout_scalar=ts)
        episode_start_time = time()
        state = np.reshape(env.reset(), [1, state_size])
        while not done:
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state
        done = False
        print('Memory Length: {}'.format(len(agent.memory)))

    for e in range(EPISODES):
        generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
        env = TradingEnv(data_generator=generator, episode_length=el, trading_fee=0.01, time_fee=0.001, history_length=hl, s_c1=1, s_c2=0, buy_sell_scalar=bss, hold_scalar=hs, timeout_scalar=ts)
        episode_start_time = time()
        state = np.reshape(env.reset(), [1, state_size])
        while not done:
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state

        # print('Memory Length: {}'.format(len(agent.memory)))

        if len(agent.memory) > batch_size:
            agent.replay(batch_size)

        total_steps += env.iteration
        episode_end_time = time()
        print("episode: {:,}/{:,} | time: {:.4} | e: {:.4} | steps: {:,} | total steps: {:,} | total reward: {:.4} | total value: {:.4} | buy: {} | hold: {} | source {}".format(
            e, EPISODES, episode_end_time - episode_start_time, agent.epsilon, env.iteration, total_steps, env.total_reward, env.total_value, env.action_history[:].count(0),
            env.action_history[:].count(1), generator.filename))

        done = False
        if e % 10 == 0:
            print('\nSAVING', agent.model.history.history)
            print('Reward history:', list(zip(env.action_history[:5], env.reward_history[:5])))
            print('Reward history:', list(zip(env.action_history[-5:], env.reward_history[-5:])))
            print(agent.model.predict(state, verbose=0))
            if agent.epsilon >= agent.epsilon_min:
                agent.update_epsilon(total_steps)
            agent.save("./agents/save/dqn.h5")
