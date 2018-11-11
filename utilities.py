from datetime import datetime

COINPAIRS = [
    'HOTBTC', 'NPXSBTC', 'BCNBTC', 'DENTBTC', 'NCASHBTC', 'KEYBTC', 'SCBTC', 'MFTBTC', 'STORMBTC', 'TNBBTC', 'POEBTC', 'IOSTBTC', 'VETBTC', 'PHXBTC', 'IOTXBTC', 'FUNBTC', 'XVGBTC', 'LENDBTC',
    'CDTBTC', 'FUELBTC', 'RPXBTC', 'DOCKBTC', 'CHATBTC', 'CNDBTC', 'SNGLSBTC', 'DNTBTC', 'TRXBTC', 'RCNBTC', 'TNTBTC', 'MTHBTC', 'WPRBTC', 'YOYOBTC', 'GOBTC', 'DATABTC', 'ZILBTC', 'QSPBTC', 'SNTBTC',
    'OSTBTC', 'VIBBTC', 'REQBTC', 'AGIBTC', 'ENJBTC', 'QLCBTC', 'SNMBTC', 'QKCBTC', 'GTOBTC', 'DLTBTC', 'MANABTC', 'VIBEBTC', 'POABTC', 'ADABTC', 'SYSBTC', 'BCPTBTC', 'THETABTC', 'ASTBTC', 'XEMBTC',
    'APPCBTC', 'LRCBTC', 'BTSBTC', 'LOOMBTC', 'SUBBTC', 'ARDRBTC', 'CVCBTC', 'CMTBTC', 'BLZBTC', 'AMBBTC', 'WINGSBTC', 'GNTBTC', 'POWRBTC', 'BATBTC', 'POLYBTC', 'WABIBTC', 'OAXBTC', 'ADXBTC',
    'XLMBTC', 'STORJBTC', 'TRIGBTC', 'LINKBTC', 'NAVBTC', 'BQXBTC', 'ELFBTC', 'BRDBTC', 'INSBTC', 'ICNBTC', 'RLCBTC', 'KNCBTC', 'AIONBTC', 'XRPBTC', 'EVXBTC', 'ARNBTC', 'GRSBTC', 'RDNBTC', 'IOTABTC',
    'SALTBTC', 'VIABTC', 'ENGBTC', 'ICXBTC', 'MODBTC', 'MTLBTC', 'MDABTC', 'ARKBTC', 'ZRXBTC', 'NXSBTC', 'STEEMBTC', 'TUSDBTC', 'PAXBTC', 'EDOBTC', 'AEBTC', 'WANBTC', 'PIVXBTC', 'KMDBTC', 'NULSBTC',
    'GXSBTC', 'BNTBTC', 'STRATBTC', 'VENBTC', 'NASBTC', 'ONTBTC', 'BCDBTC', 'NEBLBTC', 'WAVESBTC', 'NANOBTC', 'HCBTC', 'CLOAKBTC', 'WTCBTC', 'LSKBTC', 'PPTBTC', 'OMGBTC', 'QTUMBTC', 'LUNBTC',
    'SKYBTC', 'MCOBTC', 'HSRBTC', 'EOSBTC', 'GASBTC', 'XZCBTC', 'BNBBTC', 'GVTBTC', 'ETCBTC', 'REPBTC', 'ZENBTC', 'NEOBTC', 'BTGBTC', 'DGDBTC', 'LTCBTC', 'XMRBTC', 'ZECBTC', 'DASHBTC', 'ETHBTC',
    'BCCBTC'
]
#COINPAIRS = ['XZCBTC', 'BNBBTC', 'ETHBTC', 'REPBTC', 'ZENBTC']

COINPAIRS_STRUCTURE = ['ACTIVE', 'COINPAIR']
HISTORY_STRUCTURE = [
    'INTERVAL', 'OPEN_TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'CLOSE_TIME', 'QUOTE_ASSET_VOLUME', 'NUMBER_TRADES', 'TAKER_BASE_ASSET_VOLUME', 'TAKER_QUOTE_ASSET_VOLUME', 'IGNORE', 'MACD',
    'MACD_SIGNAL', 'MACD_DIFF', 'RSI', 'UPPERBAND', 'LOWERBAND'
]
BALANCES_STRUCTURE = ['ASSET', 'FREE']
ACTIONS_STRUCTURE = ['COINPAIR', 'TIME', 'USED', 'ACTION', 'QUANTITY', 'PRICE']
ORDERS_STRUCTURE = ['COINPAIR', 'ID', 'TIME', 'STATUS']

#TIME_INTERVALS = ['5m', '15m', '30m', '1h', '2h', '4h']
TIME_INTERVALS = ['30m']

# Binance Constants
BINANCE_PUBLIC_KEY = ''
BINANCE_SECRET_KEY = ''

# Database Constants - CURRENTLY DOWN. AWS FREE TIER ENDED
DB_NAME = 'test2'
DB_HOST = 'binance-bot.cfypif4yfq4f.us-east-1.rds.amazonaws.com'
DB_PORT = '3306'
DB_USER = 'epsenex'
DB_PASS = 'Minecraft#1PUBG#2'

# SMTP Email Constants
EMAIL_USERNAME = 'alecjmasterson@gmail.com'
EMAIL_PASS = 'tmnvzdlgdnntaavh'

HISTORY_START_DATE = datetime(2018, 2, 1)        # Starting date, in milliseconds, that historical data starts from
BACKTEST_START_DATE = datetime(2018, 9, 1)        # Starting date, in milliseconds, that backtesting runs from
BACKTEST_END_DATE = datetime(2018, 10, 1)        # End date, in milliseconds, that backtesting stops

# Backtesting Constants
BACKTEST_CANDLE_INTERVAL = 30        # Used to increment the datetime object.
BACKTEST_CANDLE_INTERVAL_STRING = '30m'        # Used to filter the candle data.
STARTING_BALANCE = 1.0        # The starting BTC in wallet.
WINDOW_SIZE = 24        # Sliding window size for coinpair candle history.

# Position Arming Concept
MAX_POSITIONS = 4        # Max number of open positions to hold.
POSITION_ARM = 1.02        # Percent gain where Position is armed to sell.
STOP_LOSS = 0.995        # If armed, percent drop from the max price.
POSITION_DROP = 0.99        # Percent drop from buy price.

ORDER_TIME_LIMIT = 11        # How long a Binance order should be live before manually cancelling.


def set_optimized(window_size, max_positions, position_arm, stop_loss, position_drop):
    global WINDOW_SIZE
    WINDOW_SIZE = window_size
    global MAX_POSITIONS
    MAX_POSITIONS = max_positions
    global POSITION_ARM
    POSITION_ARM = position_arm
    global STOP_LOSS
    STOP_LOSS = stop_loss
    global POSITION_DROP
    POSITION_DROP = position_drop
