import sys, os, argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_binance, helpers_db

logger = helpers.create_logger('download_coinpair')


def fun(coinpair):
    client = helpers_binance.safe_connect(logger)
    db_info = helpers_db.safe_connect(logger)
    if client is None or db_info is None: raise Exception

    data = helpers_binance.safe_get_historical_data(logger, client, coinpair)
    policy = helpers_binance.safe_get_trading_policy(logger, client, coinpair)
    if data is None or policy is None: raise Exception

    # TODO: Update DB with data and policy info.

    return helpers_db.safe_disconnect(logger, db_info[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Updating a Coinpair in the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Update', type=str, dest='coinpair', required=True)
    args = parser.parse_args()

    result = helpers.bullet_proof(logger, 'Updating Coinpair \'' + args.coinpair + '\' in the DB', lambda: fun(args.coinpair))
    if result is None: sys.exit(1)
    else: sys.exit(0)
