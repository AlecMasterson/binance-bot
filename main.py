import utilities, argparse, sys, time
from scripts import helpers, helpers_binance, helpers_db

logger = helpers.create_logger('main')


def fun():
	client = helpers_binance.safe_connect(logger)
	if client is None: return None
    db = helpers_db.safe_connect(logger)
	if db is None: return None

    actions = db.safe_get_bot_actions(logger, db)
	if actions is None: return None

	for coinpair in utilities.COINPAIRS:
		logger.info('Analyzing Most Recent \'' + coinpair + '\' Action')

		coinpair_actions = actions[actions['COINPAIR'] == coinpair]
		action = coinpair_actions.iloc[len(coinpair_actions)-1] if len(coinpair_actions) > 0 else continue

		if int(round(time.time() * 1000)) - action['TIME'] > utilities.ACTION_RECENT:
			logger.warn('Most Recent \'' + coinpair + '\' Action Not Recent Enough')
			continue

		trading_policy = helpers_binance.safe_get_trading_policy(client, coinpair)
		if trading_policy is None: continue

		if action['ACTION'] != 'HOLD':
			# TODO: Determine what asset balance it wants for 'BUY' vs 'SELL'.
			balance = helpers_binance.safe_get_asset_balance(client, coinpair[:-3] if action['ACTION'] == 'BUY' else coinpair[-3:])
			if balance is None: continue

			quantity, price = helpers.validate_order(trading_policy, action['ACTION'], balance, action['PRICE'])
			if quantity != -1 and price != -1:
				helpers_binance.safe_create_order(client, coinpair, action['ACTION'], quantity, price)

    return True


if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for the Binance Bot').parse_args()

    if helpers.bullet_proof(logger, 'Main Script', lambda: fun()) is None: sys.exit(1)
    else: sys.exit(0)
