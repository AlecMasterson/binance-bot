import sys, os, argparse

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_coinpair')


def fun(coinpair):
    client = helpers_binance.safe_connect(logger)
    if client is None: return None
    db_info = helpers_db.safe_connect(logger)
    if db_info is None: return None

    data = helpers_binance.safe_get_historical_data(logger, client, coinpair)
    if data is None: return None
    policy = helpers_binance.safe_get_trading_policy(logger, client, coinpair)
    if policy is None: return None

    data_old = helpers_db.safe_get_historical_data(logger, db_info[1], coinpair)
    if data_old is None: return None

    logger.info('Inserting \'' + coinpair + '\' into the DB')
    for index in data.index:
        sys.stdout.write('\r')
        sys.stdout.write('\tProgress... %d%%' % (math.ceil(index / (len(data.index) - 1) * 100)))
        sys.stdout.flush()

        if len(data_old[data_old['OPEN_TIME'] == data.at[index, 'OPEN_TIME']]) != 0: continue

        db_info[1].execute("INSERT INTO " + args.coinpair + " VALUES (" + str(data.at[index, 'OPEN_TIME']) + ", " + str(data.at[index, 'OPEN']) + ", " + str(data.at[index, 'HIGH']) + ", " +
                           str(data.at[index, 'LOW']) + ", " + str(data.at[index, 'CLOSE']) + ", " + str(data.at[index, 'VOLUME']) + ", " + str(data.at[index, 'CLOSE_TIME']) + ", " +
                           str(data.at[index, 'QUOTE_ASSET_VOLUME']) + ", " + str(data.at[index, 'NUMBER_TRADES']) + ", " + str(data.at[index, 'TAKER_BASE_ASSET_VOLUME']) + ", " +
                           str(data.at[index, 'TAKER_QUOTE_ASSET_VOLUME']) + ", " + str(data.at[index, 'IGNORE']) + ", " + str(data.at[index, 'MACD']) + ", " + str(data.at[index, 'MACD_SIGNAL']) +
                           ", " + str(data.at[index, 'MACD_DIFF']) + ", " + str(data.at[index, 'UPPERBAND']) + ", " + str(data.at[index, 'LOWERBAND']) + ") ON CONFLICT DO NOTHING;")
        db_info[0].commit()
    sys.stdout.write('\n')

    return helpers_db.safe_disconnect(logger, db_info[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Updating a Coinpair in the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Update', type=str, dest='coinpair', required=True)
    args = parser.parse_args()

    message = 'Updating Coinpair \'' + args.coinpair + '\' in the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun(args.coinpair))
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
