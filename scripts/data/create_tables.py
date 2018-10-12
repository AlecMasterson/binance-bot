import sys, os, argparse, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_db

logger = helpers.create_logger('create_tables')


def fun(**args):

    df = pandas.DataFrame(colums=utilities.COINPAIRS_STRUCTURE)
    if helpers_db.safe_create_table(logger, args['db'], 'COINPAIRS', df) is None: return 1

    df = pandas.DataFrame(columns=utilities.HISTORY_STRUCTURE)
    for coinpair in utilities.COINPAIRS:
        if helpers_db.safe_create_table(logger, args['db'], coinpair, df) is None: return 1

    df = pandas.DataFrame(columns=utilities.BALANCES_STRUCTURE)
    if helpers_db.safe_create_table(logger, args['db'], 'BALANCES', df) is None: return 1

    df = pandas.DataFrame(columns=utilities.ACTIONS_STRUCTURE)
    if helpers_db.safe_create_table(logger, args['db'], 'ACTIONS', df) is None: return 1

    df = pandas.DataFrame(columns=utilities.ORDERS_STRUCTURE)
    if helpers_db.safe_create_table(logger, args['db'], 'ORDERS', df) is None: return 1

    return 0


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Creating Empty Tables in the DB').parse_args()

    if input('Are you sure you want to erase all data from the DB? (y) ') != 'y': sys.exit(1)
    if input('Are you absolutely sure you want to erase ALL data from the DB? (y) ') != 'y': sys.exit(1)

    helpers.main_function(logger, 'Creating Empty Tables in the DB', fun, db=True)
