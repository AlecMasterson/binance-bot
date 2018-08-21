import utilities, helpers, pandas, sys, math
from sqlalchemy import create_engine


def connect():
    return create_engine('mysql://' + utilities.DB_USER + ':' + utilities.DB_PASS + '@' + utilities.DB_HOST + ':' + utilities.DB_PORT + '/' + utilities.DB_NAME)


''' GET '''


def get_historical_data(db, coinpair):
    return pandas.read_sql_table(con=db, table_name=coinpair, columns=utilities.HISTORY_STRUCTURE)


def get_trading_policies(db):
    return pandas.read_sql_table(con=db, table_name='POLICIES', columns=utilities.POLICY_STRUCTURE)


def get_asset_balances(db):
    return pandas.read_sql_table(con=db, table_name='BALANCES', columns=utilities.BALANCE_STRUCTURE)


''' CREATE '''


def create_historical_data_table(db, coinpair, data):
    data.to_sql(con=db, name=coinpair, index=False, if_exists='replace')
    return True


def create_trading_policies_table(db, data):
    data.to_sql(con=db, name='POLICIES', index=False, if_exists='replace')
    return True


def create_asset_balances_table(db, data):
    data.to_sql(con=db, name='BALANCES', index=False, if_exists='replace')
    return True


''' INSERT '''


def insert_history_data(db, coinpair, data):
    for index, row in data.iterrows():
        sys.stdout.write('\r')
        sys.stdout.write('\tProgress... %d%%' % (math.ceil(index / (len(data.index) - 1) * 100)))
        sys.stdout.flush()

        q = db.execute('SELECT * FROM ' + coinpair + ' WHERE OPEN_TIME = ' + str(row['OPEN_TIME'])).fetchall()
        if len(q) == 0:
            db.execute('INSERT INTO ' + coinpair + ' VALUES (' + str(row['OPEN_TIME']) + ',' + str(row['OPEN']) + ',' + str(row['HIGH']) + ',' + str(row['LOW']) + ',' + str(row['CLOSE']) + ',' +
                       str(row['VOLUME']) + ',' + str(row['CLOSE_TIME']) + ',' + str(row['QUOTE_ASSET_VOLUME']) + ',' + str(row['NUMBER_TRADES']) + ',' + str(row['TAKER_BASE_ASSET_VOLUME']) + ',' +
                       str(row['TAKER_QUOTE_ASSET_VOLUME']) + ',' + str(row['IGNORE']) + ',' + str(row['MACD']) + ',' + str(row['MACD_SIGNAL']) + ',' + str(row['MACD_DIFF']) + ',' +
                       str(row['UPPERBAND']) + ',' + str(row['LOWERBAND']) + ')')
    return True


''' SAFE '''


def safe_connect(logger):
    return helpers.bullet_proof(logger, 'Connecting to the DB', lambda: connect())


def safe_get_historical_data(logger, db, coinpair):
    return helpers.bullet_proof(logger, 'Downloading \'' + coinpair + '\' Historical Data from the DB', lambda: get_historical_data(db, coinpair))


def safe_get_trading_policies(logger, db):
    return helpers.bullet_proof(logger, 'Downloading Trading Policies from the DB', lambda: get_trading_policies(db))


def safe_get_asset_balances(logger, db):
    return helpers.bullet_proof(logger, 'Downloading Asset Balances from the DB', lambda: get_asset_balances(db))


def safe_create_historical_data_table(logger, db, coinpair, data):
    return helpers.bullet_proof(logger, 'Creating \'' + coinpair + '\' Historical Data Table in the DB', lambda: create_historical_data_table(db, coinpair, data))


def safe_create_trading_policies_table(logger, db, data):
    return helpers.bullet_proof(logger, 'Creating Trading Policies Table in the DB', lambda: create_trading_policies_table(db, data))


def safe_create_asset_balances_table(logger, db, data):
    return helpers.bullet_proof(logger, 'Creating Asset Balances Table in the DB', lambda: create_asset_balances_table(db, data))


def safe_insert_history_data(logger, db, coinpair, data):
    return helpers.bullet_proof(logger, 'Inserting \'' + coinpair + '\' History Data into the DB', lambda: insert_history_data(db, coinpair, data))
