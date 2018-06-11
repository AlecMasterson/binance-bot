import utilities, math


# Returns True if num1 and num2 are with range % of each other
# num1 - The first number
# num2 - The second number
# range - Percent threshold to test
def within_range(num1, num2, range):
    if (num1 - num2) / num2 < range:
        return True
    return False


def check_buy(bot, coinpair, index):
    if index < 3: return
    elif index < 36:
        if bot.minMACD == None or bot.data[coinpair].macd[index - 1] < bot.minMACD: bot.minMACD = bot.data[coinpair].macd[index - 1]
        if bot.data[coinpair].macd[index - 1] > 0: bot.primed = True
    valid = False
    if bot.data[coinpair].macd[index - 3] < 0 and bot.data[coinpair].macdDiff[index - 3] < 0 and bot.data[coinpair].macd[index - 3] < 0 and bot.data[coinpair].macdDiff[index - 1] < 0:
        if bot.data[coinpair].macdDiff[index - 2] < bot.data[coinpair].macdDiff[index - 3]:
            if bot.data[coinpair].macdDiff[index - 1] > bot.data[coinpair].macdDiff[index - 2] and bot.data[coinpair].macdDiff[index - 2] < -2e-6:
                valid = True

    if valid:
        if bot.data[coinpair].candles[index - 1].close < ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]:
            bot.buy(coinpair, bot.recent[coinpair][-1].close)
    return
    if bot.data[coinpair].macdDiff[index - 2] > 0 and bot.data[coinpair].macdDiff[index - 1] < 0:
        bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
    return

    if bot.minMACD == None or bot.data[coinpair].macd[index - 1] < bot.minMACD: bot.minMACD = bot.data[coinpair].macd[index - 1]
    if bot.data[coinpair].macd[index - 1] > 0:
        bot.primed = True
        bot.localMinMACD = None

    if bot.data[coinpair].macd[index - 1] < 0:
        if bot.localMinMACD == None or bot.data[coinpair].macd[index - 1] < bot.localMinMACD: bot.localMinMACD = bot.data[coinpair].macd[index - 1]
        if bot.primed and bot.data[coinpair].macd[index - 1] > bot.localMinMACD:
            bot.plot_buy_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
            bot.primed = False

    return

    # Never buy in the top half of the Bollinger Bands.
    if bot.data[coinpair].candles[index - 1].close >= ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return

    if bot.aboveZero and bot.data[coinpair].macd[index - 1] < bot.minMACD * 0.5:
        bot.aboveZero = False
        return

    maxPrice = None
    maxPriceIndex = None
    maxMACD = None
    maxTrades = None
    minPrice = None
    minPriceIndex = None
    minMACD = None
    minLower = None

    # Get the above values for the past 3 hours.
    for i in range(1, 37):
        if maxPrice == None or bot.data[coinpair].candles[index - i].close > maxPrice:
            maxPrice = bot.data[coinpair].candles[index - i].close
            maxPriceIndex = index - i
        if maxMACD == None or bot.data[coinpair].macd[index - i] > maxMACD:
            maxMACD = bot.data[coinpair].macd[index - i]
        if maxTrades == None or bot.data[coinpair].candles[index - i].numTrades > maxTrades:
            maxTrades = bot.data[coinpair].candles[index - i].numTrades
        if minPrice == None or bot.data[coinpair].candles[index - i].close < minPrice:
            minPrice = bot.data[coinpair].candles[index - i].close
            minPriceIndex = index - i
        if minMACD == None or bot.data[coinpair].macd[index - i] < minMACD:
            minMACD = bot.data[coinpair].macd[index - i]
        if minLower == None or bot.data[coinpair].lowerband[index - i] < minLower:
            minLower = bot.data[coinpair].lowerband[index - i]

    if bot.data[coinpair].candles[index - 1].close / minPrice > 1.0125: return
    #if bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 1] > bot.data[coinpair].macd[index - 3] - bot.data[coinpair].macd[index - 2]: return

    if bot.data[coinpair].macd[index - 1] < bot.bottom * utilities.ONE:
        if bot.data[coinpair].macd[index - 1] > bot.data[coinpair].macd[index - 3]:
            bot.plot_buy_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
            if utilities.ONE_Y == 1: bot.buy(coinpair, bot.recent[coinpair][-1].close)
    if bot.data[coinpair].macd[index - 1] < bot.bottom * utilities.TWO:
        if bot.data[coinpair].candles[index - 1].close < bot.data[coinpair].lowerband[index - 1]:
            bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
            if utilities.TWO_Y == 1: bot.buy(coinpair, bot.recent[coinpair][-1].close)
    elif bot.data[coinpair].macd[index - 1] < bot.bottom * utilities.THREE:
        if bot.data[coinpair].candles[index - 1].close < bot.data[coinpair].lowerband[index - 1]:
            bot.plot_buy_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
            if utilities.THREE_Y == 1: bot.buy(coinpair, bot.recent[coinpair][-1].close)

        #else:
        #bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})

        #bot.buy(coinpair, bot.recent[coinpair][-1].close)
    #if bot.data[coinpair].macd[index - 1] > bot.top and bot.data[coinpair].candles[index - 1].close > bot.data[coinpair].upperband[index - 1]:
    #bot.plot_buy_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
    return

    #if bot.data[coinpair].macd[index - 1] > 0: return
    if bot.data[coinpair].candles[index - 1].close >= ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return

    for x in range(1, utilities.V_DISTANCE):
        # Velocity between two candles ago and that minues x candles ago.
        v2 = (bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 2 - x])
        valid = True

        for y in range(1, utilities.V_PAST):
            if (bot.data[coinpair].macd[index - (2 + y)] - bot.data[coinpair].macd[index - (2 + y) - x]) < v2: valid = False
            v2 = (bot.data[coinpair].macd[index - (2 + y)] - bot.data[coinpair].macd[index - (2 + y) - x])
        v1 = (bot.data[coinpair].macd[index - 1] - bot.data[coinpair].macd[index - 1 - x])
        if good and v1 > 0:
            bot.buy(coinpair, bot.recent[coinpair][-1].close)
            #f v1 < 0 and v2 < 0 and v3 > 0 and v3 - v2 > 0:
            #bot.plot_buy_triggers.append({'color': colors[x - 4], 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
            #print(str(v2 - v1) + '\t' + str(v3 - v2))
    return
    a = (v2 - v1) / 12

    if v1 < 0 and v2 < 0 and v3 > 0 and v3 - v2 > 1e-7:
        bot.plot_buy_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        print(str(v2 - v1) + '\t' + str(v3 - v2))

    if a < -2e-7:
        bot.test = True
        bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
    if bot.test and a > 0:
        bot.test = False
        print(str(v2) + '\t' + str(v1) + '\t' + str(a))
        bot.plot_buy_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})

    # Don't buy if price is in the top half of the upper/lower BollingerBand range.
    if bot.data[coinpair].candles[index - 1].close >= ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return
    # Don't buy if the peak price happened after the min price.
    if minPriceIndex < maxPriceIndex: return
    return

    if maxTrades == bot.data[coinpair].candles[index - 1].numTrades:
        bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})

    #if bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 1] > bot.data[coinpair].macd[index - 3] - bot.data[coinpair].macd[index - 2]: return

    #if bot.data[coinpair].lowerband[index - 2] == minLower and bot.data[coinpair].lowerband[index - 2] > bot.data[coinpair].lowerband[index - 1]: return

    # If the previous close price fell below the lower BollingerBand.
    if bot.data[coinpair].candles[index - 1].close < bot.data[coinpair].lowerband[index - 1]:
        bot.plot_buy_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_trigger += utilities.TRIGGER_0

    if bot.data[coinpair].macd[index - 2] < 0 and bot.data[coinpair].macd[index - 1] > 0:
        bot.plot_buy_triggers.append({'color': 'orange', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_trigger += utilities.TRIGGER_1

    if bot.data[coinpair].macd[index - 1] < 0 and bot.data[coinpair].macd[index - 1] == minMACD:
        bot.plot_buy_triggers.append({'color': 'green', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_trigger += utilities.TRIGGER_2

    if bot.data[coinpair].candles[index - 2].close == minPrice and bot.data[coinpair].candles[index - 2].close < bot.data[coinpair].candles[index - 1].close:
        bot.plot_buy_triggers.append({'color': 'red', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_trigger += utilities.TRIGGER_3

    if maxPrice / bot.data[coinpair].candles[index - 1].close > 1.025:
        if bot.data[coinpair].candles[index - 1].close / minPrice > 1.005:
            bot.plot_buy_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
            bot.buy_trigger += utilities.TRIGGER_3

    return

    # Buy if the trigger value meets the required threshold.
    if bot.buy_trigger >= utilities.TRIGGER_THRESHOLD:
        bot.buy(coinpair, bot.recent[coinpair][-1].close)

    # Decay the trigger value, but not below zero.
    bot.buy_trigger -= utilities.TRIGGER_DECAY
    if bot.buy_trigger < 0.0: bot.buy_trigger = 0.0

    # SELLING
    #--------
    #--------
    #--------
    #--------
    '''maxPrice = -1000.0
    maxMACD = -1000.0
    minPrice = 1000.0
    minMACD = 1000.0

    for i in range(2, 24):
        if bot.data[coinpair].candles[index - i].close > maxPrice:
            maxPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] > maxMACD:
            maxMACD = bot.data[coinpair].macd[index - i]
        if bot.data[coinpair].candles[index - i].close < minPrice:
            minPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] < minMACD:
            minMACD = bot.data[coinpair].macd[index - i]

    if bot.data[coinpair].candles[index - 1].close / minPrice > 1.025:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3

    if bot.data[coinpair].macd[index - 1] < 0: return
    if bot.data[coinpair].macd[index - 1] - bot.data[coinpair].macd[index - 2] > bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 3]: return
    if bot.data[coinpair].candles[index - 1].close < ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return

    if bot.data[coinpair].candles[index - 1].close > bot.data[coinpair].upperband[index - 1]:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[0] += utilities.TRIGGER_0
    if bot.data[coinpair].macd[index - 2] > 0 and bot.data[coinpair].macd[index - 1] < 0:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[1] += utilities.TRIGGER_1

    if bot.data[coinpair].macd[index - 1] > 0 and bot.data[coinpair].macd[index - 1] == maxMACD:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[2] += utilities.TRIGGER_2
    if bot.data[coinpair].candles[index - 1].close == maxPrice:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3'''


def check_sell(bot, position, index):
    if index < 12: return
    coinpair = position.coinpair

    if position.stopLoss: bot.sell(position)
    elif position.result < utilities.DROP: bot.sell(position)
    return

    if sell: bot.sell(position)

    if bot.data[coinpair].macd[index - 1] > bot.top and bot.data[coinpair].candles[index - 1].close > bot.data[coinpair].upperband[index - 1]:
        bot.plot_buy_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell(position)
    return

    maxPrice = -1000.0
    maxMACD = -1000.0
    minPrice = 1000.0
    minMACD = 1000.0

    for i in range(2, 24):
        if bot.data[coinpair].candles[index - i].close > maxPrice:
            maxPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] > maxMACD:
            maxMACD = bot.data[coinpair].macd[index - i]
        if bot.data[coinpair].candles[index - i].close < minPrice:
            minPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] < minMACD:
            minMACD = bot.data[coinpair].macd[index - i]
    '''if bot.data[coinpair].candles[index - 1].close / minPrice > 1.025:
        bot.plot_sell_triggers.append({'color': 'red', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3
        bot.sell(position)
        return'''

    if bot.data[coinpair].macd[index - 1] < 0: return
    if bot.data[coinpair].macd[index - 1] - bot.data[coinpair].macd[index - 2] > bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 3]: return
    if bot.data[coinpair].candles[index - 1].close < ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return

    if bot.data[coinpair].candles[index - 1].close > bot.data[coinpair].upperband[index - 1]:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[0] += utilities.TRIGGER_0
        bot.sell(position)
        return
    if bot.data[coinpair].macd[index - 2] > 0 and bot.data[coinpair].macd[index - 1] < 0:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[1] += utilities.TRIGGER_1
        bot.sell(position)
        return

    if bot.data[coinpair].macd[index - 1] > 0 and bot.data[coinpair].macd[index - 1] == maxMACD:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[2] += utilities.TRIGGER_2
        bot.sell(position)
        return
    if bot.data[coinpair].candles[index - 1].close == maxPrice:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3
        bot.sell(position)
        return

    if position.result >= 1.03:
        bot.sell(position)
        return

    return
    if sum(bot.sell_triggers) >= utilities.TRIGGER_THRESHOLD:
        bot.sell(position)
        status = 'sell'

    for index, strat in enumerate(bot.sell_triggers):
        bot.sell_triggers[index] -= utilities.TRIGGER_DECAY
        if bot.sell_triggers[index] < 0.0: bot.sell_triggers[index] = 0.0

    return

    if bot.data[position.coinpair].macd[index - 1] > bot.data[position.coinpair].macd[index - 2] and bot.data[position.coinpair].macd[index - 2] > 0.0:
        status = 'hold'
    elif bot.data[position.coinpair].macdDiff[index - 1] > bot.data[position.coinpair].macdDiff[index - 2] and bot.data[position.coinpair].macdDiff[index - 2] > 0.0:
        status = 'hold'
    else:
        status = ''

    sell = False
    if position.stopLoss: sell = True
    elif position.age > 9e5 and position.result < utilities.DROP: sell = True
    elif status == 'sell': sell = True

    if sell: bot.sell(position)
