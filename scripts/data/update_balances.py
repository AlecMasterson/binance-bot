import argparse, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_binance, helpers_db
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities

logger = helpers.create_logger('update_balances')
if logger is None:
    print('Failed to Create Logger...')
    sys.exit(1)

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Asset Balances').parse_args()
    error = False

    logger.info('Updating All Asset Balances in the DB...')
    try:
        client = helpers_binance.binance_connect(logger)
        if client is None: raise Exception
        db, db_cursor = helpers_db.db_connect(logger)
        if db is None or db_cursor is None: raise Exception

        balances = {}
        for coinpair in utilities.COINPAIRS:
            balances[coinpair[:-3]] = helpers_binance.binance_get_asset_balance(client, coinpair[:-3], logger)
            if balances[coinpair[:-3]] is None: raise Exception

        for asset in balances:
            result = helpers_db.db_insert_asset_balance(db_cursor, asset, balances[asset], logger)
            if result is None: raise Exception
    except:
        logger.error('Failed to Update All Balances in the DB')
        error = True

    helpers_db.db_disconnect(db, logger)

    if error: sys.exit(1)
    sys.exit(0)
