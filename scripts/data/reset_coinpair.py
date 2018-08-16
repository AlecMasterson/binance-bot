import sys, os, argparse

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import helpers, helpers_db

logger = helpers.create_logger('reset_coinpair')


def fun(coinpair):
    db_info = helpers_db.safe_connect(logger)
    if db_info is None: return None

    if helpers_db.safe_drop_historical_data_table(logger, db_info[0], db_info[1], coinpair) is None: return None
    if helpers_db.safe_delete_trading_policy(logger, db_info[0], db_info[1], coinpair) is None: return None
    if helpers_db.safe_create_historical_data_table(logger, db_info[0], db_info[1], coinpair) is None: return None

    return helpers_db.safe_disconnect(logger, db_info[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Resetting a Coinpair in the DB')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to Reset', type=str, dest='coinpair', required=True)
    args = parser.parse_args()

    message = 'Resetting Coinpair \'' + args.coinpair + '\' in the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun(args.coinpair))
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message + '\nPlease Update Coinpair \'' + args.coinpair + '\' before Using')
        sys.exit(0)
