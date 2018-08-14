import sys, os, helpers, pandas
from binance.client import Client

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities
''' CONNECTING TO BINANCE API '''


def binance_connect():
    return Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)


def safe_connect(logger):
    message = 'Connecting to the Binance API'
    return helpers.bullet_proof(logger, message, lambda: binance_connect())


''' GET HISTORICAL DATA '''


def binance_get_historical_data(client, coinpair):
    data = client.get_historical_klines(symbol=coinpair, interval=utilities.TIME_INTERVAL, start_str=utilities.START_DATE)
    for row in data:
        row.extend(['0', '0', '0', '0', '0'])
    return pandas.DataFrame(data, columns=utilities.HISTORY_STRUCTURE)


def safe_get_historical_data(logger, client, coinpair):
    message = 'Downloading \'' + coinpair + '\' Historical Data from the Binance API'
    return helpers.bullet_proof(logger, message, lambda: binance_get_historical_data(client, coinpair))


''' GET COINPAIR TRADING POLICY '''


def binance_get_trading_policy(client, coinpair):
    return client.get_symbol_info(coinpair)


def safe_get_trading_policy(logger, client, coinpair):
    message = 'Downloading \'' + coinpair + '\' Trading Policy from the Binance API'
    return helpers.bullet_proof(logger, message, lambda: binance_get_trading_policy(client, coinpair))


''' INSERT ASSET BALANCE '''


def binance_get_asset_balance(client, asset):
    return client.get_asset_balance(asset=asset)['free']


def safe_get_asset_balance(logger, client, asset):
    message = 'Downloading \'' + asset + '\' Balance from the Binance API'
    return helpers.bullet_proof(logger, message, lambda: binance_get_asset_balance(client, asset))
