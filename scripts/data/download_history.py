import sys, os, argparse, pandas, glob
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('download_history')


def download(client, coinpair):
    intervals = []
    for interval in utilities.TIME_INTERVALS:
        temp = helpers_binance.safe_get_historical_data(logger, client, coinpair, interval).sort_values(by=['OPEN_TIME']).reset_index(drop=True)
        if temp is None: return False
        temp = helpers.safe_calculate_overhead(logger, coinpair, temp)
        if temp is None: return False

        intervals.append(temp)
    data = pandas.concat(intervals, ignore_index=True)

    if helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data) is None: return False

    return True


def upload(db, coinpair, data):
    if helpers_db.safe_create_table(logger, db, coinpair, data) is None: return False
    return True


def fun(**args):
    logger.info('Deleting Previously Saved Data')
    for file in glob.glob(os.path.join(os.getcwd(), 'binance-bot', 'data', 'history', '*.csv')):
        os.remove(file)

    for coinpair in args['extra']['coinpairs']:
        data = download(args['client'], coinpair)
        if data is None: return 1
        if args['extra']['upload'] and not upload(args['db'], coinpair, data): return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading History from Binance')
    parser.add_argument('-c', '--coinpair', help='a specific coinpair to download', type=str, dest='coinpair', required=False)
    parser.add_argument('-u', '--upload', help='upload to the DB', action='store_true', required=False)
    args = parser.parse_args()

    coinpairs = []
    if args.coinpair is None: coinpairs = utilities.COINPAIRS
    else: coinpairs.append(args.coinpair)

    db = False
    if args.upload:
        db = True
        if args.coinpair is None:
            if input('Are you sure you want to reset all history in the DB? (y) ') != 'y': sys.exit(1)
            if input('Are you absolutely sure you want to reset ALL history in the DB? (y) ') != 'y': sys.exit(1)
        else:
            if input('Are you sure you want to reset all \'' + args.coinpair + '\' history in the DB? (y) ') != 'y': sys.exit(1)

    message = 'Downloading {} History'.format('ALL' if args.coinpair is None else '\'' + args.coinpair + '\'')
    helpers.main_function(logger, message, fun, client=True, db=db, extra={'coinpairs': coinpairs, 'upload': args.upload})
