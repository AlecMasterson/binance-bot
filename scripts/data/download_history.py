import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_db

logger = helpers.create_logger('download_history')


def fun(**args):
    for coinpair in utilities.COINPAIRS:
        data = helpers_db.safe_get_table(logger, args['db'], coinpair, utilities.HISTORY_STRUCTURE)
        if data is None: continue

        helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data)

    return 0


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Downloading All History from the DB').parse_args()

    helpers.main_function(logger, 'Downloading All History from the DB', fun, db=True)
