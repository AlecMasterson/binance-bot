import psycopg2, pandas, sys, os, traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def db_connect(logger):
    try:
        logger.info('Connecting to the DB...')
        db = psycopg2.connect(database=utilities.DB_NAME, user=utilities.DB_USER, password=utilities.DB_PASS, host=utilities.DB_HOST, port=utilities.DB_PORT)
        return db, db.cursor()
    except:
        logger.error('Failed to Connect to the DB. Ending Script...')
        logger.error('\n' + traceback.print_exc())
        return None, None


def db_disconnect(db, logger):
    try:
        logger.info('Closing Connection to the DB...')
        db.close()
    except:
        logger.error('Failed to Close Connection to the DB. Ending Script...')
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


def db_insert_asset_balance(db_cursor, asset, free, logger):
    try:
        logger.info('Inserting \'' + asset + '\' Balance into the DB...')
        db_cursor.execute("INSERT INTO BALANCES VALUES ('" + asset + "', " + str(free) + ") ON CONFLICT (ASSET) DO UPDATE SET FREE = Excluded.FREE;")
        db.commit()
        return True
    except:
        logger.error('Failed to Insert \'' + asset + '\' Balance into the DB')
        logger.error('\n' + traceback.print_exc())
        return None
