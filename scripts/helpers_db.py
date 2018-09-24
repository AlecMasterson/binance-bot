import utilities, helpers, pandas
from sqlalchemy import create_engine


def connect():
    return create_engine('mysql://' + utilities.DB_USER + ':' + utilities.DB_PASS + '@' + utilities.DB_HOST + ':' + utilities.DB_PORT + '/' + utilities.DB_NAME)


def get_table(db, name, structure):
    return pandas.read_sql_table(con=db, table_name=name, columns=structure)


def create_table(db, name, data):
    data.to_sql(con=db, name=name, index=False, if_exists='replace')
    return True


def update_order(db, coinpair, orderId, status):
    db.execute('UPDATE ORDERS SET STATUS = \'' + status + '\' WHERE ID = \'' + orderId + '\' AND COINPAIR = \'' + coinpair + '\'')
    return True


''' SAFE '''


def safe_connect(logger):
    return helpers.bullet_proof(logger, 'Connecting to the DB', lambda: connect())


def safe_get_table(logger, db, name, structure):
    return helpers.bullet_proof(logger, 'Downloading ' + name + ' Table from the DB', lambda: get_table(db, name, structure))


def safe_create_table(logger, db, name, data):
    return helpers.bullet_proof(logger, 'Creating ' + name + ' Table in the DB', lambda: create_table(db, name, data))


def safe_update_order(logger, db, coinpair, orderId, status):
    return helpers.bullet_proof(logger, 'Updating Order \'' + str(orderId) + '\' Status to \'' + str(status) + '\'', lambda: update_order(db, coinpair, orderId, status))
