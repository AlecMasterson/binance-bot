import sys, os, helpers, psycopg2, pandas

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities
''' CONNECTING TO DB '''


def db_connect():
    db = psycopg2.connect(database=utilities.DB_NAME, user=utilities.DB_USER, password=utilities.DB_PASS, host=utilities.DB_HOST, port=utilities.DB_PORT)
    return [db, db.cursor()]


def safe_connect(logger):
    message = 'Connecting to the DB'
    return helpers.bullet_proof(logger, message, lambda: db_connect())


''' DISCONNECTING FROM DB '''


def db_disconnect(db):
    db.close()
    return True


def safe_disconnect(logger, db):
    message = 'Disconnecting from the DB'
    return helpers.bullet_proof(logger, message, lambda: db_disconnect(db))


''' GET HISTORICAL DATA '''


def db_get_historical_data(db_cursor, coinpair):
    db_cursor.execute('SELECT * FROM ' + coinpair + ';')
    return pandas.DataFrame(db_cursor.fetchall(), columns=utilities.HISTORY_STRUCTURE)


def safe_get_historical_data(logger, db_cursor, coinpair):
    message = 'Downloading \'' + coinpair + '\' Historical Data from the DB'
    return helpers.bullet_proof(logger, message, lambda: db_get_historical_data(db_cursor, coinpair))


''' GET ALL TRADING POLICIES '''


def db_get_trading_policies(db_cursor):
    db_cursor.execute('SELECT * FROM POLICIES;')
    return pandas.DataFrame(db_cursor.fetchall(), columns=utilities.POLICY_STRUCTURE)


def safe_get_trading_policies(logger, db_cursor):
    message = 'Downloading Trading Policies from the DB'
    return helpers.bullet_proof(logger, message, lambda: db_get_trading_policies(db_cursor))


''' CREATE HISTORICAL DATA TABLE '''


def db_create_historical_data_table(db, db_cursor, coinpair):
    db_cursor.execute(
        "CREATE TABLE " + coinpair +
        " (OPEN_TIME BIGINT PRIMARY KEY NOT NULL, OPEN REAL NOT NULL, HIGH REAL NOT NULL, LOW REAL NOT NULL, CLOSE REAL NOT NULL, VOLUME REAL NOT NULL, CLOSE_TIME BIGINT NOT NULL, QUOTE_ASSET_VOLUME REAL NOT NULL, NUMBER_TRADES REAL NOT NULL, TAKER_BASE_ASSET_VOLUME REAL NOT NULL, TAKER_QUOTE_ASSET_VOLUME REAL NOT NULL, IGNORE REAL NOT NULL, MACD REAL NOT NULL, MACD_SIGNAL REAL NOT NULL, MACD_DIFF REAL NOT NULL, UPPERBAND REAL NOT NULL, LOWERBAND REAL NOT NULL);"
    )
    db.commit()
    return True


def safe_create_historical_data_table(logger, db, db_cursor, coinpair):
    message = 'Creating Coinpair \'' + coinpair + '\' Historical Data Table in the DB'
    return helpers.bullet_proof(logger, message, lambda: db_create_historical_data_table(db, db_cursor, coinpair))


''' DROP HISTORICAL DATA TABLE '''


def db_drop_historical_data_table(db, db_cursor, coinpair):
    db_cursor.execute('DROP TABLE IF EXISTS ' + coinpair + ';')
    db.commit()
    return True


def safe_drop_historical_data_table(logger, db, db_cursor, coinpair):
    message = 'Dropping \'' + coinpair + '\' Table from the DB'
    return helpers.bullet_proof(logger, message, lambda: db_drop_historical_data_table(db, db_cursor, coinpair))


''' INSERT COINPAIR TRADING POLICY '''


def db_insert_trading_policy(db, db_cursor, coinpair, policy):
    db_cursor.execute("INSERT INTO POLICIES VALUES (\'" + coinpair + "\', \'" + str(','.join(policy['orderTypes'])) + "\', " + str(policy['baseAssetPrecision']) + ", " +
                      str(policy['filters'][0]['minPrice']) + ", " + str(policy['filters'][0]['maxPrice']) + ", " + str(policy['filters'][0]['tickSize']) + ", " + str(policy['filters'][1]['minQty']) +
                      ", " + str(policy['filters'][1]['maxQty']) + ", " + str(policy['filters'][1]['stepSize']) + ", " + str(policy['filters'][2]['minNotional']) + ") ON CONFLICT DO NOTHING;")
    db.commit()
    return True


def safe_insert_trading_policy(logger, db, db_cursor, coinpair, policy):
    message = 'Inserting \'' + coinpair + '\' Trading Policy into the DB'
    return helpers.bullet_proof(logger, message, lambda: db_insert_trading_policy(db, db_cursor, coinpair, policy))


''' DELETE COINPAIR TRADING POLICY '''


def db_delete_trading_policy(db, db_cursor, coinpair):
    db_cursor.execute('DELETE FROM POLICIES WHERE COINPAIR = \'' + coinpair + '\';')
    db.commit()
    return True


def safe_delete_trading_policy(logger, db, db_cursor, coinpair):
    message = 'Deleting \'' + coinpair + '\' Trading Policy from the DB'
    return helpers.bullet_proof(logger, message, lambda: db_delete_trading_policy(db, db_cursor, coinpair))


''' INSERT ASSET BALANCE '''


def db_insert_asset_balance(db, db_cursor, asset, free):
    db_cursor.execute("INSERT INTO BALANCES VALUES ('" + asset + "', " + str(free) + ") ON CONFLICT (ASSET) DO UPDATE SET FREE = Excluded.FREE;")
    db.commit()
    return True


def safe_insert_asset_balance(logger, db, db_cursor, asset, free):
    message = 'Inserting \'' + asset + '\' Balance into the DB'
    return helpers.bullet_proof(logger, message, lambda: db_insert_asset_balance(db, db_cursor, asset, free))
