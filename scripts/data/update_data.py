import sys, os, argparse, time
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_data')


def update_history(client, db, time_interval):
    for coinpair in utilities.COINPAIRS:

        saved_data = helpers_db.safe_get_table(logger, db, coinpair, utilities.HISTORY_STRUCTURE)
        if saved_data is None: return False

        data = helpers_binance.safe_get_recent_data(logger, client, coinpair, time_interval)
        if data is None: return False

        count = 0
        for index, row in data.iterrows():
            if not ((saved_data['INTERVAL'] == row['INTERVAL']) & (saved_data['OPEN_TIME'] == row['OPEN_TIME'])).any():
                saved_data = saved_data.append(row, ignore_index=True)
                count += 1
        logger.info('Adding ' + str(count) + ' New Rows')

        if count == 0: continue

        saved_data = helpers.safe_calculate_overhead(logger, coinpair, saved_data)
        if saved_data is None: return False

        for index, candle in saved_data.tail(count).iterrows():
            if helpers_db.safe_upsert_candle(logger, db, coinpair, candle) is None: return False

    return True


def update_orders(client, db):
    orders = helpers_db.safe_get_table(logger, db, 'ORDERS', utilities.ORDERS_STRUCTURE)
    if orders is None: return False

    for index, order in orders.iterrows():
        if not order['STATUS'] is 'FILLED' and not order['STATUS'] is 'CANCELED':
            update = helpers_binance.safe_get_order(logger, client, order['COINPAIR'], order['ID'])
            if update is None: return False

            order['STATUS'] = update['status']

            if not order['STATUS'] is 'FILLED' and (helpers.current_time() - order['TIME']) > utilities.ORDER_TIME_LIMIT:
                print(int(round(time.time() * 1000)))
                print(order['TIME'])
                if helpers_binance.safe_cancel_order(logger, client, order['COINPAIR'], order['ID']) is None: return False

            if helpers_db.safe_upsert_order(logger, db, order) is None: return False

    return True


def fun(**args):
    if not update_history(args['client'], args['db'], args['extra']['time_interval']): return 1
    #if not update_orders(args['client'], args['db']): return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Updating Data in the DB')
    parser.add_argument('-t', help='the time interval', type=str, dest='time_interval', required=True, choices=utilities.TIME_INTERVALS)
    args = parser.parse_args()

    helpers.main_function(logger, 'Updating Data in the DB', fun, client=True, db=True, extra={'time_interval': args.time_interval})
