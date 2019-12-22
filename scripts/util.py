import json
import logging
import datetime
import binance.client
import pandas
import numpy
import os
import ta
import tqdm


def main(name):
    """
    A decoration for setting up a script with proper logging, config usage, and error handling.
    The function must take 2 keyword arguments: 'logger' of type 'logging.Logger' and 'config' of type 'dict'.
    The decoration annotation must include the keyword argument 'name' of type 'str'.
    The 'name' will be the name of the log file.
    """

    def main_function(f):
        def wrapper(*args, **kwargs):
            try:
                logger = None
                config = json.load(open('scripts/config.json'))

                logger = logging.getLogger(name)
                logger.setLevel(logging.DEBUG)

                fileHandler = logging.FileHandler(get_file_path(
                    create=True,
                    directoryTree=(config['export_directories']['logs'], datetime.datetime.today().strftime('%Y-%m-%d')),
                    fileName='{}.log'.format(name)
                ))
                consoleHandler = logging.StreamHandler()

                formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
                fileHandler.setFormatter(formatter)
                consoleHandler.setFormatter(formatter)

                logger.addHandler(fileHandler)
                logger.addHandler(consoleHandler)

                kwargs['logger'] = logger
                kwargs['config'] = config

                logger.info('Starting Script...')
                f(*args, **kwargs)
                logger.info('Successfully Completed Script')
            except Exception as e:
                msg = 'Unexpected Error Running Script: {}'.format(e)
                if logger is not None:
                    logger.error(msg)
                else:
                    print(msg)
        return wrapper
    return main_function


def retry(f):
    """
    A decoration for automatically retrying a function up to 3 times if an Exception is thrown.
    The function must have the keyword argument 'logger' of type 'logging.Logger'.

    Parameters:
        f (function): A reference to the function being decorated.

    Returns:
        function: The wrapper that handles retry attempts.
    """

    def retry_function(*args, **kwargs):
        if 'logger' not in kwargs or type(kwargs['logger']) is not logging.Logger:
            raise Exception('KeyWord Argument \'logger\' of Type \'logging.Logger\' is Required')

        attempt = 1
        while attempt <= 3:
            try:
                if attempt > 1:
                    kwargs['logger'].info('Function \'{}\' Attempt #{}...'.format(f.__name__, attempt))
                return f(*args, **kwargs)
            except Exception as e:
                kwargs['logger'].info('Unexpected Error Attempting Function \'{}\': {}'.format(f.__name__, e))
            attempt += 1
        raise Exception('Retry Attempt Limit Reached for Function \'{}\''.format(f.__name__))
    return retry_function


@retry
def binance_connect(*, logger=None, publicKey='', secretKey=''):
    """
    Create an open connection to the Binance Exchange API.

    Parameters:
        logger (logging.Logger): An open logging object.
        publicKey (str): An account Public API Key.
        secretKey (str): An account Secret API Key.

    Returns:
        binance.client.Client: An open connected client to the Binance Exchange API.
    """

    return binance.client.Client(publicKey, secretKey)


@retry
def get_historical_data(*, logger=None, client=None, symbol='', interval='', startDate=''):
    """
    Download historical pricing data from the Binance Exchange.

    Parameters:
        logger (logging.Logger): An open logging object.
        client (binance.client.Client): An open connected client to the Binance Exchange API.
        symbol (str): The Crypto symbol being downloaded.
        interval (str): Candlestick interval being downloaded.
        startDate (str): Download historical data from this starting date. Ex. "2019-02-01 00:00:00".

    Returns:
        pandas.DataFrame: All data formatted for easy use.
    """

    df = pandas.DataFrame(
        data=client.get_historical_klines(symbol=symbol, interval=interval, start_str=startDate)[:-1],
        columns=[
            'OPEN_TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'CLOSE_TIME',
            'QUOTE_ASSET_VOLUME', 'NUMBER_TRADES', 'TAKER_BASE_ASSET_VOLUME', 'TAKER_QUOTE_ASSET_VOLUME', 'IGNORE'
        ]
    ).drop(
        columns=['QUOTE_ASSET_VOLUME', 'TAKER_BASE_ASSET_VOLUME', 'TAKER_QUOTE_ASSET_VOLUME', 'IGNORE']
    ).sort_values(by=['OPEN_TIME']).reset_index(drop=True)

    df['SYMBOL'] = symbol
    df['INTERVAL'] = interval

    df['OPEN_TIME'] = pandas.to_datetime(df['OPEN_TIME'], unit='ms')
    df['CLOSE_TIME'] = pandas.to_datetime(df['CLOSE_TIME'], unit='ms')

    def format_hour(timestamp):
        timestamp = timestamp.replace(second=0, microsecond=0)
        if timestamp.minute == 59:
            timestamp += numpy.timedelta64(1, 'm')
        timestamp.replace(minute=0)

        return timestamp

    df['OPEN_TIME'] = df['OPEN_TIME'].map(lambda x: format_hour(x))
    df['CLOSE_TIME'] = df['CLOSE_TIME'].map(lambda x: format_hour(x))

    df['OPEN'] = df['OPEN'].astype(float)
    df['HIGH'] = df['HIGH'].astype(float)
    df['LOW'] = df['LOW'].astype(float)
    df['CLOSE'] = df['CLOSE'].astype(float)
    df['VOLUME'] = df['VOLUME'].astype(float)
    df['NUMBER_TRADES'] = df['NUMBER_TRADES'].astype(float)

    return df


def apply_ta(*, data=None):
    """
    Apply TA features to historical pricing data.

    Parameters:
        data (pandas.DataFrame): The historical pricing data.

    Returns:
        pandas.DataFrame: The historical pricing data with additional columns for TA features.
    """

    dataTA = data.copy()

    ta.add_volatility_ta(dataTA, 'HIGH', 'LOW', 'CLOSE', fillna=True, colprefix='')
    ta.add_momentum_ta(dataTA, 'HIGH', 'LOW', 'CLOSE', 'VOLUME', fillna=True, colprefix='')
    ta.add_trend_ta(dataTA, 'HIGH', 'LOW', 'CLOSE', fillna=True, colprefix='')

    return dataTA


def get_file_path(*, create=False, directoryTree=None, fileName=None):
    """
    Return the OS path to a file and create the directories if required.

    Parameters:
        create (bool): True if the directory is allowed to be created.
        directoryTree (tuple): An in-order tuple of sub-directories to reach the file.
        fileName (str): The name of the file at the end of the OS path.

    Returns:
        str: The OS path to the given file.
    """

    path = os.path.join(*directoryTree)
    if create and not os.path.exists(path) or not os.path.isdir(path):
        os.makedirs(path)
    return os.path.join(path, fileName)


def track_errors(*, f=None, items=[], keyName='', **kwargs):
    """
    Run a function for each item in a list, but catch/track any errors.

    Parameters:
        f (Function): The function each item will call.
        items (list): All the items to go through the function.
        keyName (str): The parameter name the item represents in the function.
        **kwargs: The additional keyword arguments given to the function.

    Returns:
        list: All the errors and the stacktrace associated with them. Organized by item.
    """

    errors = []
    for key in tqdm.tqdm(items):
        try:
            kwargs[keyName] = key
            f(**kwargs)
        except Exception as e:
            errors.append('{}: {}'.format(key, e))
    return errors
