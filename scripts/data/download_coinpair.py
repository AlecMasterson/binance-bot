import argparse, sys, os, traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_db
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('download_coinpair')
if logger is None:
    print('Failed to Create Logger...')
    sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading a Coinpair from the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to download', type=str, dest='coinpair', required=True)
    args = parser.parse_args()
    error = False

    logger.info('Downloading Coinpair \'' + args.coinpair + '\' from the DB...')
    try:
        db, db_cursor = helpers_db.db_connect(logger)
        if db is None or db_cursor is None: raise Exception

        history = helpers_db.db_get_coinpair(db_cursor, args.coinpair, logger)
        if history is None: raise Exception

        result = helpers.to_file(data, 'data/history/' + args.coinpair + '.csv', logger)
        if result is None: raise Exception

        policies = helpers_db.db_get_policies(db_cursor, logger)
        if policies is None: raise Exception

        result = helpers.to_file(policies, 'data/policies.csv', logger)
        if result is None: raise Exception
    except:
        logger.error('Failed to Download Coinpair \'' + args.coinpair + '\' from the DB')
        logger.error('\n' + traceback.print_exc())
        error = True

    if not error:
        helpers_db.db_disconnect(db, logger)
        sys.exit(0)
    else:
        sys.exit(1)
