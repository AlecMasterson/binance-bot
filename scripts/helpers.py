import sys, os, logging, ta, pandas, traceback


def bullet_proof(logger, message, f):
    try:
        logger.info(message)
        return f()
    except:
        logger.error(message + '\nTraceback Output:\n' + str(traceback.print_exc()))
        return None


def create_logger(name):
    try:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)

        fh = logging.FileHandler(os.path.dirname(__file__) + '/../logs/' + name + '.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)

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


def round_down_nearest_n(x, n):
    return round(x - (x % pow(10, -1 * n)), n)


def validate_order(policies, type, balance, price):

    # Convert the price we want to order at to the correct format for this coinpair.
    formatPrice = round_down_nearest_n(price, len(str(float(policies['filters'][0]['minPrice'])).split('.')[1]))

    # Convert the quantity of our desired asset to the correct format for this coinpair.
    # NOTE: Using all available BTC for BUY.
    quantity = round_down_nearest_n(balance / formatPrice if type == 'BUY' else balance, len(str(float(policies['filters'][1]['minQty'])).split('.')[1]))

    # Test the trading policy filters provided by the symbols dictionary.
    valid = True

    if formatPrice < float(policies['filters'][0]['minPrice']): valid = False
    elif formatPrice > float(policies['filters'][0]['maxPrice']): valid = False
    elif int((formatPrice - float(policies['filters'][0]['minPrice'])) % float(policies['filters'][0]['tickSize'])) != 0: valid = False

    if quantity < float(policies['filters'][1]['minQty']): valid = False
    elif quantity > float(policies['filters'][1]['maxQty']): valid = False
    elif int((quantity - float(policies['filters'][1]['minQty'])) % float(policies['filters'][1]['stepSize'])) != 0: valid = False

    if quantity * formatPrice < float(policies['filters'][2]['minNotional']): valid = False

    # Return the desired trade quantity and price if all is valid.
    if valid: return quantity, formatPrice
    else: return -1, -1


def safe_calculate_overhead(logger, coinpair, data):
    return bullet_proof(logger, 'Calculating \'' + coinpair + '\' Overhead Information', lambda: calculate_overhead(data))
