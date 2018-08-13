import pandas, sys, os, traceback
from binance.client import Client

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def binance_connect(logger):
    try:
        logger.info('Connecting to the Binance API...')
        return Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        logger.error('Failed to Connect to the Binance API')
        logger.error('\n' + traceback.print_exc())
        return None


def binance_get_coinpair(client, coinpair, logger):
    try:
        logger.info('Downloading \'' + coinpair + '\' Historical Data from the Binance API...')
        data = client.get_historical_klines(symbol=coinpair, interval=utilities.TIME_INTERVAL, start_str=utilities.START_DATE)
        for row in data:
            row.extend(['0', '0', '0', '0', '0'])
        return pandas.DataFrame(data, columns=utilities.HISTORY_STRUCTURE)
    except:
        logger.error('Failed to Download \'' + coinpair + '\' Historical Data from the Binance API')
        logger.error('\n' + traceback.print_exc())
        return None


def binance_get_coinpair_policy(client, coinpair, logger):
    try:
        logger.info('Downloading \'' + coinpair + '\' Trading Policy from the Binance API...')
        return client.get_symbol_info(coinpair)
    except:
        logger.error('Failed to Download \'' + coinpair + '\' Trading Policy from the Binance API')
        logger.error('\n' + traceback.print_exc())
        return None


def binance_get_asset_balance(client, asset, logger):
    try:
        logger.info('Downloading \'' + asset + '\' Balance from the Binance API...')
        return client.get_asset_balance(asset=asset)['free']
    except:
        logger.error('Failed to Download \'' + asset + '\' Balance from the Binance API')
        logger.error('\n' + traceback.print_exc())
        return None
