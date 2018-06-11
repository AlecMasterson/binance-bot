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

mins = []
maxs = []
markers = []
localsMACD = [0, 0]
marker_locals = [None, None]
aboveZero = False
for index, candle in enumerate(coinpair.candles):
    if index < 3: continue

    if coinpair.macdDiff[index - 1] > 0:
        if localsMACD[0] != 0 and marker_locals[0] != None: markers.append(marker_locals[0])
        mins.append(localsMACD[0])
        localsMACD[0] = 0
        aboveZero = True
    elif coinpair.macdDiff[index - 1] < 0:
        if localsMACD[1] != 0 and marker_locals[1] != None: markers.append(marker_locals[1])
        maxs.append(localsMACD[1])
        localsMACD[1] = 0

    if coinpair.macdDiff[index - 1] > localsMACD[1]:
        localsMACD[1] = coinpair.macdDiff[index - 1]
        marker_locals[1] = {'color': 'blue', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close}
    elif coinpair.macdDiff[index - 1] < localsMACD[0]:
        localsMACD[0] = coinpair.macdDiff[index - 1]
        marker_locals[0] = {'color': 'purple', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close}

    valid = False

    # TODO: Attempt to predict if their slopes point to each other by seeing how close they are together.
    macdSlope = slope(1, 2, coinpair.macd[index - 2], coinpair.macd[index - 1])
    signalSlope = slope(1, 2, coinpair.macdSignal[index - 2], coinpair.macdSignal[index - 1])
    if aboveZero and coinpair.macdDiff[index - 1] < 0:
        if macdSlope < signalSlope and coinpair.macd[index - 1] > coinpair.macdSignal[index - 1]:
            valid = True
            aboveZero = False
        elif macdSlope > signalSlope and coinpair.macd[index - 1] < coinpair.macdSignal[index - 1]:
            valid = True
            aboveZero = False

    if coinpair.macd[index - 3] < 0 and coinpair.macdDiff[index - 3] < 0 and coinpair.macd[index - 1] < 0 and coinpair.macdDiff[index - 1] < 0:
        if coinpair.macdDiff[index - 2] < coinpair.macdDiff[index - 3]:
            if coinpair.macdDiff[index - 1] > coinpair.macdDiff[index - 2] and coinpair.macdDiff[index - 1] < localsMACD[0] * 0.6:
                print()
            elif coinpair.macdDiff[index - 1] < localsMACD[0] * 0.85:
                print()

    if valid and coinpair.candles[index - 1].close < ((coinpair.upperband[index - 1] - coinpair.lowerband[index - 1]) / 2) + coinpair.lowerband[index - 1]:
        markers.append({'color': 'black', 'time': coinpair.candles[index - 1].closeTime, 'price': coinpair.candles[index - 1].close})

print('Max Min: ' + str(max(mins)))
print('Average Min: ' + str(sum(mins) / len(mins)) + '\n')
print('Min Max: ' + str(min(maxs)))
print('Average Max: ' + str(sum(maxs) / len(maxs)))

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
