import util.binance
import util.db
import datetime
import os
import ta


def get_historical_data(*, logger, client, symbol, interval):
    """
    Return historical pricing data from the Binance Exchange formatted for use.

    Parameters:
        logger (logging.Logger): An open logging object.
        client (binance.client.Client): An open connected client to the Binance Exchange API.
        symbol (str): A Crypto-Pair symbol.
        interval (str): An OHLC candlestick width.

    Returns:
        pandas.core.frame.DataFrame: Historical pricing data for the given symbol and interval.
    """

    data = util.binance.get_historical_data(
        client=client,
        symbol=symbol,
        interval=interval
    )

    ta.add_momentum_ta(data, 'high', 'low', 'close', 'volume', fillna=True, colprefix='')
    ta.add_trend_ta(data, 'high', 'low', 'close', fillna=True, colprefix='')
    ta.add_volatility_ta(data, 'high', 'low', 'close', fillna=True, colprefix='')

    data = util.db.organize_table_history(data=data)

    return data


def get_file_path(*, create, directoryTree, fileName):
    """
    Return an OS path to a file and create the directories if required.

    Parameters:
        create (bool): True if the directory tree is allowed to be created.
        directoryTree (tuple): An in-order tuple of sub-directories to reach the file.
        fileName (str): Name of the file at the end of the OS path.

    Returns:
        str: An OS path to the file.
    """

    path = os.path.join(*directoryTree)
    if create and (not os.path.exists(path) or not os.path.isdir(path)):
        os.makedirs(path)
    return os.path.join(path, fileName)


def is_recent(*, data):
    if len(data) == 0:
        return False

    intervals = data['width'].unique()

    for interval in intervals:
        tempData = data[data['width'] == interval].sort_values(
            by=['open_time']
        ).reset_index(
            drop=True
        )

        interval = tempData['close_time'].iloc[-1] - tempData['open_time'].iloc[-1]
        if datetime.datetime.now() > (tempData['close_time'].iloc[-1] + interval):
            return False
    return True
