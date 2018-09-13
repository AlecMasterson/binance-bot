import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import helpers, helpers_binance, helpers_db

logger = helpers.create_logger('erase_coinpair')


def fun(client, db, coinpair):

    data = helpers_binance.safe_get_historical_data(logger, client, coinpair)
    if data is None: return 1

    data = helpers.safe_calculate_overhead(logger, coinpair, data)
    if data is None: return 1

    result = helpers_db.safe_create_historical_data_table(logger, db, coinpair, data)
    if result is None: return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Erasing a Coinpair\'s History in the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Erase', type=str, dest='coinpair', required=True)
    args = parser.parse_args()

    if input('Are you sure you want to erase all \'' + args.coinpair + '\' history in the DB? (y) ') != 'y': sys.exit(1)

    client = helpers_binance.safe_connect(logger)
    if client is None: sys.exit(1)
    db = helpers_db.safe_connect(logger)
    if db is None: sys.exit(1)

    exit_status = helpers.bullet_proof(logger, 'Erasing \'' + args.coinpair + '\' History in the DB', lambda: fun(client, db, args.coinpair))

    if exit_status != 0: logger.error('Closing Script with Exit Status ' + str(exit_status))
    else: logger.info('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)
