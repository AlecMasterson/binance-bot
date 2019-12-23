import sys, os, pandas, numpy, collections, datetime
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import utilities, helpers, BacktestSimple


def format_data(data, start_date, end_date, candle_minutes, future_window_size):
    interval_string = '{}h'.format(candle_minutes / 60) if candle_minutes > 30 else '{}m'.format(candle_minutes)
    data = data[(data['INTERVAL'] == interval_string) & (data['OPEN_TIME'] >= start_date.timestamp() * 1000.0)].sort_values(by=['OPEN_TIME']).reset_index(drop=True)

    window = collections.deque(maxlen=future_window_size)
    for index, row in data.iterrows():
        window.append(row['OPEN'])
        if index >= future_window_size: data.at[index - future_window_size, 'FUTURE_POTENTIAL'] = ((max(window) / data.at[index - future_window_size, 'OPEN']) - 1.0) * 100.0

    data = data[data['OPEN_TIME'] <= end_date.timestamp() * 1000.0].drop(columns=['INTERVAL', 'CLOSE', 'CLOSE_TIME', 'QUOTE_ASSET_VOLUME', 'NUMBER_TRADES', 'TAKER_BASE_ASSET_VOLUME', 'TAKER_QUOTE_ASSET_VOLUME', 'IGNORE']).sort_values(by=['OPEN_TIME']).reset_index(drop=True)
    data - data.drop(columns=['OPEN_TIME'])

    if len(data) != ((end_date - start_date).days * 24 * 60 / candle_minutes + 1): return None
    return data


if __name__ == '__main__':
    coinpair = 'BNBBTC'

    print('Loading/Formatting Data...')

    data = format_data(helpers.read_file('data/history/' + coinpair + '.csv'), utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.BACKTEST_CANDLE_INTERVAL, utilities.FUTURE_WINDOW_SIZE)
    environment = BacktestSimple.BacktestSimple(data, utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, datetime.timedelta(minutes=utilities.BACKTEST_CANDLE_INTERVAL))

    print('Creating Dataset...')

    X = []
    window = collections.deque(maxlen=utilities.WINDOW_SIZE)

    state, reward, done, info = environment.reset()
    while not done:
        state, reward, done, info = environment.step(False)
        window.append(state)
        if len(window) == utilities.WINDOW_SIZE: X.append([reward] + [candle[key] for candle in window for key in candle])

    df = pandas.DataFrame(X)
    X = df.values[:, 1:]
    Y = df.values[:, :1]

    print('Building Network...')
