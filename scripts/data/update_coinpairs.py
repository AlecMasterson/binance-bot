import argparse, time, sys, os
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

global errors
errors = 0

logger = helpers.create_logger('update_coinpairs')


def db_insert(message):
    try:
        db_cursor.execute("INSERT INTO " + message['s'] + " VALUES (" + str(message['k']['t']) + ", " + str(message['k']['o']) + ", " + str(message['k']['h']) + ", " + str(message['k']['l']) + ", " +
                          str(message['k']['c']) + ", " + str(message['k']['v']) + ", " + str(message['k']['T']) + ", " + str(message['k']['q']) + ", " + str(message['k']['n']) + ", " +
                          str(message['k']['V']) + ", " + str(message['k']['Q']) + ", " + str(message['k']['B']) + ") ON CONFLICT DO NOTHING;")
        db.commit()
        logger.info('Inserted \'' + message['s'] + '\' into the DB')
        return False
    except:
        return True


def callback(message):
    global errors
    if message['e'] == 'error':
        logger.error('Failed to Get \'' + message['s'] + '\' Data')
        errors += 1
    else:
        if message['k']['x']:
            attempt = 1
            while db_insert(message):
                logger.error('Failed to Insert \'' + message['s'] + '\' into the DB - Attempt ' + str(attempt))
                errors += 1
                attempt += 1
                time.sleep(5)


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating all Coinpairs in the DB').parse_args()
    error = False

    client = helpers.binance_connect(logger)
    db, db_cursor = helpers.db_connect(logger)

    try:
        logger.info('Starting Binance API Sockets...')
        manager = BinanceSocketManager(client)
        for coinpair in utilities.COINPAIRS:
            manager.start_kline_socket(coinpair, callback, interval=utilities.TIME_INTERVAL)
        manager.start()
    except:
        if step == 0: logger.error('Failed to Start Binance API Sockets')
        error = True

    if not error: logger.info('Starting Infinite Loop... Hold On Tight!')
    while not error and errors < 10:
        continue

    try:
        logger.info('Closing Binance API Sockets...')
        manager.close()
        reactor.stop()
    except:
        logger.error('Failed to Close Binance API Sockets')
        error = True

    helpers.db_disconnect(db, logger)
    if error: sys.exit(1)
