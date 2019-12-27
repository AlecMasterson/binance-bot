import logging
import datetime
import os
import time


def main(*, name):
    """
    Setup a function for proper logging and error handling.

    Function Requirements:
        logger (logging.Logger): An open logging object.

    Parameters:
        name (str): Name of the logger file that the function will use.

    Usage:
        @main(name=...)
        def fun(..., *, logger, ...):
    """

    def main_function(f):
        def wrapper(*args, **kwargs):
            logger = None

            try:
                import util.util

                logger = logging.getLogger(name)
                logger.setLevel(logging.DEBUG)

                fileHandler = logging.FileHandler(util.util.get_file_path(
                    create=True,
                    directoryTree=('{}/logs/'.format(os.environ['PROJECT_PATH']), datetime.datetime.today().strftime('%Y-%m-%d')),
                    fileName='{}.log'.format(name)
                ))
                streamHandler = logging.StreamHandler()

                formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
                fileHandler.setFormatter(formatter)
                streamHandler.setFormatter(formatter)

                logger.addHandler(fileHandler)
                logger.addHandler(streamHandler)

                kwargs['logger'] = logger

                logger.info('Starting Function \'{}\'...'.format(f.__name__))
                f(*args, **kwargs)
                logger.info('Successfully Completed Function \'{}\''.format(f.__name__))
            except Exception as e:
                msg = 'Unexpected Error Running Function \'{}\': {}'.format(f.__name__, e)
                if logger is not None:
                    logger.exception(msg)
                else:
                    print(msg)
        return wrapper
    return main_function


def retry(f):
    """
    Attempt a function up to 3 times. If an Exception is thrown, wait before retrying.

    Function Requirements:
        logger (logging.Logger): An open logging object.

    Usage:
        @retry
        def fun(..., *, logger, ...):
    """

    def retry_function(*args, **kwargs):
        attempt = 1
        while attempt <= 3:
            try:
                if attempt > 1:
                    kwargs['logger'].info('Sleeping for 5 Seconds...')
                    time.sleep(5)
                    kwargs['logger'].info('Function \'{}\' Attempt #{}...'.format(f.__name__, attempt))

                return f(*args, **kwargs)
            except Exception as e:
                kwargs['logger'].exception('Unexpected Error Attempting Function \'{}\': {}'.format(f.__name__, e))
            attempt += 1
        raise Exception('Attempt Limit Reached for Function \'{}\''.format(f.__name__))
    return retry_function
