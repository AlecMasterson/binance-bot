import utilities, argparse, pandas, time
from scripts import helpers, strategy

logger = helpers.create_logger('main')


def get_data(db_cursor):
    try:
        logger.info('Downloading \'BNBBTC\' Historical Data from the DB...')
        db_cursor.execute("SELECT * FROM BNBBTC ORDER BY OPEN_TIME DESC LIMIT " + str(utilities.WINDOW * 2) + ";")
        data = pandas.DataFrame(db_cursor.fetchall()[::-1], columns=utilities.HISTORY_STRUCTURE)
        return data
    except:
        logger.error('Failed to Download \'BNBBTC\' Historical Data from the DB')
        return None


# TODO: Support more than just BNBBTC...
if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for the Binance Bot').parse_args()
    error = False

    client = helpers.binance_connect(logger)
    db, db_cursor = helpers.db_connect(logger)

    logger.info('Starting Infinite Loop... Hold On Tight!')
    while not error:
        data = get_data(db_cursor)

        if data is None: error = True
        else:
            action = strategy.action(data)
            logger.info('Bot Chooses Action: ' + action)

            price = data.at[len(data) - 1, 'CLOSE']
            if action == 'BUY': helpers.buy(client, 'BNBBTC', price, logger)
            if action == 'SELL': helpers.sell(client, 'BNBBTC', price, logger)

            time.sleep(15)

    helpers.db_disconnect(db, logger)
    if error: sys.exit(1)
