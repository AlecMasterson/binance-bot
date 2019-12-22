import argparse
import pandas
import numpy


def getInterval(data, interval):
    temp = data[data['INTERVAL'] == interval].sort_values(
        by=['OPEN_TIME']
    ).drop(
        columns=['SYMBOL', 'INTERVAL']
    ).reset_index(drop=True)

    return temp


def getCandleClose(interval, data, time):
    print(interval)
    print(time)
    print(data[data['CLOSE_TIME'] == time]['CLOSE'].values)
    return data[data['CLOSE_TIME'] == time]['CLOSE'].values[0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backtest a Symbol')
    parser.add_argument('-s', '--symbol', help='the symbol to backtest', dest='SYMBOL', required=True)
    args = parser.parse_args()

    data = pandas.read_csv('./data/history/{}.csv'.format(args.SYMBOL))

    data2H = getInterval(data, '2h')
    data4H = getInterval(data, '4h')
    data6H = getInterval(data, '6h')
    data12H = getInterval(data, '12h')

    best = 0
    config = 0
    for i in range(10):
        if i < 2:
            continue
        wallet = 1.0
        prev = None
        for index, row in data4H.iterrows():
            if prev is not None and (row['CLOSE'] / prev) > ((i / 1000) + 1):
                # print('Buying at {} and Selling at {} for a {}% Profit'.format(
                #    prev, row['CLOSE'], (row['CLOSE'] / prev)))
                wallet *= (row['CLOSE'] / prev)
            prev = row['CLOSE']
        if wallet > best:
            best = wallet
            config = i
    print(best)
    print(config)
    1/0

    print(data4H['CLOSE_TIME'])

    time = data4H['CLOSE_TIME'].values[0]
    while time < (data4H['CLOSE_TIME'].values[len(data4H)-1] - (14400000 * 5)):
        current = getCandleClose('4h', data4H, time)

        if (getCandleClose('4h', data4H, time + numpy.timedelta64(4, 'h')) / current) > 1.005:
            if getCandleClose('2h', data2H, time + numpy.timedelta64(2, 'h')) >= current:
                print('Buy at Time \'{}\''.format(time))
            else:
                print('Buy at \'{}\''.format(time))

        time += numpy.timedelta64(4, 'h')
