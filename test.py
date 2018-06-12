import plotly.graph_objs as go
import plotly.offline as py
from plotly import tools

from components.Coinpair import Coinpair

import pandas, sys


def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


def slope(x1, x2, y1, y2):
    return (y2 - y1) / (x2 - x1)


coinpair = Coinpair(None, 'BNBBTC', False)

markers = []
best_buys = []
test_buys = []
localInfo = [{'marker': None, 'value': 0}, {'marker': None, 'value': 0}]

window = 120

slopes = []
top_slopes = []
aboveZero = False
belowZero = False
for index, candle in enumerate(coinpair.candles):
    if index == 0: continue

    if coinpair.macdDiff[index - 1] > 0:
        if localInfo[0]['value'] != 0 and localInfo[0]['marker'] != None:
            #markers.append(localInfo[0]['marker'])
            best_buys.append(localInfo[0]['marker']['time'])
        localInfo[0]['value'] = 0
        aboveZero = True
    elif coinpair.macdDiff[index - 1] < 0:
        #if localInfo[1]['value'] != 0 and localInfo[1]['marker'] != None: markers.append(localInfo[1]['marker'])
        localInfo[1]['value'] = 0
        belowZero = True

    if coinpair.macdDiff[index - 1] > localInfo[1]['value']:
        localInfo[1]['value'] = coinpair.macdDiff[index - 1]
        localInfo[1]['marker'] = {'color': 'blue', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close}
    elif coinpair.macdDiff[index - 1] < localInfo[0]['value']:
        localInfo[0]['value'] = coinpair.macdDiff[index - 1]
        localInfo[0]['marker'] = {'color': 'blue', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close}

    if index < window: continue
    minimum = min(coinpair.macdDiff[index - window:index])

    valid = False
    alsoValid = False

    # -2.7e-6
    macdSlope = slope(1, 2, coinpair.macd[index - 2], coinpair.macd[index - 1])
    signalSlope = slope(1, 2, coinpair.macdSignal[index - 2], coinpair.macdSignal[index - 1])
    if aboveZero and coinpair.macdDiff[index - 1] < minimum * 0.6 and coinpair.macdDiff[index - 2] < coinpair.macdDiff[index - 3]:
        if coinpair.macd[index - 1] > coinpair.macdSignal[index - 1]:
            if macdSlope > signalSlope: slopes.append(macdSlope - signalSlope)
            else: valid = True
        elif coinpair.macd[index - 1] < coinpair.macdSignal[index - 1]:
            if macdSlope < signalSlope: slopes.append(signalSlope - macdSlope)
            else: valid = True
        if len(slopes) > 1 and slopes[-1] - (slopes[-2] - slopes[-1]) < 0:
            valid = True
    if aboveZero and coinpair.macdDiff[index - 1] < -2.9e-6 and coinpair.macdDiff[index - 2] < coinpair.macdDiff[index - 3]:
        if coinpair.macd[index - 1] > coinpair.macdSignal[index - 1]:
            if macdSlope > signalSlope: slopes.append(macdSlope - signalSlope)
            else: alsoValid = True
        elif coinpair.macd[index - 1] < coinpair.macdSignal[index - 1]:
            if macdSlope < signalSlope: slopes.append(signalSlope - macdSlope)
            else: alsoValid = True
        if len(slopes) > 1 and slopes[-1] - (slopes[-2] - slopes[-1]) < 0:
            alsoValid = True
    '''
    # TODO: Try numTrades as a method of finding buy/sell points
    if coinpair.candles[index - 1].close < coinpair.lowerband[index - 1] and coinpair.candles[index - 1].numTrades > 300:
        andValid = True
    '''

    if (valid or alsoValid) and coinpair.candles[index - 1].close < ((coinpair.upperband[index - 1] - coinpair.lowerband[index - 1]) / 2) + coinpair.lowerband[index - 1]:
        if valid: markers.append({'color': 'black', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close})
        elif alsoValid: markers.append({'color': 'purple', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close})
        test_buys.append(coinpair.candles[index - 1].closeTime)
        slopes = []
        aboveZero = False
    '''
    valid = False
    alsoValid = False

    if belowZero and coinpair.macdDiff[index - 1] > 2.9e-6 and coinpair.macdDiff[index - 2] > coinpair.macdDiff[index - 3]:
        if coinpair.macd[index - 1] > coinpair.macdSignal[index - 1]:
            if macdSlope > signalSlope: top_slopes.append(macdSlope - signalSlope)
            else: valid = True
        elif coinpair.macd[index - 1] < coinpair.macdSignal[index - 1]:
            if macdSlope < signalSlope: top_slopes.append(signalSlope - macdSlope)
            else: valid = True
        if len(top_slopes) > 1 and top_slopes[-1] - (top_slopes[-2] - top_slopes[-1]) < 0:
            alsoValid = True

    if (valid or alsoValid) and coinpair.candles[index - 1].close > ((coinpair.upperband[index - 1] - coinpair.lowerband[index - 1]) / 2) + coinpair.lowerband[index - 1]:
        print(to_datetime(coinpair.candles[index].openTime))
        if valid: markers.append({'color': 'blue', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close})
        elif alsoValid: markers.append({'color': 'blue', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close})
        top_slopes = []
        belowZero = False
    '''

