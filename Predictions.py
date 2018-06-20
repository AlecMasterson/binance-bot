# coding: utf-8

# In[1]:

import pandas as pd
from time import time
from datetime import datetime
import numpy as np
from sklearn.preprocessing import minmax_scale, MinMaxScaler
from scipy.stats import linregress
from matplotlib import pyplot
import seaborn as sns
sns.set_style('ticks')

from keras.models import Sequential, Model
from keras.layers import Flatten, Dense, Conv1D, Input, Reshape, Dropout, LeakyReLU, MaxPooling1D
from keras.optimizers import Adam, RMSprop, Nadam, SGD, Adagrad
from keras.utils import plot_model
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau
from keras.layers.merge import concatenate

# In[2]:


def data():
    """
    Data providing function:

    This function is separated from create_model() so that hyperopt
    won't reload data for each evaluation run.
    """

    def frame_to_features(df, time_in, time_out):
        f = []
        n_features = len(df.columns)
        for i in range(time_in + 1, len(andf) - time_out):
            # reshape input to be 3D [samples, timesteps, features]
            f.append([
                df.iloc[i - time_in:i].values,
            #             df['Open'].iloc[i - time_out + 2:i + 2].values
                (df['Open'].iloc[i + time_out - 1] > df['Open'].iloc[i + time_out])
            ])
        return f

    raw_df = pd.read_csv('data/history/ADABTC.csv')
    ndf = raw_df.filter(items=['Open', 'High', 'Low', 'Close', 'Volume', 'Number Trades', 'Quote Asset Volume', 'Taker Base Asset Volume', 'Taker Quote Asset Volume'])
    ndf = ndf.set_index(pd.to_datetime(raw_df['Open Time'], unit='ms'))
    ndf.dropna(inplace=True)
    andf = ndf.apply(lambda c: minmax_scale(X=c, feature_range=(0, 1)))

    history_length = 50
    prediction_length = 1
    fs = frame_to_features(andf, history_length, prediction_length)

    # split into train and test sets
    train = [x[0] for x in fs]
    test = [x[1] for x in fs]
    # split into input and outputs
    train_X, test_X = np.array(train[:int(len(train) * 0.7)]), np.array(train[int(len(train) * 0.7):])
    train_y = np.array(test[:int(len(test) * 0.7)])
    test_y = np.array(test[int(len(test) * 0.7):])
    return train_X, train_y, test_X, test_y


# In[3]:

from hyperas import optim
from hyperas.distributions import choice, uniform, randint

from hyperopt import Trials, STATUS_OK, tpe


def make_model():

    optimizer = {{choice(['rmsprop', 'adam', 'sgd'])}}

    def get_lr_metric(optimizer):

        def lr(y_true, y_pred):
            return optimizer.lr

        return lr

    lr_metric = get_lr_metric(optimizer)

    activation = {{choice(['linear', 'tanh', 'relu'])}}
    conv_pooling = {{randint(1, 10)}}
    conv_pooling_kernel_length = {{randint(1, 1000)}}
    conv_pool_size = {{randint(1, 10)}}
    conv_end = {{randint(0, 10)}}
    conv_end_kernel_length = {{randint(1, 1000)}}
    dense_end = {{randint(1, 10)}}

    history_cnn_input = Input(shape=(train_X.shape[1], train_X.shape[2]))
    for x in reversed(range(conv_pooling)):
        if x == conv_pooling:
            history_cnn_out = Conv1D(filters=2 ^ x, kernel_size=conv_pooling_kernel_length, padding='same', activation=activation)(history_cnn_input)
            history_cnn_out = MaxPooling1D(pool_size=conv_pool_size)(history_cnn_out)
        else:
            history_cnn_out = Conv1D(filters=2 ^ x, kernel_size=conv_pooling_kernel_length, padding='same', activation=activation)(history_cnn_out)
            history_cnn_out = MaxPooling1D(pool_size=conv_pool_size)(history_cnn_out)

    for x in reversed(range(conv_end)):
        history_cnn_out = Conv1D(filters=16, kernel_size=conv_end_kernel_length, padding='same', activation=activation)(history_cnn_out)

    history_cnn_out = Flatten()(history_cnn_out)
    for x in reversed(range(dense)):
        history_cnn_out = Dense(int(10 * x), activation=activation)(history_cnn_out)

    history_cnn_out = Dense(prediction_length, activation='linear')(history_cnn_out)
    brain = Model(input=history_cnn_input, output=history_cnn_out)

    brain.compile(optimizer=optimizer, loss='mse', metrics=['mse', lr_metric])
    #     print(brain.summary())

    # fit network
    TB = TensorBoard(log_dir='./TBlogs/' + datetime.now().strftime("%Y%m%d-%H%M%S"), histogram_freq=5, batch_size=64, write_graph=False, write_grads=True, write_images=True)

    # reduceLR = ReduceLROnPlateau(monitor='loss', patience=1, verbose=1, factor=0.1, min_lr=0.0001)
    brain.fit(train_X, train_y, epochs=10, batch_size={{choice([16, 64, 256])}}, validation_data=(test_X, test_y), verbose=1, shuffle=True, callbacks=[TB])

    score, lr = model.evaluate(x_test, y_test, verbose=0)
    print('Test loss:', score)
    return {'loss': -score, 'status': STATUS_OK, 'model': brain}


# In[4]:

best_run, best_model = optim.minimize(model=make_model, data=data, algo=tpe.suggest, max_evals=5, trials=Trials())
X_train, Y_train, X_test, Y_test = data()
print("Evalutation of best performing model:")
print(best_model.evaluate(X_test, Y_test))
print("Best performing model chosen hyper-parameters:")
print(best_run)
