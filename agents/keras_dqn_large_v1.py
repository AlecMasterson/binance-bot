import sys
from time import time
from os.path import dirname
sys.path.append(dirname(sys.path[0]))

import numpy as np

import GPyOpt

from trading_env.trading_env import TradingEnv
from trading_env.csvstream import CSVStreamer

from keras.models import Sequential, Model
from keras.layers import *
from keras.optimizers import Adam, RMSprop
from keras.utils import plot_model
from keras_diagram import ascii
from keras.utils import plot_model
from keras.utils.vis_utils import model_to_dot
from keras.callbacks import TensorBoard

from rl.agents.dqn import DQNAgent
from rl.agents.cem import CEMAgent
from rl.agents.sarsa import SARSAAgent
from rl.policy import BoltzmannQPolicy, MaxBoltzmannQPolicy
from rl.memory import SequentialMemory
from rl.processors import MultiInputProcessor

possible_actions = ['buy', 'sell', 'hold']
training_episodes = 2500
episode_length = int(10e10)        # all the data
trading_fee = .01
# time_fee = 0.0000
# history_length = 4
s_c1 = 1
s_c2 = 0

# Instantiating the environment
# generator = CSVStreamer('data_15_min/ADAETH.csv')
# env = TradingEnv(
#         data_generator=generator,
#         episode_length=episode_length,
#         trading_fee=trading_fee,
#         time_fee=time_fee,
#         history_length=history_length,
#         s_c1=s_c1,
#         s_c2=s_c2,
#         failed_trade_scalar=failed_trade_scalar,
#         buy_sell_scalar=buy_sell_scalar)
# state = env.reset()
# state_size = len(state)

# Instantiating the agent
memory_size = 100000
gamma = 0.96
epsilon_min = 0.01
batch_size = 16
action_size = len(possible_actions)
train_interval = 4
learning_rate = 1e-1


