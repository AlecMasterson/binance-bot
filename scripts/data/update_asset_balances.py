import sys, os, argparse, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_balances')


def fun():
    client = helpers_binance.safe_connect(logger)
    if client is None: return None
    db = helpers_db.safe_connect(logger)
    if db is None: return None

    balances = pandas.DataFrame(columns=utilities.BALANCE_STRUCTURE)
    for coinpair in utilities.COINPAIRS:
        balance = helpers_binance.safe_get_asset_balance(logger, client, coinpair[:-3])
        if balance is None: return None
        balances = balances.append({'ASSET': coinpair[:-3], 'FREE': balance}, ignore_index=True)

    return helpers_db.safe_create_asset_balances_table(logger, db, balances)


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating Asset Balances in the DB').parse_args()

    message = 'Updating Asset Balances in the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun())
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
