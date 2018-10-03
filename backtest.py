import utilities, argparse, pandas, ta, sys, traceback
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
    backtest_props = {'buy': [], 'sell': [], 'result': 1.0}
    observation = {'selling': False, 'maximum': None, 'minimum': None, 'going_up': 0, 'going_down': 0}

    data = data.drop(data[data['OPEN_TIME'] < utilities.BACKTEST_START_DATE].index).reset_index(drop=True)

    for index, row in data[utilities.WINDOW * 2:].iterrows():
        action, observation = strategy.action_alec(data[:index], observation)

        if not observation['selling'] and action == 'BUY' and check_time_limit(data, row['OPEN'], index):
            backtest_props['buy'].append(row['OPEN_TIME'])
            observation['selling'] = True
        elif observation['selling'] and action == 'SELL' and check_time_limit(data, row['OPEN'], index):
            backtest_props['sell'].append(row['OPEN_TIME'])
            backtest_props['result'] = backtest_props['result'] * data.at[backtest_props['sell'][-1], 'CLOSE'] / data.at[backtest_props['buy'][-1], 'CLOSE']
            observation['selling'] = False

    logger.info('Completed Positions: ' + str(len(backtest_props['sell'])))
    return backtest_props


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backtesting Script for the Binance Bot')
    parser.add_argument('-c', '--coinpair', help='the Coinpair to download', type=str, dest='coinpair', required=True)
    parser.add_argument('-o', '--optimize', help='True if optimizing the Bot', action='store_true', required=False)
    parser.add_argument('-p', '--plot', help='True if plotting the results', action='store_true', required=False)
    args = parser.parse_args()

    try:
        step = 0

        if not args.optimize: logger.info('Reading \'' + args.coinpair + '\' Historical Data from File...')
        data = pandas.read_csv('data/history/' + args.coinpair + '.csv')
        step += 1

        if not args.optimize: logger.info('Simulating Coinpair \'' + args.coinpair + '\'...')
        results = backtest(data)
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        if not args.optimize:
            if step == 0: logger.error('Failed to Read \'' + args.coinpair + '\' Historical Data from File')
            if step == 1: logger.error('Failed to Simulate Coinpair \'' + args.coinpair + '\'')
        sys.exit(1)

    if not args.optimize: logger.info('Successfully Simulated Coinpair \'' + args.coinpair + '\' with Resulting ' + str(results['result'] * 100) + ' % ROI')

    # TODO: Export backtesting results to './results/backtesting/'
    if args.plot:
        logger.info('Plotting Coinpair \'' + args.coinpair + '\' Backtesting Results...')
