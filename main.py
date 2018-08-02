import utilities, argparse
from scripts import helpers

logger = helpers.create_logger('main')

if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for the Binance Bot').parse_args()
    error = False

    # Connect to the Binance Client for all API calls.
    client = helpers.binance_connect(logger)

    logger.info('Starting Infinite Loop... Hold On Tight!')

    if error: sys.exit(1)
