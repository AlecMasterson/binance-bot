import sys
from os.path import dirname
sys.path.append(dirname(sys.path[0]))

import numpy as np
import gym

from trading_env.tenv.envs.trading_env import TradingEnv
from trading_env.tenv.envs.gens.csvstream import CSVStreamer

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from keras.utils import plot_model

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

episode_length = 10e100
trading_fee = 0.001
time_fee = 0
renderwindr = 20
actions = ['buy', 'sell', 'hold']
hist_n = 100

generator = CSVStreamer('data_15_min/ADAETH.csv')

env = TradingEnv(data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=hist_n)

# Next, we build a very simple model.
model = Sequential()
model.add(Flatten(input_shape=(1,) + (hist_n+5,)))
model.add(Dense(5, activation='relu'))
model.add(Dense(len(actions), activation='linear'))
print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model, nb_actions=len(actions), memory=memory, nb_steps_warmup=100, target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-2), metrics=['mae'])

for x in range(1, 101):
    env = TradingEnv(data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=hist_n)
    dqn.fit(env, nb_steps=10e4, visualize=False, verbose=1)
    dqn.save_weights('dqn_{}_{}_weights.h5f'.format('v1', str(x)), overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=5, visualize=True)
