import utilities, argparse, pandas, ta, sys
from scripts import helpers, strategy

logger = helpers.create_logger('backtest')


def check_time_limit(coinpair, price, index):
    startTime = coinpair.at[index, 'CLOSE_TIME']
    curIndex = index
    while curIndex < len(coinpair.index) and coinpair.at[curIndex, 'CLOSE_TIME'] - startTime <= utilities.ORDER_TIME_LIMIT * 3e5:
        if price < coinpair.at[curIndex, 'HIGH'] and price > coinpair.at[curIndex, 'LOW']: return True
        curIndex += 1
    return False


def backtest(data):

    trade_points = {'buy': [], 'sell': []}
    result = 1.0
    selling = False

    for index, row in data.iterrows():
        if index < (utilities.WINDOW * 2) or data.at[index, 'OPEN_TIME'] < utilities.BACKTEST_START_DATE: continue

        action = strategy.action(data[:index])
        if not selling and action == 'BUY' and check_time_limit(data, row['OPEN'], index):
            trade_points['buy'].append(index - 1)
            selling = True
        elif selling and action == 'SELL' and check_time_limit(data, row['OPEN'], index):
            trade_points['sell'].append(index - 1)
            result = result * data.at[trade_points['sell'][-1], 'CLOSE'] / data.at[trade_points['buy'][-1], 'CLOSE']
            selling = False

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backtesting Script for the Binance Bot')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to download', type=str, dest='coinpair', required=True)
    parser.add_argument('-o', '--optimize', help='True if optimizing the Bot', action='store_true', required=False)
    args = parser.parse_args()

    try:
        step = 0

        if not args.optimize: logger.info('Reading \'' + args.coinpair + '\' Historical Data from File...')
        data = pandas.read_csv('data/history/' + args.coinpair + '.csv')
        step += 1

        if not args.optimize: logger.info('Simulating Coinpair \'' + args.coinpair + '\'...')
        result = backtest(data)
    except:
        if not args.optimize:
            if step == 0: logger.error('Failed to Read \'' + args.coinpair + '\' Historical Data from File')
            if step == 1: logger.error('Failed to Simulate Coinpair \'' + args.coinpair + '\'')
        sys.exit(1)

    if not args.optimize: logger.info('Successfully Simulated Coinpair \'' + args.coinpair + '\' with Resulting ' + str(result * 100) + ' % ROI')

    # TODO: Export backtesting results to './results/backtesting/'
