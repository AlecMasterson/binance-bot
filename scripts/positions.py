import helpers, argparse, pandas, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities

if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Positions').parse_args()

    client = helpers.connect_binance()

    positions = helpers.read_csv('data/online/positions.csv', utilities.POSITIONS_STRUCTURE)
    orders = helpers.read_csv('data/online/orders.csv', utilities.ORDERS_STRUCTURE)

    # TODO: Actually update the positions.
    '''
    self.age = time - self.time
    self.current = price
    self.result = self.current / self.price
    if self.result > self.peak: self.peak = self.result
    if self.peak > utilities.STOP_LOSS_ARM and self.peak - self.result > utilities.STOP_LOSS: self.stopLoss = True
    '''

    helpers.to_csv('data/online/positions.csv', utilities.POSITIONS_STRUCTURE, positions)
