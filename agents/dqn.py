import random
import shutil
import sys
from collections import deque
from os import environ
from os.path import dirname
from time import time

import numpy as np
from keras.models import Sequential, Model
from keras.layers import Flatten, Dense, Conv1D, Input, Reshape, Dropout, LeakyReLU
from keras.optimizers import Adam, RMSprop, Nadam
from keras.utils import plot_model
from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.layers.merge import concatenate

sys.path.append(dirname(sys.path[0]))

from trading_env.csvstream import CSVStreamer
from trading_env.trading_env import TradingEnv

# environ["CUDA_VISIBLE_DEVICES"] = "-1"

EPISODES = 10000000
batch_size = 16
data_csvs = ['data_5_min/ADABTC.csv', 'data_5_min/BNBBTC.csv', 'data_5_min/ETHBTC.csv', 'data_5_min/ICXBTC.csv', 'data_5_min/LTCBTC.csv', 'data_5_min/IOTAETH.csv']


class DQNAgent:

    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=100000)
        self.gamma = 0.9        # discount rate
        self.epsilon = 1.1        # exploration rate
        self.epsilon_min = 0.0000000
        self.epsilon_decay = 0.95
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):

        # kernel_length = min(int(self.state_size / 100), 10)

        # history_cnn_input = Input(shape=(self.state_size,))
        # history_cnn_out = Reshape((1, self.state_size))(history_cnn_input)
        # history_cnn_out = Conv1D(filters=64, kernel_size=3, padding='same')(history_cnn_out)
        # history_cnn_out = LeakyReLU(alpha=0.1)(history_cnn_out)
        # history_cnn_out = Conv1D(filters=48, kernel_size=3, padding='same')(history_cnn_out)
        # history_cnn_out = LeakyReLU(alpha=0.1)(history_cnn_out)
        # history_cnn_out = Conv1D(filters=32, kernel_size=3, padding='same')(history_cnn_out)
        # history_cnn_out = LeakyReLU(alpha=0.1)(history_cnn_out)
        # history_cnn_out = Flatten()(history_cnn_out)
        # history_cnn_out = Dense(max(int(self.state_size * 0.5), 10))(history_cnn_out)
        # history_cnn_out = LeakyReLU(alpha=0.1)(history_cnn_out)
        # # history_cnn_out = Dropout(0.1)(history_cnn_out)
        # history_cnn_out = Dense(max(int(self.state_size * 0.2), 10))(history_cnn_out)
        # history_cnn_out = LeakyReLU(alpha=0.1)(history_cnn_out)
        # history_cnn_out = Dense(10)(history_cnn_out)
        # history_cnn_out = LeakyReLU(alpha=0.1)(history_cnn_out)
        # history_cnn_out = Dense(self.action_size)(history_cnn_out)
        # history_cnn_out = LeakyReLU(alpha=0.1)(history_cnn_out)
        # brain = Model(input=history_cnn_input, output=history_cnn_out)
        # brain.compile(optimizer=Nadam(lr=self.learning_rate), metrics=['mae', 'mse', 'accuracy'], loss='mae')

        simple_input = Input(shape=(self.state_size,))
        simple_output = Dense(max(int(self.state_size * 4), 10))(simple_input)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(max(int(self.state_size * 3), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dropout(0.1)(simple_output)
        simple_output = Dense(max(int(self.state_size * 2), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(max(int(self.state_size * 1), 10))(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        simple_output = Dense(self.action_size)(simple_output)
        simple_output = LeakyReLU(alpha=0.3)(simple_output)
        brain = Model(inputs=simple_input, outputs=simple_output)
        brain.compile(optimizer=Adam(lr=self.learning_rate), loss='mae', metrics=['mae'])

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
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)


if __name__ == "__main__":
    el = 10e10
    hl = 100
    bss = 1
    hs = 1
    ts = 0

    # generator = CSVStreamer(data_csvs[int(np.random.randint(len(data_csvs), size=1))])
    generator = CSVStreamer(data_csvs[0])
    env = TradingEnv(data_generator=generator, episode_length=el, trading_fee=0.01, time_fee=0.001, history_length=hl, s_c1=1, s_c2=0, buy_sell_scalar=bss, hold_scalar=hs, timeout_scalar=ts)
    state_size = env.observation_shape[0]
    action_size = env.action_space
    agent = DQNAgent(state_size, action_size)
    done = False

    # try:
    #     agent.load('./agents/save/dqn.h5')
    #     agent.epsilon = 1
    #     agent.epsilon_decay = 0.5
    # except:
    #     pass

    while len(agent.memory) < 100000:        # prep memory buffer
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

        episode_end_time = time()
        print("episode: {}/{}, time: {:.4}, e: {:.4}, steps: {}, total reward: {}, total value: {}, buy: {}, hold: {}, source: {}".format(
            e, EPISODES, episode_end_time - episode_start_time, agent.epsilon, env.iteration, env.total_reward, env.total_value, env.action_history[:].count(0), env.action_history[:].count(1),
            generator.filename))

        done = False
        if e % 10 == 0:
            print('\nSAVING', agent.model.history.history)
            print('Reward history:', list(zip(env.action_history[:5], env.reward_history[:5])))
            print('Reward history:', list(zip(env.action_history[-5:], env.reward_history[-5:])))
            print(agent.model.predict(state, verbose=0))
            # if agent.epsilon <= agent.epsilon_min:
            #     agent.epsilon += np.random.uniform(0, 0.01, 1)[0]
            agent.save("./agents/save/dqn.h5")
