import logging, ta, pandas, os, traceback


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
        return None


def to_file(data, file, logger):
    try:
        logger.info('Writing Data to File...')
        data.to_csv(os.path.dirname(__file__) + '/../' + file, index=False)
        return True
    except:
        logger.error('Failed to Write Data to File')
        logger.error('\n' + traceback.print_exc())
        return None


def calculate_overhead(data, coinpair, logger):
    try:
        logger.info('Calculating \'' + coinpair + '\' Overhead Information...')
        close_data = pandas.Series([row['CLOSE'] for index, row in data.iterrows()])

        macd = ta.trend.macd(close_data, n_fast=12, n_slow=26, fillna=True)
        macd_signal = ta.trend.macd_signal(close_data, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        macd_diff = ta.trend.macd_diff(close_data, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        upperband = ta.volatility.bollinger_hband(close_data, n=14, ndev=2, fillna=True)
        lowerband = ta.volatility.bollinger_lband(close_data, n=14, ndev=2, fillna=True)

        length = len(data.index)
        if length != len(macd) or length != len(macd_signal) or length != len(macd_diff) or length != len(upperband) or length != len(lowerband): raise Exception

        for index in data.index:
            data.at[index, 'MACD'] = macd[index]
            data.at[index, 'MACD_SIGNAL'] = macd_signal[index]
            data.at[index, 'MACD_DIFF'] = macd_diff[index]
            data.at[index, 'UPPERBAND'] = upperband[index]
            data.at[index, 'LOWERBAND'] = lowerband[index]
        return data
    except:
        logger.error('Failed to Calculate \'' + coinpair + '\' Overhead Information')
        logger.error('\n' + traceback.print_exc())
        return None


def buy(client, coinpair, price, logger):
    logger.info('BUYING ' + coinpair + ' at Price ' + str(price) + '...')


def sell(client, coinpair, price, logger):
    logger.info('SELLING ' + coinpair + ' at Price ' + str(price) + '...')
