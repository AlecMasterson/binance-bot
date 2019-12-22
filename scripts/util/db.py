from util.decor import retry
import sqlalchemy
import os


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
    db = sqlalchemy.create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(
        os.environ['DB_TEST_USER'],
        os.environ['DB_TEST_PASS'],
        os.environ['DB_TEST_HOST'],
        os.environ['DB_TEST_PORT'],
        os.environ['DB_TEST_NAME']
    ))
    logger.info('Connect to the DB')

    return db


@retry
def insert_data(*, db, tableName, qualifier, data):
    """
    Insert data into the DB and ignore duplicate rows.

    Parameters:
        db (sqlalchemy.engine.base.Engine): An open connected client to the DB.
        tableName (str): Name of the table the data is being inserted into.
        qualifier (str): A special unique qualifier for this data.
        data (pandas.core.frame.DataFrame): The actual data being inserted.
    """

    tempTableName = 'temp_{}_{}'.format(tableName, qualifier)

    data.to_sql(
        con=db,
        name=tempTableName,
        if_exists='replace',
        index=False
    )

    connect = db.connect()
    connection.execute("INSERT IGNORE INTO " + tableName + " SELECT * FROM " + tempTableName + ";")
    connection.close()


def organize_table_history(*, data):
    """
    Organize historical data in a specific order for the DB.

    Parameters:
        data (pandas.core.frame.DataFrame): Historical pricing data.

    Returns:
        pandas.core.frame.DataFrame: Historical pricing data organized for the DB.
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
