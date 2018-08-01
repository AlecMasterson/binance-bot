import argparse, pandas, math, sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Adding a Coinpair into the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to add', type=str, dest='coinpair', required=True)
    args = parser.parse_args()
    error = False

    client = helpers.binance_connect()
    db, db_cursor = helpers.db_connect()

    try:
        step = 0

        print('INFO: Getting \'' + args.coinpair + '\' Historical Data from the Binance API...')
        data = pandas.DataFrame(client.get_historical_klines(symbol=args.coinpair, interval=utilities.TIME_INTERVAL, start_str=utilities.START_DATE), columns=utilities.HISTORY_STRUCTURE)
        step += 1

        print('INFO: Creating Table \'' + args.coinpair + '\' in the DB...')
        db_cursor.execute("DROP TABLE IF EXISTS " + args.coinpair + ";")
        db_cursor.execute(
            "CREATE TABLE " + args.coinpair +
            " (OPEN_TIME BIGINT PRIMARY KEY NOT NULL, OPEN REAL NOT NULL, HIGH REAL NOT NULL, LOW REAL NOT NULL, CLOSE REAL NOT NULL, VOLUME REAL NOT NULL, CLOSE_TIME BIGINT NOT NULL, QUOTE_ASSET_VOLUME REAL NOT NULL, NUMBER_TRADES REAL NOT NULL, TAKER_BASE_ASSET_VOLUME REAL NOT NULL, TAKER_QUOTE_ASSET_VOLUME REAL NOT NULL, IGNORE REAL NOT NULL);"
        )
        db.commit()
        step += 1

        print('INFO: Inserting \'' + args.coinpair + '\' into the DB...')
        for index, row in data.iterrows():
            db_cursor.execute("INSERT INTO " + args.coinpair + " VALUES (" + str(row['OPEN_TIME']) + ", " + str(row['OPEN']) + ", " + str(row['HIGH']) + ", " + str(row['LOW']) + ", " +
                              str(row['CLOSE']) + ", " + str(row['VOLUME']) + ", " + str(row['CLOSE_TIME']) + ", " + str(row['QUOTE_ASSET_VOLUME']) + ", " + str(row['NUMBER_TRADES']) + ", " +
                              str(row['TAKER_BASE_ASSET_VOLUME']) + ", " + str(row['TAKER_QUOTE_ASSET_VOLUME']) + ", " + str(row['IGNORE']) + ") ON CONFLICT DO NOTHING;")
            db.commit()
            sys.stdout.write('\r')
            sys.stdout.write('\tProgress... %d%%' % (math.ceil(index / (len(data.index) - 1) * 100)))
            sys.stdout.flush()
    except:
        if step == 0: print('ERROR: Failed to Get \'' + args.coinpair + '\' Historical Data from the Binance API')
        if step == 1: print('ERROR: Failed to Create Table \'' + args.coinpair + '\' in the DB...')
        if step == 2: print('ERROR: Failed to Insert \'' + args.coinpair + '\' into the DB')
        error = True

    helpers.db_disconnect(db)
    if error: sys.exit(1)
