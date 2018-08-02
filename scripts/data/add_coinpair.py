import argparse, pandas, math, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('add_coinpair')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Adding a Coinpair into the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to add', type=str, dest='coinpair', required=True)
    parser.add_argument('-r', '--reset', help='True if resetting the DB', action='store_true', required=False)
    args = parser.parse_args()
    error = False

    client = helpers.binance_connect(logger)
    db, db_cursor = helpers.db_connect(logger)

    try:
        step = 0

        logger.info('Getting \'' + args.coinpair + '\' Historical Data and Policies from the Binance API...')
        data = pandas.DataFrame(client.get_historical_klines(symbol=args.coinpair, interval=utilities.TIME_INTERVAL, start_str=utilities.START_DATE), columns=utilities.HISTORY_STRUCTURE)
        policies = client.get_symbol_info(args.coinpair)
        step += 1

        if args.reset:
            logger.info('Creating Table \'' + args.coinpair + '\' in the DB...')
            db_cursor.execute("DROP TABLE IF EXISTS " + args.coinpair + ";")
            db_cursor.execute(
                "CREATE TABLE " + args.coinpair +
                " (OPEN_TIME BIGINT PRIMARY KEY NOT NULL, OPEN REAL NOT NULL, HIGH REAL NOT NULL, LOW REAL NOT NULL, CLOSE REAL NOT NULL, VOLUME REAL NOT NULL, CLOSE_TIME BIGINT NOT NULL, QUOTE_ASSET_VOLUME REAL NOT NULL, NUMBER_TRADES REAL NOT NULL, TAKER_BASE_ASSET_VOLUME REAL NOT NULL, TAKER_QUOTE_ASSET_VOLUME REAL NOT NULL, IGNORE REAL NOT NULL);"
            )
            db.commit()
        step += 1

        if not args.reset:
            logger.info('Downloading \'' + args.coinpair + '\' Historical Data from the DB...')
            db_cursor.execute("SELECT * FROM " + args.coinpair)
            data_old = pandas.DataFrame(db_cursor.fetchall(), columns=utilities.HISTORY_STRUCTURE)
        step += 1

        logger.info('Inserting \'' + args.coinpair + '\' Policies into the DB...')
        db_cursor.execute("INSERT INTO POLICIES VALUES (\'" + args.coinpair + "\', \'" + str(','.join(policies['orderTypes'])) + "\', " + str(policies['baseAssetPrecision']) + ", " +
                          str(policies['filters'][0]['minPrice']) + ", " + str(policies['filters'][0]['maxPrice']) + ", " + str(policies['filters'][0]['tickSize']) + ", " +
                          str(policies['filters'][1]['minQty']) + ", " + str(policies['filters'][1]['maxQty']) + ", " + str(policies['filters'][1]['stepSize']) + ", " +
                          str(policies['filters'][2]['minNotional']) + ") ON CONFLICT DO NOTHING;")
        db.commit()
        step += 1

        logger.info('Inserting \'' + args.coinpair + '\' into the DB...')
        for index, row in data.iterrows():
            sys.stdout.write('\r')
            sys.stdout.write('\tProgress... %d%%' % (math.ceil(index / (len(data.index) - 1) * 100)))
            sys.stdout.flush()

            if len(data_old[data_old['OPEN_TIME'] == row['OPEN_TIME']]) != 0: continue

            db_cursor.execute("INSERT INTO " + args.coinpair + " VALUES (" + str(row['OPEN_TIME']) + ", " + str(row['OPEN']) + ", " + str(row['HIGH']) + ", " + str(row['LOW']) + ", " +
                              str(row['CLOSE']) + ", " + str(row['VOLUME']) + ", " + str(row['CLOSE_TIME']) + ", " + str(row['QUOTE_ASSET_VOLUME']) + ", " + str(row['NUMBER_TRADES']) + ", " +
                              str(row['TAKER_BASE_ASSET_VOLUME']) + ", " + str(row['TAKER_QUOTE_ASSET_VOLUME']) + ", " + str(row['IGNORE']) + ") ON CONFLICT DO NOTHING;")
            db.commit()
        sys.stdout.write('\n')
    except:
        if step == 0: logger.error('Failed to Get \'' + args.coinpair + '\' Historical Data and Policies from the Binance API')
        if step == 1: logger.error('Failed to Create Table \'' + args.coinpair + '\' in the DB...')
        if step == 2: logger.error('Failed to Download \'' + args.coinpair + '\' Historical Data from the DB')
        if step == 3: logger.error('Failed to Insert \'' + args.coinpair + '\' Policies into the DB')
        if step == 4: logger.error('Failed to Insert \'' + args.coinpair + '\' into the DB')
        error = True

    helpers.db_disconnect(db, logger)
    if error: sys.exit(1)
