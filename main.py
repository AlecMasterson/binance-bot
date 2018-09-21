import sys, os, argparse, time
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('main')


def fun(client, db):
    actions = helpers_db.safe_get_bot_actions(logger, db)
    if actions is None: return 1

    for coinpair in utilities.COINPAIRS:
        logger.info('Analyzing Most Recent \'' + coinpair + '\' Action')

        coinpair_actions = actions[actions['COINPAIR'] == coinpair]
        if len(coinpair_actions) > 0: action = coinpair_actions.iloc[len(coinpair_actions) - 1]
        else: continue

        if int(round(time.time() * 1000)) - action['TIME'] > utilities.ACTION_RECENT:
            logger.warn('Most Recent \'' + coinpair + '\' Action Not Recent Enough')
            continue

        if action['ACTION'] != 'HOLD':

            asset = coinpair[-3:] if action['ACTION'] == 'BUY' else coinpair[:-3]

            trading_policy = helpers_binance.safe_get_trading_policy(logger, client, coinpair)
            if trading_policy is None: continue

            balance = helpers_binance.safe_get_asset_balance(logger, client, asset)
            if balance is None: continue

            quantity, price = helpers.validate_order(trading_policy, action['ACTION'], float(balance), float(action['PRICE']))
            if quantity != -1 and price != -1: helpers_binance.safe_create_order(logger, client, coinpair, action['ACTION'], quantity, price)
            else: logger.warn('Failed to Create Valid Order with Current Balance')

    return 0


if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for the Binance Bot').parse_args()

    client = helpers_binance.safe_connect(logger)
    if client is None: sys.exit(1)
    db = helpers_db.safe_connect(logger)
    if db is None: sys.exit(1)

    exit_status = helpers.bullet_proof(logger, 'Main Script', lambda: fun(client, db))

    if exit_status != 0: logger.error('Closing Script with Exit Status ' + str(exit_status))
    else: logger.info('Closing Script with Exit Status ' + str(exit_status))
    sys.exit(exit_status)
