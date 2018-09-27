import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import helpers, helpers_binance, helpers_db

logger = helpers.create_logger('erase_coinpair')


def fun(**args):

    data = helpers_binance.safe_get_historical_data(logger, args['client'], args['extra']['coinpair'], args['extra']['time_interval'])
    if data is None: return 1

    data = helpers.safe_calculate_overhead(logger, args['extra']['coinpair'], data)
    if data is None: return 1

    result = helpers_db.safe_create_table(logger, args['db'], args['extra']['coinpair'], data)
    if result is None: return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Erasing a Coinpair\'s History in the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Erase', type=str, dest='coinpair', required=True)
    parser.add_argument('-t', help='the time interval', type=str, dest='time_interval', required=True, choices=['5m', '30m', '1h', '2h', '4h'])
    args = parser.parse_args()

    if input('Are you sure you want to erase all \'' + args.coinpair + '\' history from the DB? (y) ') != 'y': sys.exit(1)

    helpers.main_function(logger, 'Erasing \'' + args.coinpair + '\' History from the DB', fun, client=True, db=True, extra={'coinpair': args.coinpair, 'time_interval': args.time_interval})
