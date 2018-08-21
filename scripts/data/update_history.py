import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_history')


def fun():
    client = helpers_binance.safe_connect(logger)
    if client is None: return None
    db = helpers_db.safe_connect(logger)
    if db is None: return None

    for coinpair in utilities.COINPAIRS:
        data = helpers_binance.safe_get_recent_data(logger, client, coinpair)
        if data is None: return None

        saved_data = helpers_db.safe_get_historical_data(logger, db, coinpair)
        if saved_data is None: return None

        count = 0
        for index, row in data.iterrows():
            if not (saved_data['OPEN_TIME'] == row['OPEN_TIME']).any():
                saved_data = saved_data.append(row, ignore_index=True)
                count += 1
        logger.info('Added ' + str(count) + ' New Rows')

        if count == 0: return True

        saved_data = helpers.safe_calculate_overhead(logger, coinpair, saved_data)
        if saved_data is None: return None

        if helpers_db.safe_create_historical_data_table(logger, db, coinpair, saved_data) is None: return None

    return True


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating All History in the DB').parse_args()

    message = 'Updating All History in the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun())
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
