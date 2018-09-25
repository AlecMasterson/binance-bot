import utilities, helpers, pandas
from sqlalchemy import create_engine


def connect():
    return create_engine('mysql://' + utilities.DB_USER + ':' + utilities.DB_PASS + '@' + utilities.DB_HOST + ':' + utilities.DB_PORT + '/' + utilities.DB_NAME)


def get_table(db, name, structure):
    return pandas.read_sql_table(con=db, table_name=name, columns=structure)


def create_table(db, name, data):
    data.to_sql(con=db, name=name, index=False, if_exists='replace')
    return True


def insert_candle(logger, db, coinpair, candle):
    q = db.execute('SELECT * FROM ' + coinpair + ' WHERE OPEN_TIME = \'' candle['OPEN_TIME'] + '\'')
    results = q.fetchall()

    if len(results) == 0:
        db.execute('INSERT INTO ' + coinpair + ' ' + str(tuple(candle.keys())) + ' VALUES ' + str(tuple(candle.values())))
        return True
    else:
        logger.error('One or More Candles Exist in DB for \'' + coinpair + '\' at OPEN_TIME \'' + str(candle['OPEN_TIME']) + '\'')

    return None


def insert_order(logger, db, order):
    q = db.execute('SELECT * FROM ORDERS WHERE COINPAIR = \'' + order['COINPAIR'] + '\' AND ID = \'' + order['ID'] + '\'')
    results = q.fetchall()

    if len(results) == 0:
        db.execute('INSERT INTO ORDERS (COINPAIR, ID, TIME, STATUS) VALUES ' + str(tuple(order.values())))
        return True
    elif len(results) == 1:
        logger.error('Order Already Exists... Updating')
        db.execute('UPDATE ORDERS SET STATUS = \'' + order['STATUS'] + '\' WHERE COINPAIR = \'' + order['COINPAIR'] + '\' AND ID = \'' + order['ID'] + '\'')
        return True
    else:
        logger.error('Multiple Orders in DB with COINPAIR \'' + str(order['COINPAIR']) + '\' and ID \'' + str(order['ID']) + '\'')

    return None


''' SAFE '''


def safe_connect(logger):
    return helpers.bullet_proof(logger, 'Connecting to the DB', lambda: connect())


def safe_get_table(logger, db, name, structure):
    return helpers.bullet_proof(logger, 'Downloading ' + name + ' Table from the DB', lambda: get_table(db, name, structure))


def safe_create_table(logger, db, name, data):
    return helpers.bullet_proof(logger, 'Creating ' + name + ' Table in the DB', lambda: create_table(db, name, data))


def safe_insert_candle(logger, db, coinpair, candle):
    return helpers.bullet_proof(logger, 'Inserting Candle for \'' + coinpair + '\' at OPEN_TIME \'' + str(candle['OPEN_TIME']) + '\' into the DB', lambda: insert_candle(logger, db, coinpair, candle))


def safe_insert_order(logger, db, order):
    return helpers.bullet_proof(logger, 'Inserting Order ' + str(order) + ' into the DB', lambda: insert_order(logger, db, order))
