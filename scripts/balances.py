import helpers, argparse, pandas, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Balances').parse_args()

    client = helpers.connect_binance()

    balances = helpers.read_csv('data/online/balances.csv', utilities.BALANCES_STRUCTURE)

    for coinpair in utilities.COINPAIRS:
        if not (balances['asset'] == coinpair[:-3]).any(): balances = balances.append({'asset': coinpair[:-3], 'free': 0}, ignore_index=True)

    errors = 0
    for index, balance in balances.iterrows():
        try:
            balances['free'] = client.get_asset_balance(asset=balance['asset'])['free']
        except:
            errors += 1
            utilities.throw_error('balances', 'Failed to Retrieve \'' + balance['asset'] + '\' Balance from Binance API', False)

    helpers.to_csv('data/online/balances.csv', utilities.BALANCES_STRUCTURE, balances)

    if errors > 0:
        utilities.throw_info('balances', 'Finished With ' + str(errors) + ' Errors')
        sys.exit(1)
