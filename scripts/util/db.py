from sqlalchemy.orm import sessionmaker
import sqlalchemy
import os


def db_connect(*, logger):
    """
    Create an open connection to the DB.

    Parameters:
        logger (logging.Logger): An open logging object.

    Returns:
        sqlalchemy.orm.session.Session: An open connected client to the DB.
    """

    env = os.environ['CUR_ENV']

    db = sqlalchemy.create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(
        os.environ['DB_{}_USER'.format(env)],
        os.environ['DB_{}_PASS'.format(env)],
        os.environ['DB_{}_HOST'.format(env)],
        os.environ['DB_{}_PORT'.format(env)],
        os.environ['DB_{}_NAME'.format(env)]
    ))

    SessionMaker = sessionmaker(bind=db)
    session = SessionMaker()

    logger.info('Connected to the \'{}\' DB'.format(env))
    return session
