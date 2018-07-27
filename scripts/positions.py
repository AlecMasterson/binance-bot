import argparse, pandas, sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities
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
        positions = pandas.DataFrame(columns=['open', 'time', 'age', 'symbol', 'amount', 'price', 'current', 'fee', 'result', 'peak', 'stopLoss', 'order_id'])
        orders = pandas.DataFrame(columns=['order_id', 'symbol', 'side', 'status', 'time', 'executedQty'])
        try:
            positions.to_csv('data/online/positions.csv', index=False)
            orders.to_csv('data/online/orders.csv', index=False)
        except:
            utilities.throw_info('Failed to Create Missing Files', True)
    except:
        utilities.throw_error('Failed to Load Data Files', True)

    # TODO: Actually update the positions.
    '''
    self.age = time - self.time
    self.current = price
    self.result = self.current / self.price
    if self.result > self.peak: self.peak = self.result
    if self.peak > utilities.STOP_LOSS_ARM and self.peak - self.result > utilities.STOP_LOSS: self.stopLoss = True
    '''

    try:
        positions.to_csv('data/online/positions.csv', index=False)
    except:
        utilities.throw_info('Failed to Update File', True)
