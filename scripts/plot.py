import sys, os, argparse, pandas
import plotly.graph_objs as go
import plotly.offline as py
from plotly import tools
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.path.join(os.getcwd(), 'binance-bot'), 'scripts'))
import utilities, helpers

logger = helpers.create_logger('plot')


def fun(**args):
    data = helpers.safe_read_file(logger, 'data/history/' + args['extra']['coinpair'] + '.csv')
    if data is None: return 1

    logger.info('Tracing Candlestick Data...')
    trace_candlestick = go.Candlestick(
        name='Candle Data',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        open=[row['OPEN'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        high=[row['HIGH'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        low=[row['LOW'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        close=[row['CLOSE'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])

    logger.info('Tracing Bollinger Data...')
    trace_upperband = go.Scatter(
        name='Bollinger Upper',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        y=[row['UPPERBAND'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])
    trace_lowerband = go.Scatter(
        name='Bollinger Lower',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        y=[row['LOWERBAND'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])

    logger.info('Tracing RSI Data...')
    trace_rsi = go.Scatter(
        name='RSI',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        y=[row['RSI'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])
    trace_rsi_70 = go.Scatter(
        name='RSI-70',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        y=[70.0 for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])
    trace_rsi_20 = go.Scatter(
        name='RSI-20',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        y=[20.0 for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])

    logger.info('Tracing MACD_DIFF Data...')
    trace_macd_diff = go.Scatter(
        name='MACD_DIFF',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        y=[row['MACD_DIFF'] for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])
    trace_macd_diff_0 = go.Scatter(
        name='MACD_DIFF-0',
        x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE],
        y=[0.0 for index, row in data.iterrows() if row['OPEN_TIME'] > utilities.BACKTEST_START_DATE])

    logger.info('Creating Figure...')
    fig = tools.make_subplots(rows=3, cols=1, specs=[[{}], [{}], [{}]], shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.001)

    fig.append_trace(trace_candlestick, 1, 1)
    fig.append_trace(trace_upperband, 1, 1)
    fig.append_trace(trace_lowerband, 1, 1)

    fig.append_trace(trace_rsi, 2, 1)
    fig.append_trace(trace_rsi_70, 2, 1)
    fig.append_trace(trace_rsi_20, 2, 1)

    fig.append_trace(trace_macd_diff, 3, 1)
    fig.append_trace(trace_macd_diff_0, 3, 1)

    fig['layout'].update(title='Plot for \'' + args['extra']['coinpair'] + '\'', showlegend=False, xaxis=dict(title='Date', rangeslider=dict(visible=False)))
    py.plot(fig, filename=os.path.dirname(__file__) + '/../data/plots/' + args['extra']['coinpair'] + '.html')

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Plotting Data')
    parser.add_argument('-c', '--coinpair', help='coinpair to plot', type=str, dest='coinpair', required=False)
    args = parser.parse_args()

    helpers.main_function(logger, 'Plotting Data', fun, extra={'coinpair': args.coinpair})
