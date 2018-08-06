import utilities, argparse, pandas, ta
from scripts import helpers
import strategy

logger = helpers.create_logger('backtest')


def check_time_limit(coinpair, price, index):
    startTime = coinpair.at[index, 'CLOSE_TIME']
    curIndex = index
    while curIndex < len(coinpair.index) and coinpair.at[curIndex, 'CLOSE_TIME'] - startTime <= utilities.ORDER_TIME_LIMIT * 3e5:
        if price < coinpair.at[curIndex, 'HIGH'] and price > coinpair.at[curIndex, 'LOW']: return True
        curIndex += 1
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backtesting Script for the Binance Bot')
    parser.add_argument('-o', '--optimize', help='True if optimizing the Bot', action='store_true', required=False)
    args = parser.parse_args()
    error = False

    data = {}
    for coinpair in utilities.COINPAIRS:
        data[coinpair] = pandas.read_csv('data/history/' + coinpair + '.csv')

    perm = {}
    trade_points = {}
    combinedPositions = []

    for coinpair in utilities.COINPAIRS:
        perm[coinpair] = {'aboveZero': False, 'belowZero': False, 'goingUp': 0, 'goingDown': 0}
        trade_points[coinpair] = {'buy': [], 'sell': []}
        if not args.optimize: logger.info('Simulating Coinpair \'' + coinpair + '\'...')

        result = 1.0
        selling = False
        for index, row in data[coinpair].iterrows():
            if index == 0 or data[coinpair].at[index, 'OPEN_TIME'] < utilities.BACKTEST_START_DATE: continue

            price = strategy.check_buy(perm[coinpair], data[coinpair], index)
            if not selling and price != None and check_time_limit(data[coinpair], price, index):
                trade_points[coinpair]['buy'].append(index - 1)
                selling = True
            if selling and strategy.check_sell(perm[coinpair], data[coinpair], index) and check_time_limit(data[coinpair], row['OPEN'], index):
                trade_points[coinpair]['sell'].append(index - 1)
                result = result * data[coinpair].at[trade_points[coinpair]['sell'][-1], 'CLOSE'] / data[coinpair].at[trade_points[coinpair]['buy'][-1], 'CLOSE']
                selling = False

        if not args.optimize: logger.info('Successfully Simulated Coinpair \'' + coinpair + '\' with Resulting ' + str(result * 100) + ' % ROI')

        if args.optimize:
            utilities.throw_info('Exporting Results from Coinpair \'' + coinpair + '\'...')
            try:
                with open('data/backtesting/' + coinpair + '.csv', 'w') as file:
                    file.write('used,time,end,price,current\n')
                    for pos in finalPositions:
                        file.write('1,' + str(pos.time) + ',' + str(pos.time + pos.age) + ',' + str(pos.price) + ',' + str(pos.current) + '\n')
                    for pos in otherPositions:
                        file.write('0,' + str(pos.time) + ',' + str(pos.time + pos.age) + ',' + str(pos.price) + ',' + str(pos.current) + '\n')
            except:
                utilities.throw_error('Failed to Export Results from Coinpair \'' + coinpair + '\'', False)
            utilities.throw_info('Successfully Exported Results from Coinpair \'' + coinpair + '\'...')

    if error: sys.exit(1)
