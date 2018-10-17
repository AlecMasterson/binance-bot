import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_db

logger = helpers.create_logger('download_history')


def download(db, coinpair):
    data = helpers_db.safe_get_table(logger, db, coinpair, utilities.HISTORY_STRUCTURE)
    if data is None: return False

    if helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data) is None: return False

    return True


def fun(**args):
    if not args['extra']['coinpair'] is None:
        if not download(args['db'], args['extra']['coinpair']): return 1
    else:
        for coinpair in utilities.COINPAIRS:
            if not download(args['db'], coinpair): return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading All History from the DB')
    parser.add_argument('-c', '--coinpair', help='a specific coinpair to download', type=str, dest='coinpair', required=False)
    args = parser.parse_args()

    helpers.main_function(logger, 'Downloading {} History from the DB'.format('ALL' if args.coinpair is None else '\'' + args.coinpair + '\''), fun, db=True, extra={'coinpair': args.coinpair})
