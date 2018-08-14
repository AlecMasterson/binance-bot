import sys, os, argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_db

logger = helpers.create_logger('download_coinpair')


def fun(coinpair):
    db_info = helpers_db.safe_connect(logger)
    if db_info is None: raise Exception

    data = helpers_db.safe_get_historical_data(logger, db_info[1], coinpair)
    if data is None: raise Exception

    if helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data) is None: raise Exception

    policies = helpers_db.safe_get_trading_policies(logger, db_info[1])
    if policies is None: raise Exception

    if helpers.safe_to_file(logger, 'data/policies.csv', policies) is None: raise Exception

    return helpers_db.safe_disconnect(logger, db_info[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading a Coinpair from the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to download', type=str, dest='coinpair', required=True)
    args = parser.parse_args()

    result = helpers.bullet_proof(logger, 'Downloading Coinpair \'' + args.coinpair + '\' from the DB', lambda: fun(args.coinpair))
    if result is None: sys.exit(1)
    else: sys.exit(0)
