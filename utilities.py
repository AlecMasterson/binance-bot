import sys, pandas
from binance.client import Client

#COINPAIRS = ['BNBBTC', 'ADABTC', 'IOSTBTC', 'ETHBTC', 'ICXBTC', 'EOSBTC', 'TRXBTC', 'ETCBTC', 'ENGBTC', 'FUELBTC']
COINPAIRS = ['BNBBTC', 'ADABTC']
HISTORY_STRUCTURE = [
    'OPEN_TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'CLOSE_TIME', 'QUOTE_ASSET_VOLUME', 'NUMBER_TRADES', 'TAKER_BASE_ASSET_VOLUME', 'TAKER_QUOTE_ASSET_VOLUME', 'IGNORE', 'MACD', 'MACD_SIGNAL',
    'MACD_DIFF', 'UPPERBAND', 'LOWERBAND'
]
POLICY_STRUCTURE = ['COINPAIR', 'TYPES', 'BASE_PRECISION', 'MIN_PRICE', 'MAX_PRICE', 'PRICE_SIZE', 'MIN_QTY', 'MAX_QTY', 'QTY_SIZE', 'MIN_NOTIONAL']

PUBLIC_KEY = 'T3b7BCBqpPwxWT7vFpQzBP6IQ5qrLkY2pOAaBG3H0sXeLmYzLfx2hLNVpELTlvoK'
SECRET_KEY = 'ouJooSDGjuhR7M8JcfpCXog2yoZs33YYS3zngvDJDtzigfBrNBCKWUMbOP5x02Cx'

DB_NAME = 'test1'
DB_HOST = 'binance-bot-dev.cfypif4yfq4f.us-east-1.rds.amazonaws.com'
DB_PORT = '5434'
DB_USER = 'epsenex'
DB_PASS = 'LaurenTuckSiss#12'

# January 21, 2018 = 1516514400000
# June 1, 2018 = 1527829200000
# June 19, 2018 = 1529384400000
# June 24, 2018 = 1529816400000
TIME_INTERVAL = Client.KLINE_INTERVAL_5MINUTE        # The base interval for our data.
START_DATE = 1516514400000        # The starting date, in milliseconds, that we import our historical data from.
BACKTEST_START_DATE = 1516514400000        # The starting date, in milliseconds, that we begin backtesting from.

ORDER_TIME_LIMIT = 11        # [1, 12] Integers = 12
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
# BNB [5, 139, 173, 0.67, 0.93]
# ADA [5, 223, 203, 0.5, 0.5]
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


def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')
