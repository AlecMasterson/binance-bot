import argparse, pandas, sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities
from binance.client import Client

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB of Current Balances').parse_args()

    try:
        client = Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        utilities.throw_error('Failed to Connect to the Binance API', True)

    try:
        balances = pandas.read_csv('data/online/balances.csv')
    except FileNotFoundError:
        balances = pandas.DataFrame(columns=['symbol', 'free'])
        try:
            balances.to_csv('data/online/balances.csv', index=False)
        except:
            utilities.throw_info('Failed to Create Missing Files', True)
    except:
        utilities.throw_error('Failed to Load Data Files', True)

    errors = 0
    for index, balance in balances.iterrows():
        try:
            balances['free'] = client.get_asset_balance(asset=balance['asset'])['free']
        except:
            errors += 1
            utilities.throw_error('Failed to Retrieve Balance from Binance API', False)

    try:
        balances.to_csv('data/online/balances.csv', index=False)
    except:
        utilities.throw_info('Failed to Update File', True)

    if errors > 0:
        utilities.throw_info('Finished With ' + str(errors) + ' Errors')
        sys.exit(1)
