import sys, os, argparse, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('reset_coinpair')


def fun(**args):
    for coinpair in args['extra']['coinpairs']:
        intervals = []
        for interval in utilities.TIME_INTERVALS:
            temp = helpers_binance.safe_get_historical_data(logger, args['client'], coinpair, interval)
            if temp is None: return 1

            intervals.append(temp)
        data = pandas.concat(intervals, ignore_index=True)

        data = helpers.safe_calculate_overhead(logger, coinpair, data)
        if data is None: return 1

        result = helpers_db.safe_create_table(logger, args['db'], coinpair, data)
        if result is None: return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Resetting a Coinpair\'s History in the DB')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--coinpair', help='the Coinpair to Reset', type=str, dest='coinpair')
    group.add_argument('-a', '--all', help='all Coinpairs to Reset', action='store_true')
    args = parser.parse_args()

    if args.all:
        if input('Are you sure you want to reset all history from the DB? (y) ') != 'y': sys.exit(1)
        if input('Are you absolutely sure you want to reset ALL history from the DB? (y) ') != 'y': sys.exit(1)

        helpers.main_function(logger, 'Resetting ALL History in the DB', fun, client=True, db=True, extra={'coinpairs': utilities.COINPAIRS})
    else:
        if input('Are you sure you want to reset all \'' + args.coinpair + '\' history from the DB? (y) ') != 'y': sys.exit(1)

        helpers.main_function(logger, 'Resetting \'' + args.coinpair + '\' History in the DB', fun, client=True, db=True, extra={'coinpairs': [args.coinpair]})
