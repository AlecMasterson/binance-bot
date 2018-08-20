import sys, os, argparse
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import helpers, helpers_binance, helpers_db

logger = helpers.create_logger('reset_coinpair')


def fun(coinpair):
    client = helpers_binance.safe_connect(logger)
    if client is None: return None
    db = helpers_db.safe_connect(logger)
    if db is None: return None

    data = helpers_binance.safe_get_historical_data(logger, client, coinpair)
    if data is None: return None

    data = helpers.safe_calculate_overhead(logger, coinpair, data)
    if data is None: return None

    return helpers_db.safe_create_historical_data_table(logger, db, coinpair, data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Resetting a Coinpair\'s History in the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Reset', type=str, dest='coinpair', required=True)
    args = parser.parse_args()

    message = 'Resetting \'' + args.coinpair + '\' History in the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun(args.coinpair))
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
