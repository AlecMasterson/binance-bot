from util.decor import retry
import binance.client
import os
import pandas
import numpy


@retry
def binance_connect(*, logger):
    """
    Create an open connection to the Binance Exchange API.

    Parameters:
        logger (logging.Logger): An open logging object.

    Returns:
        binance.client.Client: An open connected client to the Binance Exchange API.
    """

    logger.info('Connecting to the Binance Exchange API...')
    client = binance.client.Client(
        os.environ['BINANCE_KEY_PUBLIC'],
        os.environ['BINANCE_KEY_PRIVATE']
    )
    logger.info('Connected to the Binance Exchange API')

    return client


@retry
def get_historical_data(*, client, symbol, interval, startDate):
    """
    Return historical pricing data from the Binance Exchange.

    Parameters:
        client (binance.client.Client): An open connected client to the Binance Exchange API.
        symbol (str): A Crypto-Pair symbol.
        interval (str): An OHLC candlestick width.
        startDate (str): Data will start from this datetime in UTC. Format: '%Y-%m-%d %H:%M:%S'

    Returns:
        pandas.core.frame.DataFrame: Historical pricing data for the given symbol and interval.
    """

    raw = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=startDate
    )

    df = pandas.DataFrame(
        data=raw[:-1],
        columns=[
            'OPEN_TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'CLOSE_TIME',
            'QUOTE_ASSET_VOLUME', 'NUMBER_TRADES', 'TAKER_BASE_ASSET_VOLUME', 'TAKER_QUOTE_ASSET_VOLUME', 'IGNORE'
        ]
    ).drop(
        columns=['QUOTE_ASSET_VOLUME', 'TAKER_BASE_ASSET_VOLUME', 'TAKER_QUOTE_ASSET_VOLUME', 'IGNORE']
    ).sort_values(
        by=['OPEN_TIME']
    ).reset_index(
        drop=True
    ).rename(
        {
            'OPEN_TIME': 'open_time',
            'OPEN': 'open',
            'HIGH': 'high',
            'LOW': 'low',
            'CLOSE': 'close',
            'NUMBER_TRADES': 'number_trades',
            'VOLUME': 'volume',
            'CLOSE_TIME': 'close_time'
        },
        axis='columns'
    )

    df['symbol'] = symbol
    df['width'] = interval

    df['open_time'] = pandas.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pandas.to_datetime(df['close_time'], unit='ms')

    def format_hour(timestamp):
        timestamp = timestamp.replace(second=0, microsecond=0)
        if timestamp.minute == 59:
            timestamp += numpy.timedelta64(1, 'm')
        timestamp.replace(minute=0)

        return timestamp

    df['open_time'] = df['open_time'].map(lambda x: format_hour(x))
    df['close_time'] = df['close_time'].map(lambda x: format_hour(x))

    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['number_trades'] = df['number_trades'].astype(float)

    return df
