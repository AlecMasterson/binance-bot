import sys, os, argparse, time
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_data')


def update_history(client, db):
    error = False

    for coinpair in utilities.COINPAIRS:
        data = helpers_binance.safe_get_recent_data(logger, client, coinpair)
        if data is None:
            error = True
            continue

        saved_data = helpers_db.safe_get_table(logger, db, coinpair, utilities.HISTORY_STRUCTURE)
        if saved_data is None:
            error = True
            continue

        count = 0
        for index, row in data.iterrows():
            if not (saved_data['OPEN_TIME'] == row['OPEN_TIME']).any():
                saved_data = saved_data.append(row, ignore_index=True)
                count += 1
        logger.info('Added ' + str(count) + ' New Rows')

        if count == 0: continue

        saved_data = helpers.safe_calculate_overhead(logger, coinpair, saved_data)
        if saved_data is None:
            error = True
            continue

        if helpers_db.safe_create_table(logger, db, coinpair, saved_data) is None:
            error = True
            continue

    return False if error else True


def update_orders(client, db):
    error = False

    orders = helpers_db.safe_get_table(logger, db, 'ORDERS', utilities.ORDERS_STRUCTURE)
    if orders is None: return False

    for index, order in orders.iterrows():
        if not order['STATUS'] is 'FILLED' and not order['STATUS'] is 'CANCELED':
            update = helpers_binance.safe_get_order(logger, client, order['COINPAIR'], order['ID'])
            if update is None:
                error = True
                continue
            order['STATUS'] = update['status']

            if not order['STATUS'] is 'FILLED' and int(round(time.time() * 1000)) - order['TIME'] > utilities.ORDER_TIME_LIMIT:
                if helpers_binance.safe_cancel_order(logger, client, order['COINPAIR'], order['ID']) is None:
                    error = True
                    continue

            if helpers_db.safe_update_order(logger, db, coinpair, order['ID'], order['STATUS']) is None:
                error = True
                continue

    return False if error else True


def fun(client, db):
    if not update_history(client, db): return 1
    if not update_orders(client, db): return 1

    return 0


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
