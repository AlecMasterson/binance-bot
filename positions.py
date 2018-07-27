import utilities, argparse, pandas
from binance.client import Client

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB of Current Positions').parse_args()

    try:
        client = Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        utilities.throw_error('Failed to Connect to the Binance API', True)

    try:
        positions = pandas.read_csv('data/online/positions.csv')
        orders = pandas.read_csv('data/online/orders.csv')
    except FileNotFoundError:
        positions = pandas.DataFrame(columns=['order_id', 'symbol'])
        orders = pandas.DataFrame(columns=['order_id', 'symbol', 'side', 'status', 'time', 'executedQty'])
        try:
            positions.to_csv('data/online/positions.csv', index=False)
            orders.to_csv('data/online/orders.csv', index=False)
        except:
            utilities.throw_info('Failed to Create Missing Files', True)
    except:
        utilities.throw_error('Failed to Load Data Files', True)

    # TODO: Actually update the positions.

    try:
        positions.to_csv('data/online/positions.csv', index=False)
    except:
        utilities.throw_info('Failed to Update File', True)
