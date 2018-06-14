import plotly.graph_objs as go
import plotly.offline as py
from plotly import tools

from components.Candle import Candle
import utilities, argparse, pandas


def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Used for Plotting Backtesting Results')
    parser.add_argument('-c', '--coinpair', help='coinpair used in backtesting', type=str, action='append', dest='coinpair', required=True)
    args = parser.parse_args()

    try:
        data = pandas.read_csv('data/history/' + args.coinpair[0] + '.csv')
    except:
        utilities.throw_error('Failed to Retrieve Historical Data', True)

    candles = []
    for index, candle in data.iterrows():
        candles.append(
            Candle(
                int(candle['Open Time']), float(candle['Open']), float(candle['High']), float(candle['Low']), float(candle['Close']), int(candle['Close Time']), int(candle['Number Trades']),
                float(candle['Volume'])))
    candles = candles[:-1]

    trace_candlestick = go.Candlestick(
        name='Candle Data',
        x=[to_datetime(candle.openTime) for candle in candles],
        open=[candle.open for candle in candles],
        high=[candle.high for candle in candles],
        low=[candle.low for candle in candles],
        close=[candle.close for candle in candles])

    try:
        data = pandas.read_csv('data/backtesting/' + args.coinpair[0] + '.csv')
    except:
        utilities.throw_error('Failed to Retrieve Backtesting Data', True)

    trace_results_buy = go.Scatter(
        name='Buy Marker',
        x=[to_datetime(row['startTime']) for index, row in data.iterrows()],
        y=[row['startPrice'] for index, row in data.iterrows()],
        mode='markers',
        marker=dict(size=9, color=['blue' for index, row in data.iterrows()]),
        text=[to_datetime(row['startTime']) for index, row in data.iterrows()])

    trace_total = go.Scatter(name='Total Value', x=[to_datetime(row['startTime']) for index, row in data.iterrows()], y=[1.0 for index, row in data.iterrows()], color='black')

    fig = tools.make_subplots(rows=2, cols=1, specs=[[{}], [{}]], shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.001)

    fig.append_trace(trace_candlestick, 1, 1)
    fig.append_trace(trace_results_buy, 1, 1)
    fig.append_trace(trace_total, 2, 1)

    fig['layout'].update(title='Backtesting Results for ' + args.coinpair[0], showlegend=False, xaxis=dict(title='Date', rangeslider=dict(visible=False)))
    py.plot(fig, filename='plot.html')
