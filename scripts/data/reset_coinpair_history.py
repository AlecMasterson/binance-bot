import sys, os, argparse, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('reset_coinpair')


def reset(client, db, coinpair):
    intervals = []
    for interval in utilities.TIME_INTERVALS:
        temp = helpers_binance.safe_get_historical_data(logger, client, coinpair, interval)
        if temp is None: return False

        intervals.append(temp)
    data = pandas.concat(intervals, ignore_index=True)

    data = helpers.safe_calculate_overhead(logger, coinpair, data)
    if data is None: return False

    result = helpers_db.safe_create_table(logger, db, coinpair, data)
    if result is None: return False

    return True


def fun(**args):
    if not args['extra']['coinpair'] is None:
        if not reset(args['client'], args['db'], args['extra']['coinpair']): return 1
    else:
        for coinpair in utilities.COINPAIRS:
            if not reset(args['client'], args['db'], coinpair): return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Resetting a Coinpair\'s History in the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Reset', type=str, dest='coinpair', required=False)
    args = parser.parse_args()

    if not args.coinpair is None:
        if input('Are you sure you want to reset all history from the DB? (y) ') != 'y': sys.exit(1)
        if input('Are you absolutely sure you want to reset ALL history from the DB? (y) ') != 'y': sys.exit(1)
    else:
        if input('Are you sure you want to reset all \'' + args.coinpair + '\' history from the DB? (y) ') != 'y': sys.exit(1)

    helpers.main_function(logger, 'Restting {} History in the DB'.format('ALL' if args.coinpair is None else '\'' + args.coinpair + '\''), fun, db=True, extra={'coinpair': args.coinpair})
