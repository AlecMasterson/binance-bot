from sqlalchemy.orm import sessionmaker
from util.decor import retry
import sqlalchemy
import os
import pandas


@retry
def db_connect(*, logger):
    """
    Create an open connection to the DB.

    Parameters:
        logger (logging.Logger): An open logging object.

    Returns:
        sqlalchemy.engine.base.Engine: An open connected client to the DB.
    """

    logger.info('Connecting to the DB...')

    env = os.environ['CUR_ENV']
    db = sqlalchemy.create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(
        os.environ['DB_{}_USER'.format(env)],
        os.environ['DB_{}_PASS'.format(env)],
        os.environ['DB_{}_HOST'.format(env)],
        os.environ['DB_{}_PORT'.format(env)],
        os.environ['DB_{}_NAME'.format(env)]
    ))

    Session = sessionmaker(bind=db)
    session = Session()

    logger.info('Connected to the DB')
    return session


@retry
def insert_data(*, logger, db, tableName, qualifier, data):
    """
    Insert data into the DB and ignore duplicate rows.

    Parameters:
        logger (logging.Logger): An open logging object.
        db (sqlalchemy.engine.base.Engine): An open connected client to the DB.
        tableName (str): Name of the table the data is being inserted into.
        qualifier (str): Unique qualifier for the data.
        data (pandas.core.frame.DataFrame): Data being inserted.
    """

    logger.info('Inserting Data into Table \'{}\' with Qualifier = {}'.format(tableName, qualifier))

    tempTableName = 'temp_{}_{}'.format(tableName, qualifier)

    data.to_sql(
        con=db.get_bind(),
        name=tempTableName,
        if_exists='replace',
        index=False
    )

    db.execute("INSERT IGNORE INTO " + tableName + " SELECT * FROM " + tempTableName + ";")

    logger.info('Inserted Data into Table \'{}\' with Qualifier = {}'.format(tableName, qualifier))


@retry
def get_data(*, logger, db, model, query):
    results = db.query(model)
    for key in query:
        results = results.filter(getattr(model, key) == query[key])
    return results.all()


def organize_table_balance(*, data):
    """
    Organize Balance data in a specific order for the DB.

    Parameters:
        data (pandas.core.frame.DataFrame): Balance data.

    Returns:
        pandas.core.frame.DataFrame: Balance data organized for the DB.
    """

    return data[[
        'user',
        'asset',
        'free',
        'locked'
    ]]


def organize_table_decision(*, data):
    """
    Organize Decision data in a specific order for the DB.

    Parameters:
        data (pandas.core.frame.DataFrame): Decision data.

    Returns:
        pandas.core.frame.DataFrame: Decision data organized for the DB.
    """

    return data[[
        'model',
        'symbol',
        'timestamp',
        'choice'
    ]]


def organize_table_history(*, data):
    """
    Organize History data in a specific order for the DB.

    Parameters:
        data (pandas.core.frame.DataFrame): History data.

    Returns:
        pandas.core.frame.DataFrame: History data organized for the DB.
    """

    return data[[
        'symbol', 'width', 'open_time',
        'open', 'high', 'low', 'close', 'number_trades', 'volume',
        'close_time',
        'momentum_ao', 'momentum_mfi', 'momentum_rsi',
        'momentum_stoch', 'momentum_stoch_signal',
        'momentum_tsi', 'momentum_uo', 'momentum_wr',
        'trend_adx_neg', 'trend_adx_pos',
        'trend_aroon_down', 'trend_aroon_ind', 'trend_aroon_up',
        'trend_cci', 'trend_dpo',
        'trend_ema_fast', 'trend_ema_slow',
        'trend_ichimoku_a', 'trend_ichimoku_b',
        'trend_kst', 'trend_kst_diff', 'trend_kst_sig',
        'trend_macd', 'trend_macd_diff', 'trend_macd_signal',
        'trend_mass_index',
        'trend_trix',
        'trend_visual_ichimoku_a', 'trend_visual_ichimoku_b',
        'trend_vortex_diff', 'trend_vortex_ind_neg', 'trend_vortex_ind_pos',
        'volatility_bbh', 'volatility_bbhi',
        'volatility_bbl', 'volatility_bbli',
        'volatility_bbm',
        'volatility_dch', 'volatility_dchi',
        'volatility_dcl', 'volatility_dcli',
        'volatility_kcc',
        'volatility_kch', 'volatility_kchi',
        'volatility_kcl', 'volatility_kcli'
    ]]


def organize_table_position(*, data):
    """
    Organize Position data in a specific order for the DB.

    Parameters:
        data (pandas.core.frame.DataFrame): Position data.

    Returns:
        pandas.core.frame.DataFrame: Position data organized for the DB.
    """

    return data[[
        'id',
        'user', 'symbol', 'open',
        'buyTime', 'buyPrice',
        'sellTime', 'sellPrice',
        'amount', 'roi'
    ]]
