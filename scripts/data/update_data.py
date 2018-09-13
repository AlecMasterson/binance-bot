import sys, os, argparse, time, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_data')


def test_connection(client):
    if client.get_system_status()['status'] == 1: return False
    return True


def update_assets(client, db):
    balances = pandas.DataFrame(columns=utilities.BALANCE_STRUCTURE)
    for coinpair in utilities.COINPAIRS:
        balance = helpers_binance.safe_get_asset_balance(logger, client, coinpair[:-3])
        if balance is None: return None
        balances = balances.append({'ASSET': coinpair[:-3], 'FREE': balance}, ignore_index=True)
    return helpers_db.safe_create_asset_balances_table(logger, db, balances)


def update_trading_policies(client, db):
    policies = pandas.DataFrame(columns=utilities.POLICY_STRUCTURE)
    for coinpair in utilities.COINPAIRS:
        policy = helpers_binance.safe_get_trading_policy(logger, client, coinpair)
        if policy is None: return None
        policies = policies.append(
            {
                'COINPAIR': coinpair,
                'TYPES': str(','.join(policy['orderTypes'])),
                'BASE_PRECISION': policy['baseAssetPrecision'],
                'MIN_PRICE': policy['filters'][0]['minPrice'],
                'MAX_PRICE': policy['filters'][0]['maxPrice'],
                'PRICE_SIZE': policy['filters'][0]['tickSize'],
                'MIN_QTY': policy['filters'][1]['minQty'],
                'MAX_QTY': policy['filters'][1]['maxQty'],
                'QTY_SIZE': policy['filters'][1]['stepSize'],
                'MIN_NOTIONAL': policy['filters'][2]['minNotional']
            },
            ignore_index=True)

    return helpers_db.safe_create_trading_policies_table(logger, db, policies)


def update_history(client, db):
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


def fun(client, db):
    most_recent_update = {'assets': None, 'trading_policies': None, 'history': None}

    connection_status = True
    while connection_status:
        current_time = int(round(time.time() * 1000))

        if most_recent_update['assets'] is None or current_time - most_recent_update['assets'] > 60000:
            result = update_assets(client, db)
            if result: most_recent_update['assets'] = int(round(time.time() * 1000))
            # TODO: Else handle errors...

        if most_recent_update['trading_policies'] is None or current_time - most_recent_update['trading_policies'] > 60000:
            result = update_trading_policies(client, db)
            if result: most_recent_update['trading_policies'] = int(round(time.time() * 1000))
            # TODO: Else handle errors...

        if most_recent_update['history'] is None or current_time - most_recent_update['history'] > 60000:
            result = update_history(client, db)
            if result: most_recent_update['history'] = int(round(time.time() * 1000))
            # TODO: Else handle errors...

        time.sleep(10)

        connection_status = test_connection(client)

    return 1 if not connection_status else 2


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating Data in the DB').parse_args()

    client = helpers_binance.safe_connect(logger)
    db = helpers_db.safe_connect(logger)
    if client is None or db is None: sys.exit(1)

    exit_status = helpers.bullet_proof(logger, 'Updating Data in the DB', lambda: fun(client, db))

    logger.error('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)
