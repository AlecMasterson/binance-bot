import logging
import datetime
import os


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

                date = datetime.datetime.now()
                fileHandler = logging.FileHandler(util.util.get_file_path(
                    create=True,
                    directoryTree=(os.environ['PROJECT_PATH'], 'logs', date.strftime('%Y-%m-%d')),
                    fileName='{}-{}.log'.format(name, date.strftime('%H-%M-%S'))
                ))
                streamHandler = logging.StreamHandler()

                formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
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
