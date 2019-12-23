import sys, os, logging, ta, pandas, time
import helpers_binance, helpers_db


def bullet_proof(logger, message, f):
    try:
        logger.info(message)
        return f()
    except Exception as e:
        logger.error(e)
        return None


def main_function(logger, message, fun, client=False, db=False, extra=None):
    if client:
        client_object = helpers_binance.safe_connect(logger)
        if client_object is None: sys.exit(1)
    else: client_object = None
    if db:
        db_object = helpers_db.safe_connect(logger)
        if db_object is None: sys.exit(1)
    else: db_object = None

    f = lambda: fun(client=client_object, db=db_object, extra=extra)
    exit_status = bullet_proof(logger, message, f)

    if exit_status is None or exit_status != 0: logger.error('Closing Script with Exit Status ' + str(exit_status if not exit_status is None else 1))
    else: logger.info('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)


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


def current_time():
    return int(round(time.time() * 1000))


def to_file(file, data):
    data.to_csv(os.path.dirname(__file__) + '/../' + file, index=False)
    return True


def read_file(file):
    return pandas.read_csv(os.path.join(os.path.dirname(__file__), '..', file))


def safe_to_file(logger, file, data):
    return bullet_proof(logger, 'Writing Data to File \'' + str(file) + '\'', lambda: to_file(file, data))


def safe_read_file(logger, file):
    return bullet_proof(logger, 'Reading Data from File \'' + str(file) + '\'', lambda: read_file(file))


def calculate_overhead(data):
    return ta.wrapper.add_all_ta_features(data, 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', fillna=False)


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
