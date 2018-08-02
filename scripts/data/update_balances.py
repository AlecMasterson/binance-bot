import helpers, argparse, time, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities

logger = helpers.create_logger('update_balances')

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Balances').parse_args()
    errors = 0

    client = helpers.binance_connect(logger)
    db, db_cursor = helpers.db_connect(logger)

    logger.info('Starting Infinite Loop... Hold On Tight!')
    while errors < 10:
        balances = {}
        for coinpair in utilities.COINPAIRS:
            try:
                logger.info('Getting \'' + coinpair[:-3] + '\' Balance from the Binance API...')
                balances[coinpair[:-3]] = client.get_asset_balance(asset=coinpair[:-3])['free']
            except:
                errors += 1
                logger.error('Failed to Get \'' + coinpair[:-3] + '\' Balance from the Binance API')

        for asset in balances:
            try:
                logger.info('Updating \'' + coinpair[:-3] + '\' Balance into the DB...')
                db_cursor.execute("INSERT INTO BALANCES VALUES ('" + asset + "', " + str(balances[asset]) + ") ON CONFLICT (ASSET) DO UPDATE SET FREE = Excluded.FREE;")
                db.commit()
            except:
                errors += 1
                logger.error('Failed to Update \'' + coinpair[:-3] + '\' Balance into the DB')

        time.sleep(15)

    helpers.db_disconnect(db, logger)
    if errors != 0: sys.exit(1)
