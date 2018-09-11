import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import helpers, helpers_db

logger = helpers.create_logger('download_data')


def fun(db):
    for coinpair in utilities.COINPAIRS:
        data = helpers_db.safe_get_historical_data(logger, db, coinpair)
        if data is None: return 1

        if helpers.safe_to_file(logger, 'data/history/' + coinpair + '.csv', data) is None: return 1

    return 0


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Downloading All Data from the DB').parser.parse_args()

	db = helpers_db.safe_connect(logger)
    if db is None: sys.exit(1)

    exit_status = helpers.bullet_proof(logger, 'Downloading All Data from the DB', lambda: fun(db))

	logger.error('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)
