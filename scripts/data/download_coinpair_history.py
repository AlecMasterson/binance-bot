import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import helpers, helpers_db

logger = helpers.create_logger('download_coinpair')


def fun(coinpair):
    db = helpers_db.safe_connect(logger)
    if db is None: return None

    data = helpers_db.safe_get_historical_data(logger, db, coinpair)
    if data is None: return None

    return helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading a Coinpair\'s History from the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Download', type=str, dest='coinpair', required=True)
    args = parser.parse_args()

    message = 'Downloading \'' + args.coinpair + '\' History from the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun(args.coinpair))
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
