import helpers, argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Balances').parse_args()

    client = helpers.binance_connect()

    balances = {}
    for coinpair in utilities.COINPAIRS:
        try:
            balances[coinpair] = client.get_asset_balance(asset=balance['asset'])['free']
        except:
            print('ERROR: Failed to Retrieve \'' + coinpair[:-3] + '\' Balance from the Binance API')

    # TODO: Update the DB with the new balances.
