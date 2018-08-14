import sys, os, argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_binance, helpers_db
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities

logger = helpers.create_logger('update_balances')


def fun():
    client = helpers_binance.safe_connect(logger)
    if client is None: raise Exception
    db_info = helpers_db.safe_connect(logger)
    if db_info None: raise Exception

    balances = {}
    for coinpair in utilities.COINPAIRS:
        balances[coinpair[:-3]] = helpers_binance.safe_get_asset_balance(logger, client, coinpair[:-3])
        if balances[coinpair[:-3]] is None: raise Exception

    for asset in balances:
        if helpers_db.safe_insert_asset_balance(logger, db_info[0], db_info[1], asset, balances[asset]) is None: raise Exception

    return helpers_db.safe_disconnect(logger, db_info[0])

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Asset Balances').parse_args()

    result = helpers.bullet_proof(logger, 'Updating All Asset Balances in the DB', lambda: fun())
    if result is None: sys.exit(1)
    else: sys.exit(0)
