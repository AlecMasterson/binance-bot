import sys, os, argparse, pandas, math, traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import helpers, helpers_binance, helpers_db
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import utilities

logger = helpers.create_logger('add_coinpair')

def fun_insert(db_info, data, data_old):
    for index in data.index:
        sys.stdout.write('\r')
        sys.stdout.write('\tProgress... %d%%' % (math.ceil(index / (len(data.index) - 1) * 100)))
        sys.stdout.flush()

        if data_old is not None and len(data_old[data_old['OPEN_TIME'] == data.at[index, 'OPEN_TIME']]) != 0: continue

        db_info[1].execute("INSERT INTO " + args.coinpair + " VALUES (" + str(data.at[index, 'OPEN_TIME']) + ", " + str(data.at[index, 'OPEN']) + ", " + str(data.at[index, 'HIGH']) + ", " +
                          str(data.at[index, 'LOW']) + ", " + str(data.at[index, 'CLOSE']) + ", " + str(data.at[index, 'VOLUME']) + ", " + str(data.at[index, 'CLOSE_TIME']) + ", " +
                          str(data.at[index, 'QUOTE_ASSET_VOLUME']) + ", " + str(data.at[index, 'NUMBER_TRADES']) + ", " + str(data.at[index, 'TAKER_BASE_ASSET_VOLUME']) + ", " +
                          str(data.at[index, 'TAKER_QUOTE_ASSET_VOLUME']) + ", " + str(data.at[index, 'IGNORE']) + ", " + str(data.at[index, 'MACD']) + ", " + str(data.at[index, 'MACD_SIGNAL']) +
                          ", " + str(data.at[index, 'MACD_DIFF']) + ", " + str(data.at[index, 'UPPERBAND']) + ", " + str(data.at[index, 'LOWERBAND']) + ") ON CONFLICT DO NOTHING;")
        db_info[0].commit()
    sys.stdout.write('\n')
    
    return True

def fun(coinpair, reset):
    client = helpers_binance.safe_connect(logger)
    if client is None: raise Exception
    db_info = helpers_db.safe_connect(logger)
    if db_info None: raise Exception

    data = helpers_binance.safe_get_historical_data(logger, client, coinpair)
    if data is None: raise Exception

    policy = helpers_binance.safe_get_trading_policy(logger, client, coinpair)
    if policy is None: raise Exception

    data = helpers.safe_calculate_overhead(logger, coinpair, data)
    if data is None: raise Exception

    if reset:
        if helpers_db.safe_drop_historical_data_table(logger, db_info[0], db_info[1], coinpair) is None: raise Exception
        if helpers_db.safe_create_historical_data_table(logger, db_info[0], db_info[1], coinpair) is None: raise Exception
        if helpers_db.safe_delete_trading_policy(logger, db_info[0], db_info[1], coinpair) is None: raise Exception

        data_old = None
    else:
        data_old = helpers_db.safe_get_historical_data(logger, db_info[1], coinpair)
        if data_old is None: raise Exception

    if helpers_db.safe_insert_trading_policy(logger, db_info[0], db_info[1], coinpair, policy) is None: raise Exception

    if helpers.bullet_proof(logger, 'Inserting \'' + coinpair + '\' into the DB', lambda: fun_insert(db_info, data, data_old)) is None: raise Exception

    return helpers_db.safe_disconnect(logger, db_info[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Adding a Coinpair into the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to add', type=str, dest='coinpair', required=True)
    parser.add_argument('-r', '--reset', help='True if resetting the DB', action='store_true', required=False)
    args = parser.parse_args()

    result = helpers.bullet_proof(logger, 'Adding Coinpair \'' + args.coinpair + '\' into the DB', lambda: fun(args.coinpair, args.reset))
    if result is None: sys.exit(1)
    else: sys.exit(0)