count = 0
for time in best_buys:
    if time in test_buys: count += 1
print('Perfect Buy Percentage: ' + str(count / len(best_buys)))

# ----------------------------------------
# TRACES
# ----------------------------------------

trace_candlestick = go.Candlestick(
    name='Candle Data',
    x=[to_datetime(candle.openTime) for candle in coinpair.candles],
    open=[candle.open for candle in coinpair.candles],
    high=[candle.high for candle in coinpair.candles],
    low=[candle.low for candle in coinpair.candles],
    close=[candle.close for candle in coinpair.candles])

trace_bollinger_upper = go.Scatter(name='Upper Bollinger Band', x=[to_datetime(candle.closeTime) for candle in coinpair.candles], y=[upperband for upperband in coinpair.upperband])
trace_bollinger_lower = go.Scatter(name='Lower Bollinger Band', x=[to_datetime(candle.closeTime) for candle in coinpair.candles], y=[lowerband for lowerband in coinpair.lowerband])

trace_markers = go.Scatter(
    name='Marker', x=[to_datetime(point['time']) for point in markers], y=[point['price'] for point in markers], mode='markers', marker=dict(size=9, color=[point['color'] for point in markers]))

trace_num_trades = go.Scatter(
    name='Num Trades',
    x=[to_datetime(candle.openTime) for candle in coinpair.candles],
    y=[candle.numTrades for candle in coinpair.candles],
    line=dict(color='blue'),
    text=[str(candle.numTrades) for candle in coinpair.candles])

trace_macd = go.Scatter(
    name='MACD', x=[to_datetime(candle.openTime) for candle in coinpair.candles], y=[macd for macd in coinpair.macd], line=dict(color='blue'), text=[str(macd) for macd in coinpair.macd])
trace_macd_diff = go.Scatter(
    name='MACD Diff',
    x=[to_datetime(candle.openTime) for candle in coinpair.candles],
    y=[macdDiff for macdDiff in coinpair.macdDiff],
    line=dict(color='black'),
    text=[str(macdDiff) for macdDiff in coinpair.macdDiff])
trace_macd_signal = go.Scatter(
    name='MACD Signal',
    x=[to_datetime(candle.openTime) for candle in coinpair.candles],
    y=[macdSignal for macdSignal in coinpair.macdSignal],
    line=dict(color='red'),
    text=[str(macdSignal) for macdSignal in coinpair.macdSignal])

fig = tools.make_subplots(rows=3, cols=1, specs=[[{}], [{}], [{}]], shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.001)

fig.append_trace(trace_num_trades, 3, 1)
fig.append_trace(trace_candlestick, 2, 1)
fig.append_trace(trace_bollinger_upper, 2, 1)
fig.append_trace(trace_bollinger_lower, 2, 1)
fig.append_trace(trace_markers, 2, 1)
fig.append_trace(trace_macd, 1, 1)
fig.append_trace(trace_macd_diff, 1, 1)
fig.append_trace(trace_macd_signal, 1, 1)

fig['layout'].update(showlegend=False, xaxis=dict(rangeslider=dict(visible=False)))
py.plot(fig, filename='plot2.html')