def build_brain(state_size, history_length, big_layers=0, small_layers=0):

    kernel_length = min(int(history_length / 32), 15)        # int(history_length*5)
    filter_length = max(int(history_length / 100), 16)        # int(max(history_length*0.1, 1))

    open_history_cnn_input = Input(shape=(1, history_length))
    open_history_cnn_out = Reshape((history_length, 1))(open_history_cnn_input)
    open_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 5, activation='relu')(open_history_cnn_out)
    open_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 3, activation='relu')(open_history_cnn_out)
    open_history_cnn_out = MaxPool1D(pool_size=int(filter_length / 3))(open_history_cnn_out)
    open_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 2, activation='relu')(open_history_cnn_out)
    open_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length, activation='relu')(open_history_cnn_out)
    open_history_cnn_out = MaxPool1D(pool_size=3)(open_history_cnn_out)
    open_history_cnn_out = Flatten()(open_history_cnn_out)
    open_history_cnn_out = Dense(max(int(history_length * 0.1), 10), activation='relu')(open_history_cnn_out)
    open_history_cnn_out = Dropout(0.1)(open_history_cnn_out)
    open_history_cnn_out = Dense(max(int(history_length * 0.08), 7), activation='relu')(open_history_cnn_out)
    open_model = Model(input=open_history_cnn_input, output=open_history_cnn_out)

    high_history_cnn_input = Input(shape=(1, history_length))
    high_history_cnn_out = Reshape((history_length, 1))(high_history_cnn_input)
    high_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 5, activation='relu')(high_history_cnn_out)
    high_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 3, activation='relu')(high_history_cnn_out)
    high_history_cnn_out = MaxPool1D(pool_size=int(filter_length / 3))(high_history_cnn_out)
    high_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 2, activation='relu')(high_history_cnn_out)
    high_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length, activation='relu')(high_history_cnn_out)
    high_history_cnn_out = MaxPool1D(pool_size=3)(high_history_cnn_out)
    high_history_cnn_out = Flatten()(high_history_cnn_out)
    high_history_cnn_out = Dense(max(int(history_length * 0.1), 10), activation='relu')(high_history_cnn_out)
    high_history_cnn_out = Dropout(0.1)(high_history_cnn_out)
    high_history_cnn_out = Dense(max(int(history_length * 0.08), 7), activation='relu')(high_history_cnn_out)
    high_model = Model(input=high_history_cnn_input, output=high_history_cnn_out)

    low_history_cnn_input = Input(shape=(1, history_length))
    low_history_cnn_out = Reshape((history_length, 1))(low_history_cnn_input)
    low_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 5, activation='relu')(low_history_cnn_out)
    low_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 3, activation='relu')(low_history_cnn_out)
    low_history_cnn_out = MaxPool1D(pool_size=int(filter_length / 3))(low_history_cnn_out)
    low_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 2, activation='relu')(low_history_cnn_out)
    low_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length, activation='relu')(low_history_cnn_out)
    low_history_cnn_out = MaxPool1D(pool_size=3)(low_history_cnn_out)
    low_history_cnn_out = Flatten()(low_history_cnn_out)
    low_history_cnn_out = Dense(max(int(history_length * 0.1), 10), activation='relu')(low_history_cnn_out)
    low_history_cnn_out = Dropout(0.1)(low_history_cnn_out)
    low_history_cnn_out = Dense(max(int(history_length * 0.08), 7), activation='relu')(low_history_cnn_out)
    low_model = Model(input=low_history_cnn_input, output=low_history_cnn_out)

    volume_history_cnn_input = Input(shape=(1, history_length))
    volume_history_cnn_out = Reshape((history_length, 1))(volume_history_cnn_input)
    volume_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 5, activation='relu')(volume_history_cnn_out)
    volume_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 3, activation='relu')(volume_history_cnn_out)
    volume_history_cnn_out = MaxPool1D(pool_size=int(filter_length / 3))(volume_history_cnn_out)
    volume_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length * 2, activation='relu')(volume_history_cnn_out)
    volume_history_cnn_out = Conv1D(filters=filter_length, kernel_size=kernel_length, activation='relu')(volume_history_cnn_out)
    volume_history_cnn_out = MaxPool1D(pool_size=3)(volume_history_cnn_out)
    volume_history_cnn_out = Flatten()(volume_history_cnn_out)
    volume_history_cnn_out = Dense(max(int(history_length * 0.1), 10), activation='relu')(volume_history_cnn_out)
    volume_history_cnn_out = Dropout(0.1)(volume_history_cnn_out)
    volume_history_cnn_out = Dense(max(int(history_length * 0.08), 7), activation='relu')(volume_history_cnn_out)
    volume_model = Model(input=volume_history_cnn_input, output=volume_history_cnn_out)

    extras_input = Input(shape=(1, 7))
    extras_output = Flatten()(extras_input)
    extras_output = Dense(20, activation='relu')(extras_output)
    extras_output = Dense(5, activation='relu')(extras_output)
    extras_model = Model(input=extras_input, output=extras_output)

    print('State_size:', state_size)
    brain_output = merge([open_model.output, high_model.output, low_model.output, volume_model.output, extras_model.output], mode='concat', concat_axis=-1)
    brain_output = Dense(int(history_length * 4), activation='relu')(brain_output)
    for _ in range(big_layers):
        brain_output = Dense(max(int(history_length * 2), 10), activation='relu')(brain_output)
        brain_output = Dropout(0.1)(brain_output)
    for _ in range(small_layers):
        brain_output = Dense(max(int(history_length * 1), 7), activation='relu')(brain_output)
        brain_output = Dropout(0.1)(brain_output)
    brain_output = Dense(max(int(history_length * 0.1), 5), activation='relu')(brain_output)
    brain_output = Dense(3, activation='relu')(brain_output)
    brain_model = Model(input=[open_model.input, high_model.input, low_model.input, volume_model.input, extras_model.input], output=brain_output)
    brain_model.compile(optimizer=Adam(lr=learning_rate), metrics=['mae', 'acc'], loss='mean_absolute_error')
    print(brain_model.summary())
    # print(ascii(brain_model))
    plot_model(brain_model, show_shapes=True, to_file='brain.png')
    # model_to_dot(brain_model).create(prog='dot', format='svg')
    return brain_model


