import argparse, sys, os
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

global errors
errors = 0


def callback(message):
    global errors
    if message['e'] == 'error':
        print('ERROR: Failed to Get \'' + message['s'] + '\' Data')
        errors += 1
    else:
        if message['k']['x']:
            try:
                db_cursor.execute("INSERT INTO " + message['s'] + " VALUES (" + str(message['k']['t']) + ", " + str(message['k']['o']) + ", " + str(message['k']['h']) + ", " + str(message['k']['l']) +
                                  ", " + str(message['k']['c']) + ", " + str(message['k']['v']) + ", " + str(message['k']['T']) + ", " + str(message['k']['q']) + ", " + str(message['k']['n']) + ", " +
                                  str(message['k']['V']) + ", " + str(message['k']['Q']) + ", " + str(message['k']['B']) + ") ON CONFLICT DO NOTHING;")
                db.commit()
                print('INFO: Inserted \'' + message['s'] + '\' into the DB')
            except:
                print('ERROR: Failed to Insert \'' + message['s'] + '\' into the DB')
                errors += 1


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating all Coinpairs in the DB').parse_args()
    error = False

    client = helpers.binance_connect()
    db, db_cursor = helpers.db_connect()

    try:
        step = 0

        print('INFO: Starting Binance API Sockets...')
        manager = BinanceSocketManager(client)
        for coinpair in utilities.COINPAIRS:
            manager.start_kline_socket(coinpair, callback, interval=utilities.TIME_INTERVAL)
        manager.start()
        step += 1
    except:
        if step == 0: print('ERROR: Failed to Start Binance API Sockets')
        error = True

    print('INFO: Starting Infinite Loop... Hold On Tight!')
    while not error and errors < 10:
        continue

    try:
        print('INFO: Closing Binance API Sockets...')
        manager.close()
        reactor.stop()
    except:
        print('ERROR: Failed to Close Binance API Sockets')
        error = True

    helpers.db_disconnect(db)
    if error: sys.exit(1)
