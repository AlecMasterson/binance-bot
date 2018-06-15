import logging
import sys

from binance.client import Client

DIRS = ['data_15_min/', 'data_30_min/', 'data_1_hour/', 'data_2_hour/']
INTERVALS = [Client.KLINE_INTERVAL_15MINUTE, Client.KLINE_INTERVAL_30MINUTE, Client.KLINE_INTERVAL_1HOUR, Client.KLINE_INTERVAL_2HOUR]
DIRS_INTERVALS = [{
    'dir': 'data_5_min/',
    'api': Client.KLINE_INTERVAL_5MINUTE
}, {
    'dir': 'data_15_min/',
    'api': Client.KLINE_INTERVAL_15MINUTE
}, {
    'dir': 'data_30_min/',
    'api': Client.KLINE_INTERVAL_30MINUTE
}, {
    'dir': 'data_1_hour/',
    'api': Client.KLINE_INTERVAL_1HOUR
}, {
    'dir': 'data_2_hour/',
    'api': Client.KLINE_INTERVAL_2HOUR
}]

COINPAIRS = ['BNBBTC']
COLUMN_STRUCTURE = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number Trades', 'Taker Base Asset Volume', 'Take Quote Asset Volume', 'Ignore']

PUBLIC_KEY = ''
SECRET_KEY = ''

START_DATE = 1527829200000        # The starting date, in milliseconds, that we begin backtesting from.
TIME_INTERVAL = Client.KLINE_INTERVAL_5MINUTE        # The base interval for our data.
CANDLE_INTERVAL = 300000        # The TIME_INTERVAL, in milliseconds, for each candlestick.

ORDER_TIME_LIMIT = 5        # [1, 12] Integers = 12
STOP_LOSS_ARM = 1.03        # [1.010, 1.050] 3 Decimal Places = 40
STOP_LOSS = 0.005        # [0.001, 0.010] 3 Decimal Places = 10
DROP = 0.960        # [0.950, 0.980] 3 Decimal Places = 30
# 12 * 40 * 10 * 30 = 144,000

#[11, 8.8, 4.4]
#[5, 7.0, 4.0]
#[10, 7.1, 4.1]

#12, 7.0, 3.9
#11, 7.1, 2.9
TOP_THRESHOLD = 2.7
BOTTOM_THRESHOLD = 2.9
#{'genes': [5, 239, 216, 0.95, 0.57], 'fitness': 1.6762378136700034} [('ADABTC', 1.6762378136700034)]
#11, 95, 180, 0.18, 0.82
#5, 166, 179, 0.59, 0.9
# [5, 150, 180, 0.67, 0.9]
WINDOW = 139
TOP_WINDOW = 173
PERCENT = 0.67
TOP_PERCENT = 0.93

NUM_TRIGGERS = 4
TRIGGER_DECAY = 0.22
TRIGGER_THRESHOLD = 1.5
TRIGGER_0 = 10
TRIGGER_1 = 4
TRIGGER_2 = 0.32
TRIGGER_3 = 0.16


def set_optimized(otl, w, tw, p, tp):
    global ORDER_TIME_LIMIT
    ORDER_TIME_LIMIT = otl
    global WINDOW
    WINDOW = w
    global TOP_WINDOW
    TOP_WINDOW = tw
    global PERCENT
    PERCENT = p
    global TOP_PERCENT
    TOP_PERCENT = tp


# Setup the logging interface with the correct formatting and log file
def set_logger():
    logger = logging.getLogger('binance-bot')

    # Output to the specific log file.
    handler = logging.FileHandler('logs/bot.log')

    # Create the default formatting for the logger and add the new handler.
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # We will only use ERROR and INFO level logs.
    logger.setLevel(logging.ERROR)
    logger.setLevel(logging.INFO)


# Return the logging interface
def get_logger():
    # Be sure the logger is set before returning it.
    logger = logging.getLogger('binance-bot')
    if len(logger.handlers) == 0: set_logger()

    return logging.getLogger('binance-bot')


# Print an error message and exit the script
# message - The unique error message
# terminate - True if the error should stop the script
def throw_error(message, terminate):
    print('ERROR: ' + message)
    get_logger().error(message)
    if terminate: sys.exit()


# Print an info message
# message - The unique info message
def throw_info(message):
    print('INFO: ' + message)
    get_logger().info(message)
