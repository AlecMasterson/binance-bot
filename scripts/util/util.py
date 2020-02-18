import json
import os
import pkgutil
import trading_models


def load_config(*, logger):
    """
    Read the JSON configuration file.

    Parameters:
        logger (logging.Logger): An open logging object.

    Returns:
        dict: The JSON configuration file.
    """

    config = json.load(open(get_file_path(
        create=False,
        directoryTree=(os.environ['PROJECT_PATH'], 'scripts'),
        fileName='config.json'
    )))

    logger.info('Loaded the Config File')
    return config


def load_trading_models(*, logger):
    """
    Load all Trading-Model modules.

    Parameters:
        logger (logging.Logger): An open logging object.

    Returns:
        list: List of loaded Trading-Model modules.
    """

    tradingModels = []

    for loader, name, is_pkg in pkgutil.walk_packages(trading_models.__path__):
        tradingModels.append(loader.find_module(name).load_module(name))

    if len(tradingModels) == 0:
        raise Exception('No Trading-Models Found')

    logger.info('Loaded {} Trading-Models'.format(len(tradingModels)))
    return tradingModels


def get_file_path(*, create, directoryTree, fileName):
    """
    Return an OS path to a file and create the directories if required.

    Parameters:
        create (bool): True if the directory tree is allowed to be created.
        directoryTree (tuple): An in-order tuple of directories to reach the file.
        fileName (str): Name of the file at the end of the OS path.

    Returns:
        str: An OS path to the file.
    """

    path = os.path.join(*directoryTree)
    if create and (not os.path.exists(path) or not os.path.isdir(path)):
        os.makedirs(path)
    return os.path.join(path, fileName)
