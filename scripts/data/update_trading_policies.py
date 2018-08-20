import sys, os, argparse, pandas
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('update_policies')


def fun():
    client = helpers_binance.safe_connect(logger)
    if client is None: return None
    db = helpers_db.safe_connect(logger)
    if db is None: return None

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

    if helpers_db.safe_create_trading_policies_table(logger, db, policies) is None: return None

    return True


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating Trading Policies in the DB').parse_args()

    message = 'Updating Trading Policies in the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun())
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
