import utilities, helpers, pandas
from sqlalchemy import create_engine


def connect():
    return create_engine('mysql://' + utilities.DB_USER + ':' + utilities.DB_PASS + '@' + utilities.DB_HOST + ':' + utilities.DB_PORT + '/' + utilities.DB_NAME)


''' GET '''


def get_historical_data(db, coinpair):
    return pandas.read_sql_table(con=db, table_name=coinpair, columns=utilities.HISTORY_STRUCTURE)


def get_asset_balances(db):
    return pandas.read_sql_table(con=db, table_name='BALANCES', columns=utilities.BALANCES_STRUCTURE)


def get_bot_actions(db):
    return pandas.read_sql_table(con=db, table_name='ACTIONS', columns=utilities.ACTIONS_STRUCTURE)


''' CREATE '''


def create_historical_data_table(db, coinpair, data):
    data.to_sql(con=db, name=coinpair, index=False, if_exists='replace')
    return True


def create_asset_balances_table(db, data):
    data.to_sql(con=db, name='BALANCES', index=False, if_exists='replace')
    return True


def create_bot_actions_table(db, data):
    data.to_sql(con=db, name='ACTIONS', index=False, if_exists='replace')
    return True


def create_logs_table(db, data):
    data.to_sql(con=db, name='LOGS', index=False, if_exists='replace')
    return True


''' SAFE '''


def safe_connect(logger):
    return helpers.bullet_proof(logger, 'Connecting to the DB', lambda: connect())


def safe_get_historical_data(logger, db, coinpair):
    return helpers.bullet_proof(logger, 'Downloading \'' + coinpair + '\' Historical Data from the DB', lambda: get_historical_data(db, coinpair))


def safe_get_asset_balances(logger, db):
    return helpers.bullet_proof(logger, 'Downloading Asset Balances from the DB', lambda: get_asset_balances(db))


def safe_get_bot_actions(logger, db):
    return helpers.bullet_proof(logger, 'Downloading Bot Actions from the DB', lambda: get_bot_actions(db))


def safe_create_historical_data_table(logger, db, coinpair, data):
    return helpers.bullet_proof(logger, 'Creating \'' + coinpair + '\' Historical Data Table in the DB', lambda: create_historical_data_table(db, coinpair, data))


def safe_create_asset_balances_table(logger, db, data):
    return helpers.bullet_proof(logger, 'Creating Asset Balances Table in the DB', lambda: create_asset_balances_table(db, data))


def safe_create_bot_actions_table(logger, db, data):
    return helpers.bullet_proof(logger, 'Creating Bot Actions Table in the DB', lambda: create_bot_actions_table(db, data))


def safe_create_logs_table(logger, db, data):
    return helpers.bullet_proof(logger, 'Creating Logs Table in the DB', lambda: create_logs_table(db, data))
