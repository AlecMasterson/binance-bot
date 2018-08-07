import logging, psycopg2, sys, os
from binance.client import Client

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    fh = logging.FileHandler('logs/' + name + '.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def binance_connect(logger):
    try:
        logger.info('Connecting to the Binance API...')
        return Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        logger.error('Failed to Connect to the Binance API')
        sys.exit(1)


def db_connect(logger):
    try:
        logger.info('Connecting to the DB...')
        db = psycopg2.connect(database=utilities.DB_NAME, user=utilities.DB_USER, password=utilities.DB_PASS, host=utilities.DB_HOST, port=utilities.DB_PORT)
        return db, db.cursor()
    except:
        logger.error('Failed to Connect to the DB')
        sys.exit(1)


def db_disconnect(db, logger):
    try:
        logger.info('Closing Connection to the DB...')
        db.close()
    except:
        logger.error('Failed to Close Connection to the DB')
        sys.exit(1)


def buy(client, coinpair, price, logger):
    logger.info('BUYING ' + coinpair + ' at Price ' + str(price))


def sell(client, coinpair, price, logger):
    logger.info('SELLING ' + coinpair + ' at Price ' + str(price))
