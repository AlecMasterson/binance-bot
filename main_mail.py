import sys, os, argparse, smtplib
from email.mime.text import MIMEText
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers, helpers_db, signals

logger = helpers.create_logger('main_email')


def fun(**args):

    potential = []
    for coinpair in utilities.COINPAIRS:
        data = helpers_db.safe_get_table(logger, args['db'], coinpair, utilities.HISTORY_STRUCTURE)
        if data is None: return 1

        data = data[data['INTERVAL'] == '15m']

        if signals.rsi(data) and signals.lowerband(data): potential.append(coinpair)

    if len(potential) > 0:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(utilities.EMAIL_USERNAME, utilities.EMAIL_PASS)

        logger.info('Sending Email Notification for \'' + str(potential) + '\'')
        msg = MIMEText('Potential Buy Orders on: ' + str(potential))
        msg['Subject'] = 'Binance-Bot'
        msg['From'] = utilities.EMAIL_USERNAME
        msg['To'] = utilities.EMAIL_USERNAME

        server.send_message(msg)

        server.quit()

    return 0


if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for Email Notifications for the Binance Bot').parse_args()

    helpers.main_function(logger, 'Main Email Script', fun, db=True)
