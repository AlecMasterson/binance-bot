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
[12, 1.056, 0.009, 0.95]
ORDER_TIME_LIMIT = 12        # [1, 12] Integers = 12
STOP_LOSS_ARM = 1.03        # [1.010, 1.050] 3 Decimal Places = 40
STOP_LOSS = 0.005        # [0.001, 0.010] 3 Decimal Places = 10
DROP = 0.960        # [0.950, 0.980] 3 Decimal Places = 30
# 12 * 40 * 10 * 30 = 144,000

ONE = 0.8
ONE_Y = 1
TWO = 0.4
TWO_Y = 1
THREE = 0.005
THREE_Y = 1

NUM_TRIGGERS = 4
TRIGGER_DECAY = 0.22
TRIGGER_THRESHOLD = 1.5
TRIGGER_0 = 10
TRIGGER_1 = 4
TRIGGER_2 = 0.32
TRIGGER_3 = 0.16


def set_optimized(otl, sla, sl, dp):
    global ORDER_TIME_LIMIT
    ORDER_TIME_LIMIT = otl
    global STOP_LOSS_ARM
    STOP_LOSS_ARM = sla
    global STOP_LOSS
    STOP_LOSS = sl
    global DROP
    DROP = dp


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
