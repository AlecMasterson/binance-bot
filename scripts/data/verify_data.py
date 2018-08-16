import argparse, pandas, sys, os, traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_binance, helpers_db
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('verify_data')

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Validating All Data in the DB').parse_args()

    client = helpers_binance.binance_connect(logger)
    db, db_cursor = helpers_db.db_connect(logger)

    try:
        binance_data = {}
        binance_policies = {}
        for coinpair in utilities.COINPAIRS:
            binance_data[coinpair] = helpers_binance.binance_get_coinpair(client, coinpair, logger)
            if binance_data[coinpair] is None: raise Exception
            binance_data[coinpair] = helpers.calculate_overhead(binance_data[coinpair], coinpair, logger)
            if binance_data[coinpair] is None: raise Exception
            binance_policies[coinpair] = helpers_binance.binance_get_coinpair_policy(client, coinpair, logger)
            if binance_policies[coinpair] is None: raise Exception

        db_data = {}
        for coinpair in utilities.COINPAIRS:
            db_data[coinpair] = helpers_db.db_get_coinpair(db_cursor, coinpair, logger)
            if db_data[coinpair] is None: raise Exception
        policies = helpers_db.db_get_policies(db_cursor, logger)
        if policies is None: raise Exception

        for coinpair in utilities.COINPAIRS:
            diff = (binance_data[coinpair] != db_data[coinpair]).any(1)
            diff_list = diff[diff == True].index
            if len(diff_list) > 0: print('NO')

    except Exception as e:
        logger.error('\n' + traceback.print_exc())
        print(e)
        logger.error('Failed to Verify All Data in the DB')
        helpers_db.db_disconnect(db, logger)
        sys.exit(1)

    logger.info('Successfully Verified All Data in the DB')
