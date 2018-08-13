import argparse, pandas, math, ta, sys, os, traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_binance, helpers_db
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('add_coinpair')
if logger is None:
    print('Failed to Create Logger...')
    sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Adding a Coinpair into the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to add', type=str, dest='coinpair', required=True)
    parser.add_argument('-r', '--reset', help='True if resetting the DB', action='store_true', required=False)
    args = parser.parse_args()
    error = False

    logger.info('Adding Coinpair \'' + args.coinpair + '\' into the DB...')
    try:
        client = helpers.binance_connect(logger)
        if client is None: raise Exception
        db, db_cursor = helpers.db_connect(logger)
        if db is None or db_cursor is None: raise Exception

        data = helpers_binance.binance_get_coinpair(client, args.coinpair, logger)
        if data is None: raise Exception

        policy = helpers_binance.binance_get_coinpair_policy(client, args.coinpair, logger)
        if policy is None: raise Exception

        data = helpers.calculate_overhead(data, args.coinpair, logger)
        if data is None: raise Exception

        if args.reset:
            result = helpers_db.db_delete_coinpair_table(db, db_cursor, args.coinpair, logger)
            if result is None: raise Exception
            result = helpers_db.db_create_coinpair_table(db, db_cursor, args.coinpair, logger)
            if result is None: raise Exception
            result = helpers_db.db_delete_coinpair_policy(db, db_cursor, args.coinpair, logger)
            if result is None: raise Exception

            data_old = None
        else:
            data_old = helpers_db.db_get_coinpair(db_cursor, args.coinpair, logger)
            if data_old is None: raise Exception

        result = helpers_db.db_insert_coinpair_policy(db, db_cursor, coinpair, policy, logger)
        if result is None: raise Exception

        logger.info('Inserting \'' + args.coinpair + '\' into the DB...')
        for index in data.index:
            sys.stdout.write('\r')
            sys.stdout.write('\tProgress... %d%%' % (math.ceil(index / (len(data.index) - 1) * 100)))
            sys.stdout.flush()

            if data_old is not None and len(data_old[data_old['OPEN_TIME'] == data.at[index, 'OPEN_TIME']]) != 0: continue

            try:
                db_cursor.execute("INSERT INTO " + args.coinpair + " VALUES (" + str(data.at[index, 'OPEN_TIME']) + ", " + str(data.at[index, 'OPEN']) + ", " + str(data.at[index, 'HIGH']) + ", " +
                                  str(data.at[index, 'LOW']) + ", " + str(data.at[index, 'CLOSE']) + ", " + str(data.at[index, 'VOLUME']) + ", " + str(data.at[index, 'CLOSE_TIME']) + ", " +
                                  str(data.at[index, 'QUOTE_ASSET_VOLUME']) + ", " + str(data.at[index, 'NUMBER_TRADES']) + ", " + str(data.at[index, 'TAKER_BASE_ASSET_VOLUME']) + ", " +
                                  str(data.at[index, 'TAKER_QUOTE_ASSET_VOLUME']) + ", " + str(data.at[index, 'IGNORE']) + ", " + str(data.at[index, 'MACD']) + ", " +
                                  str(data.at[index, 'MACD_SIGNAL']) + ", " + str(data.at[index, 'MACD_DIFF']) + ", " + str(data.at[index, 'UPPERBAND']) + ", " + str(data.at[index, 'LOWERBAND']) +
                                  ") ON CONFLICT DO NOTHING;")
                db.commit()
            except:
                logger.error('Failed to Insert \'' + args.coinpair + '\' into the DB')
                logger.error('\n' + traceback.print_exc())
                raise Exception

        sys.stdout.write('\n')
    except:
        logger.error('Failed to Add Coinpair \'' + args.coinpair + '\' into the DB')
        error = True

    helpers_db.db_disconnect(db, logger)

    if error: sys.exit(1)
    sys.exit(0)
