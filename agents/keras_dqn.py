import sys
from os.path import dirname
sys.path.append(dirname(sys.path[0]))

import numpy as np
import gym

from trading_env.trading_env import TradingEnv
from trading_env.csvstream import CSVStreamer

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from keras.utils import plot_model

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory


possible_actions = ['buy', 'sell', 'hold']
training_episodes = 10000
episode_length = int(10e10)        # all the data
trading_fee = .01
time_fee = 0.01
history_length = 16
s_c1 = 1
s_c2 = 0

# Instantiating the environment
generator = CSVStreamer('data_15_min/ADAETH.csv')
env = TradingEnv(data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=history_length, s_c1=s_c1, s_c2=s_c2)
state = env.reset()
state_size = len(state)

# Instantiating the agent
memory_size = 1000
training_episodes = 10000
episode_length = int(10e10)        # all the data
gamma = 0.96
epsilon_min = 0.01
batch_size = 64
action_size = len(possible_actions)
train_interval = 10
learning_rate = 1e-3

brain = Sequential()
brain.add(Flatten(input_shape=(1, state_size)))
brain.add(Dense(int(state_size), activation='relu'))
brain.add(Dense(max(int(state_size * 0.2), 10), activation='relu'))
brain.add(Dense(max(int(state_size * 0.3), 7), activation='relu'))
brain.add(Dense(max(int(state_size * 0.2), 5), activation='relu'))
brain.add(Dense(action_size, activation='linear'))
brain.compile(loss='mse', optimizer=Adam(lr=learning_rate))
print(brain.summary())

memory = SequentialMemory(limit=memory_size, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=brain, nb_actions=action_size, memory=memory, nb_steps_warmup=100, target_model_update=learning_rate, policy=policy)
dqn.compile(Adam(lr=1e-2), metrics=['mae'])

for x in range(1, 501):
    env = TradingEnv(data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=history_length, s_c1=s_c1, s_c2=s_c2)
    dqn.fit(env, nb_steps=10e4, visualize=False, verbose=1)
    print('Total reward:', env.total_reward, '| Total value:', env.total_value)
    if x % 10 == 0:
        dqn.save_weights('dqn_{}_{}_weights.h5f'.format('v1', str(x)), overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=5, visualize=True)
