import plotly.graph_objs as go
import plotly.offline as py
from plotly import tools

from components.Candle import Candle
import utilities, argparse, pandas

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Used for Plotting Backtesting Results')
    parser.add_argument('-c', '--coinpair', help='coinpair used in backtesting', type=str, action='append', dest='coinpair', required=True)
    args = parser.parse_args()

    try:
        data = pandas.read_csv('data/history/' + args.coinpair[0] + '.csv')
    except:
        utilities.throw_error('Failed to Import Historical Data for Coinpair \'' + args.coinpair[0] + '\'', True)

    candles = []
    for index, candle in data.iterrows():
        candles.append(Candle(candle['Open Time'], candle['Open'], candle['High'], candle['Low'], candle['Close'], candle['Close Time'], candle['Number Trades'], candle['Volume']))
    candles = candles[:-1]

    trace_candlestick = go.Candlestick(
        name='Candle Data',
        x=[utilities.to_datetime(candle.openTime) for candle in candles if candle.openTime > utilities.BACKTEST_START_DATE],
        open=[candle.open for candle in candles if candle.openTime > utilities.BACKTEST_START_DATE],
        high=[candle.high for candle in candles if candle.openTime > utilities.BACKTEST_START_DATE],
        low=[candle.low for candle in candles if candle.openTime > utilities.BACKTEST_START_DATE],
        close=[candle.close for candle in candles if candle.openTime > utilities.BACKTEST_START_DATE])

    try:
        data = pandas.read_csv('data/backtesting/' + args.coinpair[0] + '.csv')
    except:
        utilities.throw_error('Failed to Import Backtesting Results for Coinpair \'' + args.coinpair[0] + '\'', True)

    trace_results_buy = go.Scatter(
        name='Buy Marker',
        x=[utilities.to_datetime(row['time']) for index, row in data.iterrows() if row['used'] == 1],
        y=[row['price'] for index, row in data.iterrows() if row['used'] == 1],
        mode='markers',
        marker=dict(size=9, color=['blue' for index, row in data.iterrows() if row['used'] == 1]),
        text=[utilities.to_datetime(row['time']) for index, row in data.iterrows() if row['used'] == 1])

    trace_results_sell = go.Scatter(
        name='Sell Marker',
        x=[utilities.to_datetime(row['end']) for index, row in data.iterrows() if row['used'] == 1],
        y=[row['current'] for index, row in data.iterrows() if row['used'] == 1],
        mode='markers',
        marker=dict(size=9, color=['purple' for index, row in data.iterrows() if row['used'] == 1]),
        text=[utilities.to_datetime(row['end']) for index, row in data.iterrows() if row['used'] == 1])

    trace_results_buy_other = go.Scatter(
        name='Other Buy Marker',
        x=[utilities.to_datetime(row['time']) for index, row in data.iterrows() if row['used'] == 0],
        y=[row['price'] for index, row in data.iterrows() if row['used'] == 0],
        mode='markers',
        marker=dict(size=9, color=['green' for index, row in data.iterrows() if row['used'] == 0]),
        text=[utilities.to_datetime(row['time']) for index, row in data.iterrows() if row['used'] == 0])

    trace_results_sell_other = go.Scatter(
        name='Other Sell Marker',
        x=[utilities.to_datetime(row['end']) for index, row in data.iterrows() if row['used'] == 0],
        y=[row['current'] for index, row in data.iterrows() if row['used'] == 0],
        mode='markers',
        marker=dict(size=9, color=['orange' for index, row in data.iterrows() if row['used'] == 0]),
        text=[utilities.to_datetime(row['end']) for index, row in data.iterrows() if row['used'] == 0])

    results = []
    for index, row in data.iterrows():
        if row['used'] == 0: continue
        if len(results) == 0: results.append(row['current'] / row['price'])
        else: results.append(results[-1] * row['current'] / row['price'])
    trace_total = go.Scatter(name='Total Value', x=[utilities.to_datetime(row['end']) for index, row in data.iterrows()], y=[val for val in results])

    updatemenus = list([
        dict(
            active=0,
            buttons=list([
                dict(label='All Markers', method='update', args=[{
                    'visible': [True, True, True, True, True]
                }, {
                    'title': 'All Markers for Coinpair \'' + args.coinpair[0] + '\''
                }]),
                dict(label='Used Markers', method='update', args=[{
                    'visible': [True, True, True, False, False]
                }, {
                    'title': 'Used Markers for Coinpair \'' + args.coinpair[0] + '\''
                }]),
                dict(label='Other Markers', method='update', args=[{
                    'visible': [True, False, False, True, True]
                }, {
                    'title': 'Other Markers for Coinpair \'' + args.coinpair[0] + '\''
                }])
            ]),
        )
    ])

    fig = tools.make_subplots(rows=2, cols=1, specs=[[{}], [{}]], shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.001)

    fig.append_trace(trace_candlestick, 1, 1)
    fig.append_trace(trace_results_buy, 1, 1)
    fig.append_trace(trace_results_sell, 1, 1)
    fig.append_trace(trace_results_buy_other, 1, 1)
    fig.append_trace(trace_results_sell_other, 1, 1)

    fig.append_trace(trace_total, 2, 1)

    fig['layout'].update(title='Backtesting Results for Coinpair \'' + args.coinpair[0] + '\'', updatemenus=updatemenus, showlegend=False, xaxis=dict(title='Date', rangeslider=dict(visible=False)))
    py.plot(fig, filename='data/plots/' + args.coinpair[0] + '.html')
