import sys, os, argparse, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_db

logger = helpers.create_logger('create_tables')


def fun(**args):

    if args['extra']['cmd'] == 'all' or args['extra']['cmd'] == 'history':
        df = pandas.DataFrame(columns=utilities.HISTORY_STRUCTURE)

        if args['extra']['cmd'] != 'all' and not args['extra']['coinpair'] is None:
            if helpers_db.safe_create_table(logger, args['db'], args['extra']['coinpair'], df) is None: return 1
        else:
            for coinpair in utilities.COINPAIRS:
                if helpers_db.safe_create_table(logger, args['db'], coinpair, df) is None: return 1

    if args['extra']['cmd'] == 'all' or args['extra']['cmd'] == 'coinpairs':
        df = pandas.DataFrame(colums=utilities.COINPAIRS_STRUCTURE)
        if helpers_db.safe_create_table(logger, args['db'], 'COINPAIRS', df) is None: return 1

    if args['extra']['cmd'] == 'all' or args['extra']['cmd'] == 'balances':
        df = pandas.DataFrame(columns=utilities.BALANCES_STRUCTURE)
        if helpers_db.safe_create_table(logger, args['db'], 'BALANCES', df) is None: return 1

    if args['extra']['cmd'] == 'all' or args['extra']['cmd'] == 'actions':
        df = pandas.DataFrame(columns=utilities.ACTIONS_STRUCTURE)
        if helpers_db.safe_create_table(logger, args['db'], 'ACTIONS', df) is None: return 1

    if args['extra']['cmd'] == 'all' or args['extra']['cmd'] == 'orders':
        df = pandas.DataFrame(columns=utilities.ORDERS_STRUCTURE)
        if helpers_db.safe_create_table(logger, args['db'], 'ORDERS', df) is None: return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Creating Empty Tables in the DB')
    subparsers = parser.add_subparsers(help='The Specific Commands Allowed', dest='cmd')

    parser_history = subparsers.add_parser('history', help='create history tables')
    parser_history.add_argument('-c', '--coinpair', help='a specific history table', type=str, dest='coinpair', required=False)

    parser_coinpairs = subparsers.add_parser('coinpairs', help='create coinpairs table')
    parser_balances = subparsers.add_parser('balances', help='create balances table')
    parser_actions = subparsers.add_parser('actions', help='create actions table')
    parser_orders = subparsers.add_parser('orders', help='create orders table')
    parser_all = subparsers.add_parser('all', help='create all tables')

    args = parser.parse_args()

    if args.cmd is None: sys.exit(1)
    extra = {'cmd': args.cmd}

    if args.cmd == 'history':
        extra['coinpair'] = args.coinpair
        if args.coinpair is None:
            if input('Are you sure you want to erase ALL history from the DB? (y) ') != 'y': sys.exit(1)
            if input('Are you absolutely sure you want to erase ALL history from the DB? (y) ') != 'y': sys.exit(1)
        else:
            if input('Are you sure you want to erase ALL \'' + args.coinpair + '\' history from the DB? (y) ') != 'y': sys.exit(1)

    if args.cmd == 'all':
        if input('Are you sure you want to erase all data from the DB? (y) ') != 'y': sys.exit(1)
        if input('Are you absolutely sure you want to erase ALL data from the DB? (y) ') != 'y': sys.exit(1)

    helpers.main_function(logger, 'Creating \'' + args.cmd + '\' Table(s) in the DB', fun, db=True, extra=extra)
