import sys, os, argparse, time
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_data')


def update_history(client, db):
    for coinpair in utilities.COINPAIRS:
        data = helpers_binance.safe_get_recent_data(logger, client, coinpair)
        if data is None: return False

        saved_data = helpers_db.safe_get_historical_data(logger, db, coinpair)
        if saved_data is None: return False

        count = 0
        for index, row in data.iterrows():
            if not (saved_data['OPEN_TIME'] == row['OPEN_TIME']).any():
                saved_data = saved_data.append(row, ignore_index=True)
                count += 1
        logger.info('Added ' + str(count) + ' New Rows')

        if count == 0: return True

        saved_data = helpers.safe_calculate_overhead(logger, coinpair, saved_data)
        if saved_data is None: return False

        if helpers_db.safe_create_historical_data_table(logger, db, coinpair, saved_data) is None: return False

    return True


def fun(client, db):
    most_recent_update = {'history': None}

    connection_status = True
    while connection_status:
        current_time = int(round(time.time() * 1000))

        if most_recent_update['history'] is None or current_time - most_recent_update['history'] > 60000:
            if update_history(client, db): most_recent_update['history'] = current_time
            else: break

        logger.info('Sleeping Script for 30 Seconds...')
        time.sleep(30)
        connection_status = helpers_binance.safe_test_connection(logger, client)

    if not connection_status: logger.error('Lost Connection to the Binance API')
    return 2 if not connection_status else 1


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating Data in the DB').parse_args()

    client = helpers_binance.safe_connect(logger)
    if client is None: sys.exit(1)
    db = helpers_db.safe_connect(logger)
    if db is None: sys.exit(1)

    exit_status = helpers.bullet_proof(logger, 'Updating Data in the DB', lambda: fun(client, db))

    if exit_status != 0: logger.error('Closing Script with Exit Status ' + str(exit_status))
    else: logger.info('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)
