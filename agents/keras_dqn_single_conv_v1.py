import sys
from time import time
from os.path import dirname
import shutil
# shutil.rmtree('./tbgraph')
try:
    shutil.rmtree('tbgraph')
except:
    pass
sys.path.append(dirname(sys.path[0]))

import numpy as np

import GPyOpt
from bayes_opt import BayesianOptimization

from trading_env.trading_env import TradingEnv
from trading_env.csvstream import CSVStreamer

from os import environ
# environ["CUDA_VISIBLE_DEVICES"] = "-1"
from keras.models import Sequential, Model
from keras.layers import Flatten, Dense, Conv1D, Input, Reshape, Dropout
from keras.optimizers import Adam, RMSprop, Nadam
from keras.utils import plot_model
from keras.utils.vis_utils import model_to_dot
from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.layers.merge import concatenate

from rl.agents.dqn import DQNAgent
from rl.agents.cem import CEMAgent
from rl.agents.sarsa import SARSAAgent
from rl.policy import BoltzmannQPolicy, MaxBoltzmannQPolicy
from rl.memory import SequentialMemory
from rl.processors import MultiInputProcessor, Processor

possible_actions = ['trade', 'hold']
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
training_episodes = 2500
episode_length = int(10e10)        # all the data
trading_fee = .000
# time_fee = 0.0000
# history_length = 4
s_c1 = 1
s_c2 = 0

memory_size = 1000000
gamma = 0.96
epsilon_min = 0.01
batch_size = 16
action_size = 2
train_interval = 4

# learning_rate = 1e-3


def build_brain(state_size, history_length, big_layers=0, small_layers=0):

    # int(history_length*5)
    # kernel_length = min(int(history_length / 32), 16)

    # history_cnn_input = Input(shape=(1, history_length, 5))
    # history_cnn_out = Reshape((history_length, 5))(history_cnn_input)
    # history_cnn_out = Conv1D(filters=60, kernel_size=kernel_length, activation='relu')(history_cnn_out)
    # history_cnn_out = Conv1D(filters=48, kernel_size=kernel_length, activation='relu')(history_cnn_out)
    # history_cnn_out = Conv1D(filters=24, kernel_size=kernel_length * 2, activation='relu')(history_cnn_out)
    # history_cnn_out = Conv1D(filters=6, kernel_size=kernel_length * 2, activation='relu')(history_cnn_out)
    # history_cnn_out = Conv1D(filters=2, kernel_size=kernel_length * 2, activation='relu')(history_cnn_out)
    # history_cnn_out = Flatten()(history_cnn_out)
    # # history_cnn_out = Dense(max(int(history_length * 0.5), 10), activation='relu')(history_cnn_out)
    # # history_cnn_out = Dropout(0.1)(history_cnn_out)
    # # history_cnn_out = Dense(max(int(history_length * 0.2), 7), activation='relu')(history_cnn_out)
    # history_cnn_out = Dense(10, activation='relu')(history_cnn_out)
    # history_cnn_out = Dense(3, activation='relu')(history_cnn_out)
    # cnn_model = Model(input=history_cnn_input, output=history_cnn_out)

    # extras_input = Input(shape=(1, 9))
    # extras_output = Flatten()(extras_input)
    # extras_output = Dense(20, activation='relu')(extras_output)
    # extras_output = Dense(20, activation='relu')(extras_output)
    # extras_output = Dense(20, activation='relu')(extras_output)
    # extras_output = Dense(20, activation='relu')(extras_output)
    # extras_model = Model(input=extras_input, output=extras_output)

    brain_input = Input(shape=(1, 9))
    # brain_output = concatenate([cnn_model.output, extras_model.output])
    # brain_output = Dense(int(history_length * 4), activation='relu')(brain_output)
    brain_output = Dense(20, activation='relu')(brain_input)
    brain_output = Dense(10, activation='relu')(brain_output)
    brain_output = Dense(10, activation='relu')(brain_output)
    brain_output = Dense(5, activation='relu')(brain_output)
    brain_output = Dense(2, activation='linear')(brain_output)
    brain_output = Flatten()(brain_output)
    # brain_model = Model(input=[cnn_model.input, extras_model.input], output=brain_output)
    brain_model = Model(input=brain_input, output=brain_output)
    # brain_model.compile(optimizer=Nadam(lr=learning_rate), metrics=['mae', 'mse'], loss='mean_absolute_error')
    plot_model(brain_model, show_shapes=True, to_file='brain.png')
    return brain_model


def build_learner(brain, learning_rate):
    memory = SequentialMemory(limit=memory_size, window_length=1)
    policy = BoltzmannQPolicy()
    learner = DQNAgent(
        model=brain,
        nb_actions=action_size,
        memory=memory,
        nb_steps_warmup=5000,
        target_model_update=learning_rate,
        policy=policy,
        processor=Processor(),
        enable_double_dqn=True,
        enable_dueling_network=False,
        dueling_type='avg')
    learner.compile(optimizer=Nadam(lr=learning_rate), metrics=['mae', 'mse'])
    return learner


def bot_learn(time_fee, history_length, buy_sell_scalar, hold_scalar, timeout_scalar, learning_rate):
    generator = CSVStreamer(data_csvs)
    env = TradingEnv(
        data_generator=generator,
        episode_length=10e10,
        trading_fee=trading_fee,
        time_fee=time_fee,
        history_length=history_length,
        s_c1=s_c1,
        s_c2=s_c2,
        buy_sell_scalar=buy_sell_scalar,
        hold_scalar=hold_scalar,
        timeout_scalar=timeout_scalar)
    state = env.reset()
    state_size = len(state)
    brain = build_brain(state_size, history_length, 0, 0)
    learner = build_learner(brain, learning_rate)
    for i in range(100):
        tbCallBack = TensorBoard(log_dir="tbgraph/{}".format(time()), write_graph=True, write_images=True)
        learner.fit(env, nb_steps=100000, visualize=False, verbose=1, callbacks=[tbCallBack])
        env.final_render(savefig=True, filename='training_' + str(i), plot_reward=False, plot_total_reward=True, plot_total_value=True)
    # l_it = env.iteration
    # scores = []
    # for _ in range(3):
    #     env.reset()
    #     learner.test(env, nb_episodes=1, visualize=False, verbose=0)
    #     if env.total_value == s_c1 and env.action_history[:].count(0) < 5:
    #         scores.append(l_it / 10000000)
    #     else:
    #         scores.append(env.total_value)

    # env.final_render(plot_reward=True, plot_total_reward=True, plot_total_value=False)
    # return np.mean(scores)


def optimize():
    bop = BayesianOptimization(
        lambda buy_sell_scalar, hold_scalar, timeout_scalar: bot_learn(0.001, 200, buy_sell_scalar, hold_scalar, timeout_scalar, 0.1),
        {
        # 'time_fee': (0, 100),
            'buy_sell_scalar': (0, 0.01),
            'hold_scalar': (0, 0.01),
            'timeout_scalar': (0, 0.01),
        # 'learning_rate': (0.00001, 1),
        })
    bop.maximize(init_points=3, n_iter=5000, acq="poi", xi=0.001)
    return bop


# learner.save_weights('agents/saves/learner_{}_{}_weights.h5f'.format('v1', str(x)), overwrite=True)

# bop = optimize()
# print(bop)

print(bot_learn(time_fee=0.0001, history_length=1, buy_sell_scalar=0.1, hold_scalar=0.0001, timeout_scalar=10, learning_rate=0.1))
