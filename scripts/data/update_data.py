import sys, os, argparse, time
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_data')


def update_active(db):
    coinpairs = helpers_db.safe_get_table(logger, db, 'COINPAIRS', utilities.COINPAIRS_STRUCTURE)
    if coinpairs is None: return False

    for index, row in coinpairs.iterrows():
        # TODO: The below calculation.
        logger.warn('Need to Include Active Calculation')

    return 0


def update_history(client, db, all, time_interval):
    coinpairs = helpers_db.safe_get_table(logger, db, 'COINPAIRS', utilities.COINPAIRS_STRUCTURE)
    if coinpairs is None: return False

    for index, row in coinpairs.iterrows():
        if not all and not row['ACTIVE']: continue
        coinpair = row['COINPAIR']

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
    if args['extra']['cmd'] == 'active': return update_active(args['db'])
    if args['extra']['cmd'] == 'history': return update_history(args['client'], args['db'], args['extra']['all'], args['extra']['time_interval'])
    if args['extra']['cmd'] == 'orders': return update_orders(args['client'], args['db'])

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Updating Data in the DB')
    subparsers = parser.add_subparsers(help='The Specific Commands Allowed', dest='cmd')

    parser_active = subparsers.add_parser('active', help='update which coinpair\'s are active')

    parser_history = subparsers.add_parser('history', help='update coinpair history')
    parser_history.add_argument('-a', '--all', help='update all coinpairs', action='store_true')
    parser_history.add_argument('-t', '--time', help='the time interval', type=str, dest='time_interval', required=True, choices=utilities.TIME_INTERVALS)

    parser_orders = subparsers.add_parser('orders', help='update open orders')

    args = parser.parse_args()

    if args.cmd is None: sys.exit(1)
    extra = {'cmd': args.cmd}

    if args.cmd == 'active': client = False
    else: client = True

    if args.cmd == 'history':
        extra['all'] = args.all
        extra['time_interval'] = args.time_interval

    helpers.main_function(logger, 'Updating Data in the DB', fun, client=client, db=True, extra=extra)
