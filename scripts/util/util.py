import util.binance
import util.db
import ta
import os
import tqdm


def get_historical_data(*, logger, client, symbol, interval):
    """
    Return historical pricing data from the Binance Exchange.

    Parameters:
        logger (logging.Logger): An open logging object.
        client (binance.client.Client): An open connected client to the Binance Exchange API.
        A Crypto-Pair symbol.
        interval (str): The OHLC candlestick width.

    Returns:
        pandas.core.frame.DataFrame: Historical pricing data for the given symbol and interval.
    """

    data = util.binance.get_historical_data(
        client=client,
        symbol=symbol,
        interval=interval
    )

    data = apply_ta(data=data)
    data = util.db.organize_table_history(data=data)

    return data


def apply_ta(*, data):
    """
    Apply TA features to historical pricing data.

    Parameters:
        data (pandas.DataFrame): Historical pricing data.

    Returns:
        pandas.core.frame.DataFrame: Historical pricing data with additional columns of TA features.
    """

    dataTA = data.copy()

    ta.add_momentum_ta(dataTA, 'high', 'low', 'close', 'volume', fillna=True, colprefix='')
    ta.add_trend_ta(dataTA, 'high', 'low', 'close', fillna=True, colprefix='')
    ta.add_volatility_ta(dataTA, 'high', 'low', 'close', fillna=True, colprefix='')

    return dataTA


def get_file_path(*, create, directoryTree, fileName):
    """
    Return an OS path to a file and create the directories if required.

    Parameters:
        create (bool): True if the directory is allowed to be created.
        directoryTree (tuple): An in-order tuple of sub-directories to reach the file.
        fileName (str): The name of the file at the end of the OS path.

    Returns:
        str: An OS path to the given file.
    """

    path = os.path.join(*directoryTree)
    if create and (not os.path.exists(path) or not os.path.isdir(path)):
        os.makedirs(path)
    return os.path.join(path, fileName)


def track_errors(*, f, items, keyName, **kwargs):
    """
    Run a function for each item in a list, but catch/track any errors.

    Parameters:
        f (Function): The function each item will call.
        items (list): All the items to go through the function.
        keyName (str): The parameter name the item represents in the function.
        **kwargs: The additional keyword arguments given to the function.

    Returns:
        list: All the errors organized by keyName.
    """

    errors = []
    for key in tqdm.tqdm(items):
        try:
            kwargs[keyName] = key
            f(**kwargs)
        except Exception as e:
            errors.append('{}: {}'.format(key, e))
    return errors
