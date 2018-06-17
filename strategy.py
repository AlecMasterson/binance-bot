import utilities


def slope(x1, x2, y1, y2):
    return (y2 - y1) / (x2 - x1)


def prev(time, num):
    return time - (utilities.CANDLE_INTERVAL * num)


def check_buy(perm, time, coinpair):
    for i in range(0, 4):
        if not prev(time, i) in coinpair.info.index: return

    index = (time - utilities.START_DATE) / utilities.CANDLE_INTERVAL

    if index < 3: return
    if coinpair.get_item(prev(time, 1), 'macdDiff') > 0: perm['aboveZero'] = True
    if index < utilities.WINDOW: return

    minimum = coinpair.get_item(prev(time, 1), 'macdDiff')
    for i in range(2, utilities.WINDOW + 1):
        if coinpair.get_item(prev(time, i), 'macdDiff') < minimum: minimum = coinpair.get_item(prev(time, i), 'macdDiff')

    valid = False

    macdSlope = slope(1, 2, coinpair.get_item(prev(time, 2), 'macd'), coinpair.get_item(prev(time, 1), 'macd'))
    signalSlope = slope(1, 2, coinpair.get_item(prev(time, 2), 'macdSignal'), coinpair.get_item(prev(time, 1), 'macdSignal'))
    if perm['aboveZero'] and coinpair.get_item(prev(time, 1), 'macdDiff') < (minimum * utilities.PERCENT) and coinpair.get_item(prev(time, 2), 'macdDiff') < coinpair.get_item(
            prev(time, 3), 'macdDiff'):
        if coinpair.get_item(prev(time, 1), 'macd') > coinpair.get_item(prev(time, 1), 'macdSignal'):
            if macdSlope > signalSlope: perm['slopes'].append(macdSlope - signalSlope)
            else: valid = True
        elif coinpair.get_item(prev(time, 1), 'macd') < coinpair.get_item(prev(time, 1), 'macdSignal'):
            if macdSlope < signalSlope: perm['slopes'].append(signalSlope - macdSlope)
            else: valid = True
        if len(perm['slopes']) > 1 and perm['slopes'][-1] - (perm['slopes'][-2] - perm['slopes'][-1]) < 0:
            valid = True

    if valid and coinpair.get_item(prev(time, 1), 'candle').close < (
        (coinpair.get_item(prev(time, 1), 'upperband') - coinpair.get_item(prev(time, 1), 'lowerband')) / 2) + coinpair.get_item(prev(time, 1), 'lowerband'):
        #bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['slopes'] = []
        perm['aboveZero'] = False
        return coinpair.get_item(prev(time, 1), 'candle').close

    return None


def check_sell(perm, time, coinpair):
    for i in range(0, 4):
        if not prev(time, i) in coinpair.info.index: return

    index = (time - utilities.START_DATE) / utilities.CANDLE_INTERVAL

    if coinpair.get_item(prev(time, 1), 'macdDiff') < 0: perm['belowZero'] = True
    if index < utilities.TOP_WINDOW: return

    maximum = coinpair.get_item(prev(time, 1), 'macdDiff')
    for i in range(2, utilities.WINDOW + 1):
        if coinpair.get_item(prev(time, i), 'macdDiff') > maximum: maximum = coinpair.get_item(prev(time, i), 'macdDiff')

    valid = False

    macdSlope = slope(1, 2, coinpair.get_item(prev(time, 2), 'macd'), coinpair.get_item(prev(time, 1), 'macd'))
    signalSlope = slope(1, 2, coinpair.get_item(prev(time, 2), 'macdSignal'), coinpair.get_item(prev(time, 1), 'macdSignal'))
    if perm['belowZero'] and coinpair.get_item(prev(time, 1), 'macdDiff') > (maximum * utilities.PERCENT) and coinpair.get_item(prev(time, 2), 'macdDiff') > coinpair.get_item(
            prev(time, 3), 'macdDiff'):
        if coinpair.get_item(prev(time, 1), 'macd') > coinpair.get_item(prev(time, 1), 'macdSignal'):
            if macdSlope > signalSlope: perm['top_slopes'].append(macdSlope - signalSlope)
            else: valid = True
        elif coinpair.get_item(prev(time, 1), 'macd') < coinpair.get_item(prev(time, 1), 'macdSignal'):
            if macdSlope < signalSlope: perm['top_slopes'].append(signalSlope - macdSlope)
            else: valid = True
        if len(perm['top_slopes']) > 1 and perm['top_slopes'][-1] - (perm['top_slopes'][-2] - perm['top_slopes'][-1]) < 0:
            valid = True

    if valid and coinpair.get_item(prev(time, 1), 'candle').close > (
        (coinpair.get_item(prev(time, 1), 'upperband') - coinpair.get_item(prev(time, 1), 'lowerband')) / 2) + coinpair.get_item(prev(time, 1), 'lowerband'):
        #bot.plot_sell_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['top_slopes'] = []
        perm['belowZero'] = False
        return True

    return False

    if position.stopLoss: bot.sell(position)
    elif position.result < utilities.DROP: bot.sell(position)
