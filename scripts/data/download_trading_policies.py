import sys, os, argparse
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import helpers, helpers_db

logger = helpers.create_logger('download_policies')


def fun():
    db = helpers_db.safe_connect(logger)
    if db is None: return None

    policies = helpers_db.safe_get_trading_policies(logger, db)
    if policies is None: return None

    return helpers.safe_to_file(logger, 'data/policies.csv', policies)


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Downloading Trading Policies from the DB').parse_args()

    message = 'Downloading Trading Policies from the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun())
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
