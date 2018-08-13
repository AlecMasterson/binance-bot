import psycopg2, pandas, sys, os, traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def db_connect(logger):
    try:
        logger.info('Connecting to the DB...')
        db = psycopg2.connect(database=utilities.DB_NAME, user=utilities.DB_USER, password=utilities.DB_PASS, host=utilities.DB_HOST, port=utilities.DB_PORT)
        return db, db.cursor()
    except:
        logger.error('Failed to Connect to the DB')
        logger.error('\n' + traceback.print_exc())
        return None, None


def db_disconnect(db, logger):
    try:
        logger.info('Closing Connection to the DB...')
        db.close()
    except:
        logger.error('Failed to Close Connection to the DB')
        logger.error('\n' + traceback.print_exc())
        return None


def db_get_coinpair(db_cursor, coinpair, logger):
    try:
        logger.info('Downloading \'' + coinpair + '\' Historical Data from the DB...')
        db_cursor.execute("SELECT * FROM " + coinpair + ";")
        return pandas.DataFrame(db_cursor.fetchall(), columns=utilities.HISTORY_STRUCTURE)
    except:
        logger.error('Failed to Download \'' + coinpair + '\' Historical Data from the DB')
        logger.error('\n' + traceback.print_exc())
        return None


def db_get_policies(db_cursor, logger):
    try:
        logger.info('Downloading Trading Policies from the DB...')
        db_cursor.execute("SELECT * FROM POLICIES;")
        return pandas.DataFrame(db_cursor.fetchall(), columns=utilities.POLICY_STRUCTURE)
    except:
        logger.error('Failed to Download Trading Policies from the DB')
        logger.error('\n' + traceback.print_exc())
        return None


def db_create_coinpair_table(db, db_cursor, coinpair, logger):
    try:
        logger.info('Creating Coinpair \'' + coinpair + '\' Table in the DB...')
        db_cursor.execute(
            "CREATE TABLE " + coinpair +
            " (OPEN_TIME BIGINT PRIMARY KEY NOT NULL, OPEN REAL NOT NULL, HIGH REAL NOT NULL, LOW REAL NOT NULL, CLOSE REAL NOT NULL, VOLUME REAL NOT NULL, CLOSE_TIME BIGINT NOT NULL, QUOTE_ASSET_VOLUME REAL NOT NULL, NUMBER_TRADES REAL NOT NULL, TAKER_BASE_ASSET_VOLUME REAL NOT NULL, TAKER_QUOTE_ASSET_VOLUME REAL NOT NULL, IGNORE REAL NOT NULL, MACD REAL NOT NULL, MACD_SIGNAL REAL NOT NULL, MACD_DIFF REAL NOT NULL, UPPERBAND REAL NOT NULL, LOWERBAND REAL NOT NULL);"
        )
        db.commit()
        return True
    except:
        logger.error('Failed to Create Coinpair \'' + coinpair + '\' Table in the DB')
        logger.error('\n' + traceback.print_exc())
        return None


def db_insert_coinpair_policy(db, db_cursor, coinpair, policy, logger):
    try:
        logger.info('Inserting \'' + coinpair + '\' Trading Policy into the DB...')
        db_cursor.execute("INSERT INTO POLICIES VALUES (\'" + coinpair + "\', \'" + str(','.join(policy['orderTypes'])) + "\', " + str(policy['baseAssetPrecision']) + ", " +
                          str(policy['filters'][0]['minPrice']) + ", " + str(policy['filters'][0]['maxPrice']) + ", " + str(policy['filters'][0]['tickSize']) + ", " +
                          str(policy['filters'][1]['minQty']) + ", " + str(policy['filters'][1]['maxQty']) + ", " + str(policy['filters'][1]['stepSize']) + ", " +
                          str(policy['filters'][2]['minNotional']) + ") ON CONFLICT DO NOTHING;")
        db.commit()
        return True
    except:
        logger.error('Failed to Insert \'' + coinpair + '\' Trading Policy into the DB')
        logger.error('\n' + traceback.print_exc())
        return None


def db_insert_asset_balance(db, db_cursor, asset, free, logger):
    try:
        logger.info('Inserting \'' + asset + '\' Balance into the DB...')
        db_cursor.execute("INSERT INTO BALANCES VALUES ('" + asset + "', " + str(free) + ") ON CONFLICT (ASSET) DO UPDATE SET FREE = Excluded.FREE;")
        db.commit()
        return True
    except:
        logger.error('Failed to Insert \'' + asset + '\' Balance into the DB')
        logger.error('\n' + traceback.print_exc())
        return None


def db_delete_coinpair_table(db, db_cursor, coinpair, logger):
    try:
        logger.info('Deleting \'' + coinpair + '\' Historical Data from the DB...')
        db_cursor.execute("DROP TABLE IF EXISTS " + coinpair + ";")
        db.commit()
        return True
    except:
        logger.error('Failed to Delete \'' + coinpair + '\' Historical Data from the DB')
        logger.error('\n' + traceback.print_exc())
        return None


def db_delete_coinpair_policy(db, db_cursor, coinpair, logger):
    try:
        logger.info('Deleting \'' + coinpair + '\' Trading Policy from the DB...')
        db_cursor.execute("DELETE FROM POLICIES WHERE COINPAIR = \'" + coinpair + "\';")
        db.commit()
        return True
    except:
        logger.error('Failed to Delete \'' + coinpair + '\' Trading Policy from the DB')
        logger.error('\n' + traceback.print_exc())
        return None
