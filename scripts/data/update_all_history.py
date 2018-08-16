import argparse, sys, os, traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_binance, helpers_db
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('update_coinpairs')
if logger is None:
    print('Failed to Create Logger...')
    sys.exit(1)

db_cursor.execute("INSERT INTO " + message['s'] + " VALUES (" + str(message['k']['t']) + ", " + str(message['k']['o']) + ", " + str(message['k']['h']) + ", " + str(message['k']['l']) + ", " +
                  str(message['k']['c']) + ", " + str(message['k']['v']) + ", " + str(message['k']['T']) + ", " + str(message['k']['q']) + ", " + str(message['k']['n']) + ", " +
                  str(message['k']['V']) + ", " + str(message['k']['Q']) + ", " + str(message['k']['B']) + ", " + str(macd.tail(1).item()) + ", " + str(macd_signal.tail(1).item()) + ", " +
                  str(macd_diff.tail(1).item()) + ", " + str(upperband.tail(1).item()) + ", " + str(lowerband.tail(1).item()) + ") ON CONFLICT DO NOTHING;")
db.commit()

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating all Coinpairs in the DB').parse_args()

    logger.info('Updating All Coinpairs in the DB...')
    try:
        client = helpers_binance.binance_connect(logger)
        if client is None: raise Exception
        db, db_cursor = helpers_db.db_connect(logger)
        if db is None or db_cursor is None: raise Exception

        data = {}
        for coinpair in utilities.COINPAIRS:
            data[coinpair] = helpers_db.db_get_coinpair(db_cursor, coinpair, logger)
            if data[coinpair] is None: raise Exception
            #db_cursor.execute("SELECT * FROM " + coinpair + " ORDER BY OPEN_TIME DESC LIMIT 50;")
            #data[coinpair] = pandas.DataFrame(db_cursor.fetchall()[::-1], columns=utilities.HISTORY_STRUCTURE)

    except:
        logger.error('Failed to Update All Coinpairs in the DB')
        logger.error('\n' + traceback.print_exc())
        error = True

    if not error:
        helpers_db.db_disconnect(db, logger)
        sys.exit(0)
    else:
        sys.exit(1)
