import sys, os, argparse, smtplib
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_db, signals

logger = helpers.create_logger('main_email')


def fun(**args):
    for coinpair in utilities.COINPAIRS:
        data = helpers_db.safe_get_table(logger, args['db'], coinpair, utilities.HISTORY_STRUCTURE)
        if data is None: return 1

        data = data[data['INTERVAL'] == '15m']

        if signals.rsi(data) and signals.lowerband(data):
            logger.info('Sending Email Notification for \'' + coinpair + '\'')

    return 0


if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for Email Notifications for the Binance Bot').parse_args()

    helpers.main_function(logger, 'Main Email Script', fun, db=True)
