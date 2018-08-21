import sys, os, argparse, pandas, numpy
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import utilities, helpers, helpers_binance, helpers_db

logger = helpers.create_logger('verify_history')


def fun():
    client = helpers_binance.safe_connect(logger)
    if client is None: return None
    db = helpers_db.safe_connect(logger)
    if db is None: return None

    for coinpair in utilities.COINPAIRS:
        data = helpers_binance.safe_get_historical_data(logger, client, coinpair)
        if data is None: return None

        data = helpers.safe_calculate_overhead(logger, coinpair, data)
        if data is None: return None

        saved_data = helpers_db.safe_get_historical_data(logger, db, coinpair)

        if len(data.index) != len(saved_data.index):
            logger.error('Different Sized DataFrames')
            return None

        ne_stacked = (data != saved_data).stack()
        changed = ne_stacked[ne_stacked]
        if len(changed) > 0:
            changed.index.names = ['ROW', 'COL']
            difference_locations = numpy.where(data != saved_data)
            changed_from = data.values[difference_locations]
            changed_to = saved_data.values[difference_locations]
            differences = pandas.DataFrame({'FROM': changed_from, 'TO': changed_to}, index=changed.index)
            logger.error('Differences Found Here:\n' + str(differences))
            logger.error('\n' + str(data.tail(5)) + '\n\n' + str(saved_data.tail(5)))
            return None

    return True


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Verifying All History in the DB').parse_args()

    message = 'Verifying All History in the DB'
    result = helpers.bullet_proof(logger, message, lambda: fun())
    if result is None: sys.exit(1)
    else:
        logger.info('SUCCESS - ' + message)
        sys.exit(0)
