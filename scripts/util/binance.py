import binance.client
import collections
import datetime
import numpy
import os
import pandas


def binance_connect(*, logger):
    """
    Create an open connection to the Binance Exchange API.

    Parameters:
        logger (logging.Logger): An open logging object.

    Returns:
        binance.client.Client: An open connected client to the Binance Exchange API.
    """

    client = binance.client.Client(
        os.environ['BINANCE_KEY_PUBLIC'],
        os.environ['BINANCE_KEY_PRIVATE']
    )

    logger.info('Connected to the Binance Exchange API')
    return client


def get_historical_data(*, logger, client, symbol, interval, startDate):
    """
    Return historical pricing data from the Binance Exchange.

    Parameters:
        logger (logging.Logger): An open logging object.
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
            'OPEN_TIME': 'openTime',
            'OPEN': 'openPrice',
            'HIGH': 'high',
            'LOW': 'low',
            'CLOSE': 'closePrice',
            'NUMBER_TRADES': 'numberTrades',
            'VOLUME': 'volume',
            'CLOSE_TIME': 'closeTime'
        },
        axis='columns'
    )

    df['openTime'] = pandas.to_datetime(df['openTime'], unit='ms')
    df['closeTime'] = pandas.to_datetime(df['closeTime'], unit='ms')

    def format_hour(timestamp):
        timestamp = timestamp.replace(second=0, microsecond=0)
        if timestamp.minute == 59:
            timestamp += numpy.timedelta64(1, 'm')
        timestamp.replace(minute=0)

        return timestamp

    df['openTime'] = df['openTime'].map(lambda x: format_hour(x))
    df['closeTime'] = df['closeTime'].map(lambda x: format_hour(x))

    df['openPrice'] = df['openPrice'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['closePrice'] = df['closePrice'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['numberTrades'] = df['numberTrades'].astype(float)

    intervalTimeDelta = datetime.timedelta(hours=int(interval.split('h')[0]))
    expectedOpenTimes = numpy.arange(
        datetime.datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S'),
        datetime.datetime.utcnow() - intervalTimeDelta,
        intervalTimeDelta
    ).astype(pandas.Timestamp)

    if collections.Counter(df['openTime']) != collections.Counter(expectedOpenTimes):
        logger.warning('(Symbol,Interval) - ({},{}) - Downloaded Data Missing Entries. Attempting to Fix...'.format(symbol, interval))

        df = df.set_index('openTime').reindex(
            pandas.Index(expectedOpenTimes, name='openTime')
        ).reset_index().fillna(numpy.nan).interpolate(limit_direction='backward')
        df['closeTime'].fillna(df['openTime'] + intervalTimeDelta, inplace=True)
        df.dropna(inplace=True)

    if collections.Counter(df['openTime']) != collections.Counter(expectedOpenTimes):
        raise Exception('(Symbol,Interval) - ({},{}) - Downloaded Data Missing Entries'.format(symbol, interval))

    df['symbol'] = symbol
    df['width'] = interval

    df = df.sort_values(by=['openTime']).reset_index(drop=True)

    return df
