import argparse
import pandas
import numpy
import math
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import LSTM
from keras.layers import RepeatVector
from keras.layers import TimeDistributed


global TEST_SIZE
TEST_SIZE = 0.25

global FORECAST_LENGTH
FORECAST_LENGTH = 6

global INPUT_LENGTH
INPUT_LENGTH = 10

global EPOCHS
EPOCHS = 10000

global BATCH_SIZE
BATCH_SIZE = 100

global VERBOSE
VERBOSE = 0


'''
Create a training and testing dataset given the DataFrame.values.
Both the training and testing datasets follow the "Output Shape" given below.
The testing dataset will be TEST_SIZE% of the original data values.
The "train_x" and "train_y" datasets will specifically be used for training the model.

Input Shape: [X, Y]
    X - Number of Candles
    Y - Number of Features
Output Shape: [I, J, K]
    I - floor(X / FORECAST_LENGTH)
    J - FORECAST_LENGTH
    K - Number of Features
'''


def split_dataset(data):
    remainder = (len(data) % FORECAST_LENGTH)
    if remainder != 0:
        data = data[:-remainder]
    splitIndex = int(numpy.floor((len(data) / FORECAST_LENGTH) * TEST_SIZE) * FORECAST_LENGTH)

    train, test = data[:-splitIndex], data[-splitIndex:]

    train_x, train_y = [], []
    for i in range(len(train)):
        if (i + INPUT_LENGTH + FORECAST_LENGTH) <= len(train):
            train_x.append(data[i: (i + INPUT_LENGTH), :])
            train_y.append(data[(i + INPUT_LENGTH): (i + INPUT_LENGTH + FORECAST_LENGTH), 0])

    train = numpy.array(numpy.split(train, len(train) / FORECAST_LENGTH))
    test = numpy.array(numpy.split(test, len(test) / FORECAST_LENGTH))

    print(
        'Number of Features = {}\nForecast Length = {}\nTraining Shape = {}\nTesting Shape = {}'.format(
            data.shape[1], FORECAST_LENGTH, train.shape, test.shape
        )
    )
    return train, test, numpy.array(train_x), numpy.array(train_y)


def build_model(train_x, train_y):
    # define parameters
    n_timesteps, n_features, n_outputs = train_x.shape[1], train_x.shape[2], train_y.shape[1]
    # reshape output into [samples, timesteps, features]
    train_y = train_y.reshape((train_y.shape[0], train_y.shape[1], 1))

    # Define the model.
    model = Sequential()
    model.add(LSTM(200, activation='relu', input_shape=(n_timesteps, n_features)))
    model.add(RepeatVector(n_outputs))
    model.add(LSTM(200, activation='relu', return_sequences=True))
    model.add(TimeDistributed(Dense(100, activation='relu')))
    model.add(TimeDistributed(Dense(1)))
    model.compile(loss='mse', optimizer='adam')

    # Fit the model.
    model.fit(train_x, train_y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=VERBOSE)
    return model


def evaluate_forecasts(actual, predicted):
    # Get the RMSE for 1, 2, 3... candles into the future.
    scores = [math.sqrt(mean_squared_error(actual[:, i], predicted[:, i])) for i in range(actual.shape[1])]

    # Get the overall RMSE across all (actual.shape[1]) candles into the future.
    score = 0
    for row in range(actual.shape[0]):
        for col in range(actual.shape[1]):
            score += ((actual[row, col] - predicted[row, col]) ** 2)
    score = math.sqrt(score / (actual.shape[0] * actual.shape[1]))

    return score, scores


def evaluate_model(train, test, train_x, train_y):
    model = build_model(train_x, train_y)

    # Create a deep-copy list of the history to be used in forecasting.
    history = [x for x in train]

    # For each entry in "test", make a prediction.
    # Then add the true value to the "history" for the next forecasting.
    predictions = []
    for i in range(len(test)):
        predictions.append(forecast(model, history, INPUT_LENGTH))
        history.append(test[i, :])

    # Evalulate the predictions using the actual values from "test".
    # The first feature should be the "CLOSE" price being predicted.
    return evaluate_forecasts(test[:, :, 0], numpy.array(predictions))


# make a forecast
def forecast(model, history, INPUT_LENGTH):
    # flatten data
    data = numpy.array(history)
    data = data.reshape((data.shape[0]*data.shape[1], data.shape[2]))
    # retrieve last observations for input data
    input_x = data[-INPUT_LENGTH:, :]
    # reshape into [1, INPUT_LENGTH, n]
    input_x = input_x.reshape((1, input_x.shape[0], input_x.shape[1]))
    # forecast the next week
    yhat = model.predict(input_x, verbose=0)
    # we only want the vector forecast
    yhat = yhat[0]
    return yhat


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used to Train an LTSM Network using Binance Symbol Data')

    parser.add_argument(
        '-i', '--interval', help='the time interval to train on',
        choices=['1h', '2h', '4h', '12h', '1d'], dest='INTERVAL', required=True
    )
    args = parser.parse_args()

    data = pandas.read_csv('./data/history/BNBBTC.csv')

    # Filter the data and rearrange everything to meet the needs of this system.
    data = data[data['INTERVAL'] == args.INTERVAL].sort_values(
        by=['OPEN_TIME']
    ).drop(
        columns=['SYMBOL', 'INTERVAL', 'OPEN_TIME', 'CLOSE_TIME']
    ).reset_index(
        drop=True
    ).astype('float32')

    # Move the "CLOSE" price feature to the front of the DataFrame.
    columns = data.columns.tolist()
    columns.insert(0, columns.pop(columns.index('CLOSE')))
    data = data.reindex(columns=columns)

    #data.head(16).to_csv('./test.csv', index=False)

    # Split the data into the training and testing datasets.
    train, test, train_x, train_y = split_dataset(data.values)

    score, scores = evaluate_model(train, test, train_x, train_y)
    print('Result: {} {}'.format(score, scores))
    print('Percent Error from Last Candle: {}%'.format(round(score / data['CLOSE'][len(data)-1] * 100, 2)))
