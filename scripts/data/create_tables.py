import sys, os, argparse, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_db

logger = helpers.create_logger('create_tables')


def fun(db):
	df = pandas.DataFrame(columns=utilities.HISTORY_STRUCTURE)
	for coinpair in utilities.COINPAIRS:
		if helpers_db.safe_create_historical_data_table(db, coinpair, df) is None: return 1

	df = pandas.DataFrame(columns=utilities.BALANCE_STRUCTURE)
	if helpers_db.safe_create_asset_balances_table(db, df) is None: return 1

    return 0


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Creating Empty Tables in the DB').parse_args()

    db = helpers_db.safe_connect(logger)
    if db is None: sys.exit(1)

    exit_status = helpers.bullet_proof(logger, 'Creating Empty Tables in the DB', lambda: fun(db))

    logger.error('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)
