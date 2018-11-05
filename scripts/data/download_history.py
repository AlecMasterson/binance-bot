import sys, os, argparse, pandas, glob
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('download_history')


def download(client, db, coinpair):
    if not client is None:
        intervals = []
        for interval in utilities.TIME_INTERVALS:
            temp = helpers_binance.safe_get_historical_data(logger, client, coinpair, interval)
            if temp is None: return False
            temp = helpers.safe_calculate_overhead(logger, coinpair, temp)
            if temp is None: return False

            intervals.append(temp.sort_values(by=['OPEN_TIME']).reset_index(drop=True))
        data = pandas.concat(intervals, ignore_index=True).sort_values(by=['INTERVAL']).reset_index(drop=True)
    else:
        data = helpers_db.safe_get_table(logger, db, coinpair, utilities.HISTORY_STRUCTURE)
        if data is None: return False

    if helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data) is None: return False

    return True


def fun(**args):
    logger.info('Deleting Previously Saved Data')
    for file in glob.glob(os.path.join(os.getcwd(), 'binance-bot', 'data', 'history', '*.csv')):
        os.remove(file)

    for coinpair in args['extra']['coinpairs']:
        if not download(args['client'], args['db'], coinpair): return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading All History from the DB')
    parser.add_argument('-c', '--coinpair', help='a specific coinpair to download', type=str, dest='coinpair', required=False)
    parser.add_argument('-b', '--binance', help='download from Binance', action='store_true', required=False)
    args = parser.parse_args()

    coinpairs = []
    if args.coinpair is None: coinpairs = utilities.COINPAIRS
    else: coinpairs.append(args.coinpair)

    client = db = False
    if args.binance is None: db = True
    else: client = True

    message = 'Downloading {} History from {}'.format('ALL' if args.coinpair is None else '\'' + args.coinpair + '\'', 'the DB' if args.binance is None else 'Binance')
    helpers.main_function(logger, message, fun, client=client, db=db, extra={'coinpairs': coinpairs})
