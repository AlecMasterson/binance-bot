import random
import shutil
import sys
from collections import deque
from os import environ
from os.path import dirname
from time import time

import numpy as np
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import Adam

from trading_env.csvstream import CSVStreamer
from trading_env.trading_env import TradingEnv

# shutil.rmtree('./tbgraph')
try:
    shutil.rmtree('tbgraph')
except:
    pass
sys.path.append(dirname(sys.path[0]))

environ["CUDA_VISIBLE_DEVICES"] = "-1"

EPISODES = 10000000
batch_size = 32
data_csvs = [
    'data_5_min/BNBBTC.csv',
    'data_5_min/CMTBTC.csv',
    'data_5_min/EOSBTC.csv',
    'data_5_min/ETHBTC.csv',
    'data_5_min/GTOBTC.csv',
    'data_5_min/ICNBTC.csv',
    'data_5_min/ICXBTC.csv',
    'data_5_min/INSBTC.csv',
    'data_5_min/NAVBTC.csv',
    'data_5_min/OMGBTC.csv',
    'data_5_min/REQBTC.csv',
    'data_5_min/SNMBTC.csv',
    'data_5_min/WTCBTC.csv',
    'data_5_min/XLMBTC.csv',
]


class DQNAgent:

    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.9        # discount rate
        self.epsilon = 1.01        # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.01
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(10, input_dim=self.state_size, activation='relu'))
        model.add(Dense(5, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

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
                target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
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
    generator = CSVStreamer(data_csvs)
    env = TradingEnv(data_generator=generator, episode_length=10e10, trading_fee=0.01, time_fee=0.001, history_length=1, s_c1=1, s_c2=0, buy_sell_scalar=0.1, hold_scalar=0.0001, timeout_scalar=100)
    state_size = env.observation_shape[0]
    action_size = env.action_space
    agent = DQNAgent(state_size, action_size)
    done = False

    for e in range(EPISODES):
        episode_start_time = time()
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        while not done:
            # env.render()
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)
            state = next_state

        if len(agent.memory) > batch_size:
            agent.replay(batch_size)

        episode_end_time = time()
        print("episode: {}/{}, time: {}, e: {:.4}, steps: {}, total reward: {}, total value: {}, buy: {}, hold: {}".format(
            e, EPISODES, episode_end_time - episode_start_time, agent.epsilon, env.iteration, env.total_reward, env.total_value, env.action_history[:].count(0), env.action_history[:].count(1)))
        done = False
        # if e % 100 == 0:
        #     agent.save("./save/dqn.h5")
              agent.model.ge
