import sys, os, logging, ta, pandas, traceback


def bullet_proof(logger, message, f):
    try:
        logger.info(message)
        return f()
    except:
        logger.error(message + str(traceback.print_exc()))
        return None


def create_logger(name):
    try:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        fh = logging.FileHandler(os.path.dirname(__file__) + '/../logs/' + name + '.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger
    except:
        print('Failed to Create Logger')
        sys.exit(1)


def to_file(file, data):
    data.to_csv(os.path.dirname(__file__) + '/../' + file, index=False)
    return True


def read_file(file):
    return pandas.read_csv(os.path.dirname(__file__) + '/../' + file)


def safe_to_file(logger, file, data):
    return bullet_proof(logger, 'Writing Data to File', lambda: to_file(file, data))


def safe_read_file(logger, file):
    return bullet_proof(logger, 'Reading Data from File', lambda: read_file(file))


def calculate_overhead(data):
    close_data = pandas.Series([row['CLOSE'] for index, row in data.iterrows()])

    macd = ta.trend.macd(close_data, n_fast=12, n_slow=26, fillna=True)
    macd_signal = ta.trend.macd_signal(close_data, n_fast=12, n_slow=26, n_sign=9, fillna=True)
    macd_diff = ta.trend.macd_diff(close_data, n_fast=12, n_slow=26, n_sign=9, fillna=True)
    upperband = ta.volatility.bollinger_hband(close_data, n=14, ndev=2, fillna=True)
    lowerband = ta.volatility.bollinger_lband(close_data, n=14, ndev=2, fillna=True)

    length = len(data.index)
    if length != len(macd) or length != len(macd_signal) or length != len(macd_diff) or length != len(upperband) or length != len(lowerband): return None

    for index in data.index:
        data.at[index, 'MACD'] = macd[index]
        data.at[index, 'MACD_SIGNAL'] = macd_signal[index]
        data.at[index, 'MACD_DIFF'] = macd_diff[index]
        data.at[index, 'UPPERBAND'] = upperband[index]
        data.at[index, 'LOWERBAND'] = lowerband[index]
    return data


def safe_calculate_overhead(logger, coinpair, data):
    return bullet_proof(logger, 'Calculating \'' + coinpair + '\' Overhead Information', lambda: calculate_overhead(data))


def buy(client, coinpair, price):
    return True


def safe_buy(logger, client, coinpair, price):
    message = 'BUYING ' + coinpair + ' at Price ' + str(price)
    return bullet_proof(logger, message, lambda: buy(client, coinpair, price))


def sell(client, coinpair, price):
    return True


def safe_sell(logger, client, coinpair, price):
    message = 'SELLING ' + coinpair + ' at Price ' + str(price)
    return bullet_proof(logger, message, lambda: sell(client, coinpair, price))
