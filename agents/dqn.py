import random
import shutil
import sys
from collections import deque
from itertools import chain
from os import environ
from os.path import dirname
from time import time
from datetime import datetime
from tqdm import tqdm

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

EPISODES = 100000
batch_size = 2**11
# data_csvs = ['data/history/ADABTC.csv', 'data/history/BNBBTC.csv', 'data/history/EOSBTC.csv', 'data/history/ICXBTC.csv', 'data/history/LTCBTC.csv', 'data/history/XLMBTC.csv']
data_csvs = ['data/history/ADABTC.csv', 'data/history/BNBBTC.csv', 'data/history/EOSBTC.csv']
# data_csvs = ['data/history/ADABTC.csv']


class DQNAgent:

    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=1000000)
        self.gamma = 1.5        # discount rate
        self.epsilon = 1.5        # exploration rate
        self.noise_level = 3
        self.epsilon_decay = 0.7
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.callbacks = [
        # ReduceLROnPlateau(monitor='loss', factor=0.1, patience=30, verbose=1, mode='auto', min_delta=0.0001, cooldown=25, min_lr=0.0001),
        # TensorBoard(log_dir='./TBlogs/' + datetime.now().strftime("%Y%m%d-%H%M%S"), histogram_freq=0, batch_size=64, write_graph=True, write_grads=True, write_images=True)
        ]
        self.n_steps = 0
        self.ti = [1252, 1511, 1839, 1933, 3910, 4227, 8834, 10209, 16195, 17072, 22000, 23271, 24000, 24727, 27130, 28130, 36760, 37730]

    def _build_model(self):

        print('MODEL NOISE LEVEL', self.noise_level)

        simple_input = Input(shape=(1,self.state_size))
        # simple_input = Reshape((1,self.state_size), input_shape=(1,self.state_size))
        simple_output = Dense(max(int(self.state_size * 0.7), 10), activation='tanh')(simple_input)
        simple_output = Dense(max(int(self.state_size * 0.5), 10), activation='tanh')(simple_output)
        # simple_output = Dropout(0.1)(simple_output)
        simple_output = Dense(max(int(self.state_size * 0.3), 10), activation='tanh')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.3), 10), activation='tanh')(simple_output)
        simple_output = Dense(max(int(self.state_size * 0.1), 10), activation='tanh')(simple_output)
        # simple_output = Dropout(0.1)(simple_output)
        # simple_output = NoisyDense(max(int(self.state_size * 0.05), 10), activation='tanh', sigma_init=self.noise_level, name='fuzzy05')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.05), 10), activation='tanh')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.05), 10), activation='tanh')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.05), 10), activation='tanh')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.05), 10), activation='tanh')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.05), 10), activation='tanh')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.05), 10), activation='tanh')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.05), 10), activation='tanh')(simple_output)
        # simple_output = NoisyDense(max(int(self.state_size * 0.03), 10), activation='tanh', sigma_init=self.noise_level, name='fuzzy03')(simple_output)
        # simple_output = Dense(max(int(self.state_size * 0.03), 10), activation='tanh')(simple_output)
        simple_output = Dense(max(int(self.state_size * 0.03), 10), activation='tanh')(simple_output)
        simple_output = Dense(max(int(self.state_size * 0.01), 10), activation='tanh')(simple_output)
        simple_output = Dense(self.action_size, activation='linear')(simple_output)
        brain = Model(inputs=simple_input, outputs=simple_output)
        brain.compile(optimizer=Adam(lr=self.learning_rate), loss='mse')
        # print(brain.summary())

        self.noise_level *= 0.9

        return brain

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def predict(self, state):
        state = np.reshape(state, (1, 1, -1))
        return self.model.predict([state])[0]

    def act(self, state):
        self.n_steps += 1
        if np.random.rand() <= self.epsilon:
            if self.n_steps in self.ti:
                print(self.n_steps, 'ACTING BASED ON BI')
                return 0
            return 1
        act_values = self.predict(state)
        return int(np.argmax(act_values[0]))

    def resetENV(self):
        self.random_trades = 0
        self.random_holds = 0
        self.n_steps = 0

    def replay(self, batch_size):
        x = []
        y = []
        # try:
        #     minibatch = random.sample(self.memory, int(self.n_steps*2))
        # else:
        #     minibatch = random.sample(self.memory, int(self.n_steps))
        # print(random.sample(self.memory, batch_size).shape)
        # print(np.array([self.memory[i] for i in range(-500, 0, 1)]).shape)
        minibatch = random.sample(self.memory, batch_size) + [self.memory[i] for i in range(-500, 0, 1)]
        # print(minibatch[-1], minibatch.shape)
        for state, action, reward, next_state, done in tqdm(minibatch, desc='Building training set', ncols=100):
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(self.predict(next_state)))
            target_f = self.predict(state)
            target_f[0][action] = target
            x += [state]
            y += [target_f]
        self.model.fit(np.array(x), np.array(y), epochs=1, verbose=1)
        self.resetENV()

    def update_epsilon(self, denom):
        self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