def build_learner(brain):
    memory = SequentialMemory(limit=memory_size, window_length=1)
    policy = BoltzmannQPolicy()
    learner = DQNAgent(
        model=brain,
        nb_actions=action_size,
        memory=memory,
        nb_steps_warmup=300,
        target_model_update=learning_rate,
        policy=policy,
        processor=MultiInputProcessor(5),
        enable_double_dqn=True,
        enable_dueling_network=False,
        dueling_type='avg')
    learner.compile(optimizer=Adam(lr=learning_rate), metrics=['mae', 'acc'])
    return learner


def bot_learn(params):
    large, small, time_fee, history_length, failed_trade_scalar, buy_sell_scalar = int(params[0][0]), int(params[0][1]), float(params[0][2]), int(params[0][3]), float(params[0][4]), float(
        params[0][5])
    # history_length = int(params[0][0])
    # large, small, time_fee, failed_trade_scalar, buy_sell_scalar = 1, 2, 0.0, 1, 1
    generator = CSVStreamer('data_15_min/ADAETH.csv')
    env = TradingEnv(
        data_generator=generator,
        episode_length=generator.file_length + 1,
        trading_fee=trading_fee,
        time_fee=time_fee,
        history_length=history_length,
        s_c1=s_c1,
        s_c2=s_c2,
        failed_trade_scalar=failed_trade_scalar,
        buy_sell_scalar=buy_sell_scalar,
        logging_level='WARN')
    state = env.reset()
    state_size = len(state)
    brain = build_brain(state_size, history_length, large, small)
    learner = build_learner(brain)
    tbCallBack = TensorBoard(log_dir="tbgraph/{}".format(time()), histogram_freq=0, write_graph=True, write_images=True)
    print('large:', large, '| small:', small, '| time_fee:', time_fee, '| history_length:', history_length, '| failed_trade_scalar:', failed_trade_scalar, '| buy_sell_scalar:', buy_sell_scalar)
    learner.fit(env, nb_steps=200000, callbacks=[tbCallBack], visualize=False, verbose=1)
    env.reset()
    learner.test(env, nb_episodes=1, visualize=False)
    x = env.total_value
    print('Total_value:', x)
    return x


def optimize():
    bounds = [
        # {
        #     'name': 'large',
        #     'type': 'discrete',
        #     'domain': [0, 1, 3, 5],
        #     'dimensionality': 1
        # }, {
        #     'name': 'large',
        #     'type': 'discrete',
        #     'domain': [0, 1, 3, 5],
        #     'dimensionality': 1
        # }, {
        #     'name': 'time_fee',
        #     'type': 'continuous',
        #     'domain': (0, 10),
        #     'dimensionality': 1
        # },
        {
            'name': 'history_length',
            'type': 'discrete',
            'domain': range(1, 75, 5),
            'dimensionality': 1
        }
        # , {
        #     'name': 'failed_trade_scalar',
        #     'type': 'continuous',
        #     'domain': (0, 100),
        #     'dimensionality': 1
        # }, {
        #     'name': 'buy_sell_scalar',
        #     'type': 'continuous',
        #     'domain': (0, 100),
        #     'dimensionality': 1
        # }
    ]

    opt = GPyOpt.methods.BayesianOptimization(bot_learn, bounds, verbosity=True, Initial_design_numdata=2, Initial_design_type='latin', num_cores=4, maximize=True)

    # Run the optimization
    max_iter = 100        # evaluation budget
    max_time = 60 * 60 * 10        # time budget
    eps = 6        # Minimum allows distance between the las two observations

    opt.run_optimization(max_iter, max_time, eps)

    print(opt.x_opt)
    print(opt.Y_best)
    # opt.plot_convergence()
    print('done')


# print('Total reward:', env.total_reward, '| Total value:', env.total_value)
# learner.save_weights('agents/saves/learner_{}_{}_weights.h5f'.format('v1', str(x)), overwrite=True)

# optimize()

# large, small, time_fee, history_length, failed_trade_scalar, buy_sell_scalar
bot_learn([[3, 2, 0.001, 40, 1, 100]])
