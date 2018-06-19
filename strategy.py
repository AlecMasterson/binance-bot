import utilities


def slope(x1, x2, y1, y2):
    return (y2 - y1) / (x2 - x1)


def check_buy(perm, coinpair, index):
    if index < 3: return

    if coinpair.overhead[index - 1]['macdDiff'] > 0: perm['aboveZero'] = True

    if index < utilities.WINDOW: return
    minimum = min([x['macdDiff'] for x in coinpair.overhead[index - utilities.WINDOW:index]])

    valid = False

    macdSlope = slope(1, 2, coinpair.overhead[index - 2]['macd'], coinpair.overhead[index - 1]['macd'])
    signalSlope = slope(1, 2, coinpair.overhead[index - 2]['macdSignal'], coinpair.overhead[index - 1]['macdSignal'])
    if perm['aboveZero'] and coinpair.overhead[index - 1]['macdDiff'] < (minimum * utilities.PERCENT) and coinpair.overhead[index - 2]['macdDiff'] < coinpair.overhead[index - 3]['macdDiff']:
        if coinpair.overhead[index - 1]['macd'] > coinpair.overhead[index - 1]['macdSignal']:
            if macdSlope > signalSlope: perm['slopes'].append(macdSlope - signalSlope)
            else: valid = True
        elif coinpair.overhead[index - 1]['macd'] < coinpair.overhead[index - 1]['macdSignal']:
            if macdSlope < signalSlope: perm['slopes'].append(signalSlope - macdSlope)
            else: valid = True
        if len(perm['slopes']) > 1 and perm['slopes'][-1] - (perm['slopes'][-2] - perm['slopes'][-1]) < 0:
            valid = True

    if valid and coinpair.candles[index - 1].close < ((coinpair.overhead[index - 1]['upperband'] - coinpair.overhead[index - 1]['lowerband']) / 2) + coinpair.overhead[index - 1]['lowerband']:
        #bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['slopes'] = []
        perm['aboveZero'] = False
        return coinpair.candles[index - 1].close

    return None


def check_sell(position, perm, coinpair, index):
    if coinpair.overhead[index - 1]['macdDiff'] < 0: perm['belowZero'] = True

    if index < utilities.TOP_WINDOW: return
    test = [x['macdDiff'] for x in coinpair.overhead[index - utilities.WINDOW:index]]
    if len(test) == 0: print(position.toString())
    maximum = max([x['macdDiff'] for x in coinpair.overhead[index - utilities.WINDOW:index]])

    valid = False

    macdSlope = slope(1, 2, coinpair.overhead[index - 2]['macd'], coinpair.overhead[index - 1]['macd'])
    signalSlope = slope(1, 2, coinpair.overhead[index - 2]['macdSignal'], coinpair.overhead[index - 1]['macdSignal'])
    if perm['belowZero'] and coinpair.overhead[index - 1]['macdDiff'] > (maximum * utilities.TOP_PERCENT) and coinpair.overhead[index - 2]['macdDiff'] > coinpair.overhead[index - 3]['macdDiff']:
        if coinpair.overhead[index - 1]['macd'] > coinpair.overhead[index - 1]['macdSignal']:
            if macdSlope > signalSlope: perm['top_slopes'].append(macdSlope - signalSlope)
            else: valid = True
        elif coinpair.overhead[index - 1]['macd'] < coinpair.overhead[index - 1]['macdSignal']:
            if macdSlope < signalSlope: perm['top_slopes'].append(signalSlope - macdSlope)
            else: valid = True
        if len(perm['top_slopes']) > 1 and perm['top_slopes'][-1] - (perm['top_slopes'][-2] - perm['top_slopes'][-1]) < 0:
            valid = True

    if valid and coinpair.candles[index - 1].close > ((coinpair.overhead[index - 1]['upperband'] - coinpair.overhead[index - 1]['lowerband']) / 2) + coinpair.overhead[index - 1]['lowerband']:
        #bot.plot_sell_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['top_slopes'] = []
        perm['belowZero'] = False
        return True

    return False

    if position.stopLoss: bot.sell(position)
    elif position.result < utilities.DROP: bot.sell(position)
