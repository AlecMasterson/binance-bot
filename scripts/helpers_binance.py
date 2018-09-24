import utilities, helpers, pandas
from binance.client import Client


def connect():
    return Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)


''' GET '''


def get_historical_data(client, coinpair):
    data = client.get_historical_klines(symbol=coinpair, interval=utilities.TIME_INTERVAL, start_str=utilities.START_DATE)
    for row in data:
        row.extend(['0', '0', '0', '0', '0'])
    return pandas.DataFrame(data, columns=utilities.HISTORY_STRUCTURE)[:-1]


def get_recent_data(client, coinpair):
    data = client.get_klines(symbol=coinpair, interval=utilities.TIME_INTERVAL, limit=200)
    for row in data:
        row.extend(['0', '0', '0', '0', '0'])
    return pandas.DataFrame(data, columns=utilities.HISTORY_STRUCTURE)[:-1]


def get_trading_policy(client, coinpair):
    return client.get_symbol_info(coinpair)


def get_asset_balance(client, asset):
    return client.get_asset_balance(asset=asset)['free']


def create_order(client, coinpair, side, quantity, price):
    return client.create_order(symbol=coinpair, side=side, type='LIMIT', timeInForce='GTC', quantity=quantity, price=price)


def get_order(client, coinpair, orderId):
    return client.get_order(symbol=coinpair, orderId=orderId)


def cancel_order(client, coinpair, orderId):
    return client.cancel_order(symbol=coinpair, orderId=orderId)


''' SAFE '''


def safe_connect(logger):
    return helpers.bullet_proof(logger, 'Connecting to the Binance API', lambda: connect())


def safe_get_historical_data(logger, client, coinpair):
    return helpers.bullet_proof(logger, 'Downloading \'' + coinpair + '\' Historical Data from the Binance API', lambda: get_historical_data(client, coinpair))


def safe_get_recent_data(logger, client, coinpair):
    return helpers.bullet_proof(logger, 'Downloading \'' + coinpair + '\' Recent Data from the Binance API', lambda: get_recent_data(client, coinpair))


def safe_get_trading_policy(logger, client, coinpair):
    return helpers.bullet_proof(logger, 'Downloading \'' + coinpair + '\' Trading Policy from the Binance API', lambda: get_trading_policy(client, coinpair))


def safe_get_asset_balance(logger, client, asset):
    return helpers.bullet_proof(logger, 'Downloading \'' + asset + '\' Balance from the Binance API', lambda: get_asset_balance(client, asset))


def safe_create_order(logger, client, coinpair, side, quantity, price):
    return helpers.bullet_proof(logger, 'Setting ' + side + ' Order on \'' + coinpair + '\' for Price: ' + str(price) + ' and Quantity: ' + str(quantity),
                                lambda: create_order(client, coinpair, side, quantity, price))


def safe_get_order(logger, client, coinpair, orderId):
    return helpers.bullet_proof(logger, 'Downloading Order \'' + str(orderId) + '\' from the Binance API', lambda: get_order(client, coinpair, orderId))


def safe_cancel_order(logger, client, coinpair, orderId):
    return helpers.bullet_proof(logger, 'Cancelling Order \'' + str(orderId) + '\' from the Binance API', lambda: cancel_order(client, coinpair, orderId))
