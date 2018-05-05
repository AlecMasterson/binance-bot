import sys
from os.path import dirname
sys.path.append(dirname(sys.path[0]))

import random
from itertools import compress
import numpy as np
import time

from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import Adam

import helpers

from trading_env.trading_env import TradingEnv
from trading_env.csvstream import CSVStreamer

# episode_length = 100000
# trading_fee = 0.001
# time_fee = 0
# renderwindr = 20
# actions = ['buy', 'sell', 'hold']


class DQNAgent:

    def __init__(self, state_size, action_size, episodes, episode_length, memory_size=2000, train_interval=100, gamma=0.95, learning_rate=0.001, batch_size=64, epsilon_min=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.memory_size = memory_size
        self.memory = [None] * memory_size
        self.gamma = gamma
        self.epsilon = 1.0
        self.epsilon_min = epsilon_min
        self.epsilon_decrement = (self.epsilon - epsilon_min)\
            * train_interval / (episodes * episode_length)  # linear decrease rate
        self.learning_rate = learning_rate
        self.train_interval = train_interval
        self.batch_size = batch_size
        self.brain = self._build_brain()
        self.i = 0

    def _build_brain(self):
        """Build the agent's brain
        """
        brain = Sequential()
        brain.add(Dense(int(self.state_size), input_dim=self.state_size, activation='relu'))
        brain.add(Dense(max(int(self.state_size * 0.2), 10), activation='relu'))
        brain.add(Dense(max(int(self.state_size * 0.3), 7), activation='relu'))
        brain.add(Dense(max(int(self.state_size * 0.2), 5), activation='relu'))
        brain.add(Dense(self.action_size, activation='linear'))
        brain.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return brain

    def act(self, state):
        """Acting Policy of the DQNAgent
        """
        action = np.zeros(self.action_size)
        if np.random.rand() <= self.epsilon:
            action[random.randrange(self.action_size)] = 1
        else:
            state = state.reshape(1, self.state_size)
            act_values = self.brain.predict(state)
            action[np.argmax(act_values[0])] = 1
        return action

    def observe(self, state, action, reward, next_state, done, warming_up=False):
        """Memory Management and training of the agent
        """
        self.i = (self.i + 1) % self.memory_size
        self.memory[self.i] = (state, action, reward, next_state, done)
        if (not warming_up) and (self.i % self.train_interval) == 0:
            if self.epsilon > self.epsilon_min:
                self.epsilon -= self.epsilon_decrement
            state, action, reward, next_state, done = self._get_batches()
            reward += (self.gamma * np.logical_not(done) * np.amax(self.brain.predict(next_state), axis=1))
            q_target = self.brain.predict(state)
            q_target[action[0], action[1]] = reward
            return self.brain.fit(state, q_target, batch_size=self.batch_size, epochs=1, verbose=False)

    def _get_batches(self):
        """Selecting a batch of memory
           Split it into categorical subbatches
           Process action_batch into a position vector
        """
        batch = np.array(random.sample(self.memory, self.batch_size))
        state_batch = np.concatenate(batch[:, 0])\
            .reshape(self.batch_size, self.state_size)
        action_batch = np.concatenate(batch[:, 1])\
            .reshape(self.batch_size, self.action_size)
        reward_batch = batch[:, 2]
        next_state_batch = np.concatenate(batch[:, 3])\
            .reshape(self.batch_size, self.state_size)
        done_batch = batch[:, 4]
        # action processing
        action_batch = np.where(action_batch == 1)
        return state_batch, action_batch, reward_batch, next_state_batch, done_batch


if __name__ == "__main__":
    # Instantiating the environmnent
    generator = CSVStreamer('data_15_min/ADAETH.csv')
    possible_actions = ['buy', 'sell', 'hold']
    training_episodes = 10000
    episode_length = int(10e10)        # all the data
    trading_fee = .01
    time_fee = 0.01
    history_length = 16
    s_c1 = 1
    s_c2 = 0
    environment = TradingEnv(data_generator=generator, episode_length=episode_length, trading_fee=trading_fee, time_fee=time_fee, history_length=history_length, s_c1=s_c1, s_c2=s_c2)
    state = environment.reset()

    # Instantiating the agent
    memory_size = 1000
    state_size = len(state)
    gamma = 0.96
    epsilon_min = 0.01
    batch_size = 64
    action_size = 3
    train_interval = 10
    learning_rate = 1e-3
    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        memory_size=memory_size,
        episodes=training_episodes,
        episode_length=episode_length,
        train_interval=train_interval,
        gamma=gamma,
        learning_rate=learning_rate,
        batch_size=batch_size,
        epsilon_min=epsilon_min)
    # Warming up the agent
    print('Warming up')
    for _ in range(memory_size):
        action = agent.act(state)
        next_state, reward, done, _ = environment.step(list(compress(possible_actions, action))[0])
        agent.observe(state, action, reward, next_state, done, warming_up=True)
    # Training the agent
    print('Training')
    for ep in range(training_episodes):
        print("Ep:" + str(ep))
        state = environment.reset()
        rew = 0
        loss = 0
        for _ in range(episode_length):
            action = agent.act(state)
            next_state, reward, done, _ = environment.step(list(compress(possible_actions, action))[0])
            l = agent.observe(state, action, reward, next_state, done)
            loss = l if l is not None else loss
            state = next_state
            rew += reward
            if done:
                break

        print("rew:" + str(round(rew, 3)) + "| eps:" + str(round(agent.epsilon, 3)) + "| loss:" + str(round(loss.history["loss"][0], 4)) + "| wallet:" + str(environment.total_value))
    # Running the agent
    done = False
    state = environment.reset()
    while not done:
        action = agent.act(state)
        state, _, done, info = environment.step(list(compress(possible_actions, action))[0])
        if 'status' in info and info['status'] == 'Closed plot':
            done = True
        else:
            environment.render()

    print(environment.total_reward, environment.total_value)
    environment.final_render(plot_reward=False, plot_total_reward=False, plot_total_value=True)
