import sys, os, argparse, pandas, glob
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('reset_coinpair')


def reset(client, db, coinpair, save):
    intervals = []
    for interval in utilities.TIME_INTERVALS:
        temp = helpers_binance.safe_get_historical_data(logger, client, coinpair, interval)
        if temp is None: return False

        intervals.append(temp.sort_values(by=['OPEN_TIME']).reset_index(drop=True))
    data = pandas.concat(intervals, ignore_index=True).sort_values(by=['INTERVAL']).reset_index(drop=True)

    data = helpers.safe_calculate_overhead(logger, coinpair, data)
    if data is None: return False

    if save and helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data) is None: return False
    elif not save and helpers_db.safe_create_table(logger, db, coinpair, data) is None: return False

    return True


def fun(**args):
    if args['extra']['save']:
        logger.info('Deleting Previously Saved Data')
        for file in glob.glob(os.path.join(os.getcwd(), 'binance-bot', 'data', 'history', '*.csv')):
            os.remove(file)

    for coinpair in args['extra']['coinpairs']:
        if not reset(args['client'], args['db'], coinpair, args['extra']['save']): return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Resetting Coinpair History')
    parser.add_argument('-c', '--coinpair', help='the coinpair to Reset', type=str, dest='coinpair', required=False)
    parser.add_argument('-s', '--save', help='save data locally ONLY', action='store_true', required=False)
    args = parser.parse_args()

    if not args.save and args.coinpair is None:
        if input('Are you sure you want to reset all history from the DB? (y) ') != 'y': sys.exit(1)
        if input('Are you absolutely sure you want to reset ALL history from the DB? (y) ') != 'y': sys.exit(1)
    elif not args.save:
        if input('Are you sure you want to reset all \'' + args.coinpair + '\' history from the DB? (y) ') != 'y': sys.exit(1)

    coinpairs = []
    if args.coinpair is None: coinpairs = utilities.COINPAIRS
    else: coinpairs.append(args.coinpair)

    helpers.main_function(
        logger, 'Resetting {} History'.format('ALL' if args.coinpair is None else '\'' + args.coinpair + '\''), fun, client=True, db=True, extra={
            'coinpairs': coinpairs,
            'save': args.save
        })
