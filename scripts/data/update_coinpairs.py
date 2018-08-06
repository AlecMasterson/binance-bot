import argparse, pandas, ta, sys, os
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('update_coinpairs')

global error
error = False


def db_insert(message):
    try:
        close_data = pandas.Series([row['CLOSE'] for index, row in data[message['s']].iterrows()])

        macd = ta.trend.macd(close_data, n_fast=12, n_slow=26, fillna=True)
        macd_signal = ta.trend.macd_signal(close_data, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        macd_diff = ta.trend.macd_diff(close_data, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        upperband = ta.volatility.bollinger_hband(close_data, n=14, ndev=2, fillna=True)
        lowerband = ta.volatility.bollinger_lband(close_data, n=14, ndev=2, fillna=True)

        length = len(data[message['s']].index)
        if length != len(macd) or length != len(macd_signal) or length != len(macd_diff) or length != len(upperband) or length != len(lowerband): return True

        db_cursor.execute("INSERT INTO " + message['s'] + " VALUES (" + str(message['k']['t']) + ", " + str(message['k']['o']) + ", " + str(message['k']['h']) + ", " + str(message['k']['l']) + ", " +
                          str(message['k']['c']) + ", " + str(message['k']['v']) + ", " + str(message['k']['T']) + ", " + str(message['k']['q']) + ", " + str(message['k']['n']) + ", " +
                          str(message['k']['V']) + ", " + str(message['k']['Q']) + ", " + str(message['k']['B']) + ", " + str(macd.tail(1).item()) + ", " + str(macd_signal.tail(1).item()) + ", " +
                          str(macd_diff.tail(1).item()) + ", " + str(upperband.tail(1).item()) + ", " + str(lowerband.tail(1).item()) + ") ON CONFLICT DO NOTHING;")
        db.commit()
        logger.info('Inserted \'' + message['s'] + '\' into the DB')
        return False
    except:
        return True


def callback(message):
    global error
    if message['e'] == 'error':
        logger.error('Failed to Get \'' + message['s'] + '\' Data')
        error = True
    else:
        if message['k']['x']:
            data[message['s']] = data[message['s']].append({'CLOSE': message['k']['c']}, ignore_index=True)
            if db_insert(message):
                logger.error('Failed to Insert \'' + message['s'] + '\' into the DB')
                error = True


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating all Coinpairs in the DB').parse_args()

    client = helpers.binance_connect(logger)
    db, db_cursor = helpers.db_connect(logger)

    try:
        step = 0

        data = {}
        for coinpair in utilities.COINPAIRS:
            db_cursor.execute("SELECT * FROM " + coinpair + " ORDER BY OPEN_TIME DESC LIMIT 50;")
            data[coinpair] = pandas.DataFrame(db_cursor.fetchall()[::-1], columns=utilities.HISTORY_STRUCTURE)
        step += 1

        logger.info('Starting Binance API Sockets...')
        manager = BinanceSocketManager(client)
        for coinpair in utilities.COINPAIRS:
            manager.start_kline_socket(coinpair, callback, interval=utilities.TIME_INTERVAL)
        manager.start()
        step += 1

        logger.info('Starting Infinite Loop... Hold On Tight!')
        while not error:
            continue

        logger.info('Closing Binance API Sockets...')
        manager.close()
        reactor.stop()
    except:
        if step == 0: logger.error('Failed to Download All Historical Data from the DB')
        if step == 1: logger.error('Failed to Start Binance API Sockets')
        if step == 2: logger.error('Failed to Close Binance API Sockets')
        error = True

    helpers.db_disconnect(db, logger)
    if error: sys.exit(1)
