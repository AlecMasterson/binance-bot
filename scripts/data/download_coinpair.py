import argparse, pandas, sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading a Coinpair from the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to download', type=str, dest='coinpair', required=True)
    args = parser.parse_args()
    error = False

    db, db_cursor = helpers.db_connect()

    try:
        step = 0

        print('INFO: Downloading \'' + args.coinpair + '\' Historical Data from the DB')
        db_cursor.execute("SELECT * FROM " + args.coinpair)
        history = db_cursor.fetchall()
        step += 1

        print('INFO: Writing \'' + args.coinpair + '\' Historical Data to File')
        data = pandas.DataFrame(history, columns=utilities.HISTORY_STRUCTURE)
        data.to_csv('data/history/' + args.coinpair + '.csv', index=False)
    except:
        if step == 0: print('ERROR: Failed to Download \'' + args.coinpair + '\' Historical Data from the DB')
        if step == 1: print('ERROR: Failed to Write \'' + args.coinpair + '\' Historical Data to File')
        error = True

    helpers.db_disconnect(db)
    if error: sys.exit(1)
