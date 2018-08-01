import psycopg2, pandas, sys, os
from binance.client import Client

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def binance_connect():
    try:
        print('INFO: Connecting to the Binance API...')
        return Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        print('ERROR: Failed to Connect to the Binance API')
        sys.exit(1)


def db_connect():
    try:
        print('INFO: Connecting to the DB...')
        db = psycopg2.connect(database=utilities.DB_NAME, user=utilities.DB_USER, password=utilities.DB_PASS, host=utilities.DB_HOST, port=utilities.DB_PORT)
        return db, db.cursor()
    except Exception as e:
        print(e)
        print('ERROR: Failed to Connect to the DB')
        sys.exit(1)


def db_disconnect(db):
    try:
        db.close()
    except:
        print('ERROR: Failed to Close Connection to the DB')
        sys.exit(1)

        sys.exit(1)


def to_csv(file, structure, data):
    try:
        if data is None: data = pandas.DataFrame(columns=structure)
        data.to_csv(file)
        return data
    except:
        print('Failed to Write to File \'' + file + '\'')
        return None


def read_csv(file, structure):
    try:
        return pandas.read_csv(file)
    except FileNotFoundError:
        print('Failed to Find File \'' + file + '\'')
        return to_csv(file, structure, None)
    except:
        print('Failed to Read File \'' + file + '\'')
        return None
