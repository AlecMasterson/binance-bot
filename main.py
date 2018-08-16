import sys, utilities, argparse, pandas
from scripts import helpers, helpers_binance, helpers_db, strategy

logger = helpers.create_logger('main')


def fun():
    client = helpers_binance.safe_connect(logger)
    if client is None: raise Exception
    db_info = helpers_db.safe_connect(logger)
    if db_info is None: raise Exception

    data = helpers_db.safe_get_historical_data(logger, db_info[1], 'BNBBTC')
    if data is None: raise Exception

    balance = helpers_db.safe_get_asset_balance(logger, db_info[1], 'BNB')
    if balance is None: raise Exception

    action = 'HOLD'        #strategy.action(data)
    logger.info('Bot Chooses Action: ' + action)

    if action != 'HOLD':
        price = data.at[len(data) - 1, 'CLOSE']
        if action == 'BUY': helpers.safe_buy(logger, client, 'BNBBTC', price)
        if action == 'SELL': helpers.safe_sell(logger, client, 'BNBBTC', price)

    return helpers_db.safe_disconnect(logger, db_info[0])


# TODO: Support more than just BNBBTC...
if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for the Binance Bot').parse_args()

    result = helpers.bullet_proof(logger, 'Main Script', lambda: fun())
    if result is None: sys.exit(1)
    else: sys.exit(0)
