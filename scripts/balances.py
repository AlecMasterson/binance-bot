import helpers, argparse, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Balances').parse_args()

    client = helpers.binance_connect()

    db = helpers.db_connect()
    db_cursor = db.cursor()

    balances = {}
    for coinpair in utilities.COINPAIRS:
        try:
            balances[coinpair[:-3]] = client.get_asset_balance(asset=coinpair[:-3])['free']
        except:
            print('ERROR: Failed to Retrieve \'' + coinpair[:-3] + '\' Balance from the Binance API')

    for asset in balances:
        try:
            db_cursor.execute("INSERT INTO BALANCES VALUES ('" + asset + "', " + str(balances[asset]) + ") ON CONFLICT (ASSET) DO UPDATE SET FREE = Excluded.FREE;")
            db.commit()
        except:
            print('ERROR: Failed to Update \'' + coinpair[:-3] + '\' Balance into the DB')

    try:
        db.close()
    except:
        print('ERROR: Failed to Close the DB Connection')
        sys.exit(1)
