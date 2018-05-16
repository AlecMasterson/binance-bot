from binance.client import Client
import sys, logging

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
ACTIVE_DIR = DIRS_INTERVALS[1]

COINPAIRS = ['BNBBTC', 'CMTBTC', 'EOSBTC', 'ETHBTC', 'GTOBTC', 'ICNBTC', 'ICXBTC', 'INSBTC', 'NAVBTC', 'OMGBTC', 'REQBTC', 'SNMBTC', 'WTCBTC', 'XLMBTC']
ASSETS = ['BNB', 'BTC', 'CMT', 'EOS', 'ETH', 'GTO', 'ICN', 'ICX', 'INS', 'NAV', 'OMG', 'REQ', 'SNM', 'WTC', 'XLM']

COLUMN_STRUCTURE = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number Trades', 'Taker Base Asset Volume', 'Take Quote Asset Volume', 'Ignore']
POSITION_STRUCTURE = ['buy_id', 'sell_id', 'open', 'time', 'age', 'pair', 'amount', 'price', 'current', 'fee', 'result', 'peak', 'stop-loss']


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