if __name__ == "__main__":
    el = 10e6
    hl = 1
    bss = 100
    hs = 10
    ts = 10000
    tws = 100

    generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
    # generator = CSVStreamer(data_csvs[0])
    env = TradingEnv(
        data_generator=generator,
        episode_length=el,
        trading_fee=0.01,
        time_fee=0.001,
        history_length=hl,
        s_c1=1,
        s_c2=0,
        buy_sell_scalar=bss,
        hold_scalar=hs,
        timeout_scalar=ts,
        temporal_window_size=tws)
    state_size = env.observation_shape[1]
    action_size = env.action_space
    agent = DQNAgent(state_size, action_size)
    done = False
    total_steps = 0

    # try:
    #     agent.load('./agents/save/dqn.h5')
    #     agent.epsilon = 1.0
    #     agent.epsilon_decay = 0.5
    #     print('SUCCESSFULLY LOADED')
    # except:
    #     print('FAILED TO LOAD')
    #     pass

    while len(agent.memory) < 1000:        # prep memory buffer
        generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
        env = TradingEnv(
            data_generator=generator,
            episode_length=el,
            trading_fee=0.01,
            time_fee=0.001,
            history_length=hl,
            s_c1=1,
            s_c2=0,
            buy_sell_scalar=bss,
            hold_scalar=hs,
            timeout_scalar=ts,
            temporal_window_size=tws)
        episode_start_time = time()
        # state = np.reshape(env.reset(), [1, state_size])
        state = env.reset()
        while not done:
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            # next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state
        done = False
        agent.resetENV()
        print('Memory Length: {:10,}'.format(len(agent.memory)), end='\r')

    print('\n\n\nTRAINING')

    for e in range(EPISODES):
        generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
        env = TradingEnv(
            data_generator=generator,
            episode_length=el,
            trading_fee=0.01,
            time_fee=0.001,
            history_length=hl,
            s_c1=1,
            s_c2=0,
            buy_sell_scalar=bss,
            hold_scalar=hs,
            timeout_scalar=ts,
            temporal_window_size=tws)

        # state = np.reshape(env.reset(), [1, state_size])
        state = env.reset()
        while not done:
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            # next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state

        total_steps += env.iteration
        print("episode: {:6}/{:6} | e: {:3.2} | steps: {:5} | memory: {:10,} | total reward: {:14,} | total value: {:8.4} | trade: {:3} | hold: {:6} | source: {}".format(
            e, EPISODES, agent.epsilon, env.iteration, len(agent.memory), round(env.total_reward, 4), env.total_value, env.action_history[:].count(0), env.action_history[:].count(1),
            generator.filename))

        if len(agent.memory) > batch_size:
            agent.replay(batch_size)

        done = False
        if e % 3 == 0:
            print('\nSAVING', agent.model.history.history)
            print(agent.predict(state))
            agent.update_epsilon(total_steps)
            agent.save("./agents/save/dqn.h5")
            agent._build_model()
            agent.load('./agents/save/dqn.h5')
