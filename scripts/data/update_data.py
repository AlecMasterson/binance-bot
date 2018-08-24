import sys, os, argparse, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_data')


def test_connection(client):
    if client.get_system_status()['status'] == 1: return False
    return True


def update_assets(client, db):
    balances = pandas.DataFrame(columns=utilities.BALANCE_STRUCTURE)
    for coinpair in utilities.COINPAIRS:
        balance = helpers_binance.safe_get_asset_balance(logger, client, coinpair[:-3])
        if balance is None: return None
        balances = balances.append({'ASSET': coinpair[:-3], 'FREE': balance}, ignore_index=True)
    helpers_db.safe_create_asset_balances_table(logger, db, balances)


def fun(client, db):

    connection_status = True
    while connection_status:
        update_assets(client, db)

        connection_status = test_connection(client)

    return helpers_db.safe_create_asset_balances_table(logger, db, balances)


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating Data in the DB').parse_args()

    client = helpers_binance.safe_connect(logger)
    db = helpers_db.safe_connect(logger)
    if client is None or db is None: sys.exit(1)

    exit_status = helpers.bullet_proof(logger, 'Updating Data in the DB', lambda: fun(client, db))

    logger.error('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)
