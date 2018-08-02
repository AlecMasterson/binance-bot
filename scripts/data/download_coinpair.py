import argparse, pandas, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('download_coinpair')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading a Coinpair from the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to download', type=str, dest='coinpair', required=True)
    args = parser.parse_args()
    error = False

    db, db_cursor = helpers.db_connect(logger)

    try:
        step = 0

        logger.info('Downloading \'' + args.coinpair + '\' Historical Data from the DB')
        db_cursor.execute("SELECT * FROM " + args.coinpair)
        history = db_cursor.fetchall()
        step += 1

        logger.info('Writing \'' + args.coinpair + '\' Historical Data to File')
        data = pandas.DataFrame(history, columns=utilities.HISTORY_STRUCTURE)
        data.to_csv('data/history/' + args.coinpair + '.csv', index=False)
    except:
        if step == 0: logger.error('Failed to Download \'' + args.coinpair + '\' Historical Data from the DB')
        if step == 1: logger.error('Failed to Write \'' + args.coinpair + '\' Historical Data to File')
        error = True

    helpers.db_disconnect(db, logger)
    if error: sys.exit(1)
