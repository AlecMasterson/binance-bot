import os, pandas, plotly
import plotly.graph_objs as go
import plotly.offline as py


class Plot:

    def __init__(self, data=None):
        self.figures, self.positions = [], []
        if not data is None: self.set_data(data)

    def set_data(self, data):
        self.data = data

        self.figures.append({'row': 1, 'fig': go.Candlestick(name='Candle Data', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in data.iterrows()], open=[row['OPEN'] for index, row in data.iterrows()], high=[row['HIGH'] for index, row in data.iterrows()], low=[row['LOW'] for index, row in data.iterrows()], close=[row['CLOSE'] for index, row in data.iterrows()])})

    def add_figure_bollinger(self):
        self.figures.append({'row': 1, 'fig': go.Scatter(name='Bollinger Upper', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[row['UPPERBAND'] for index, row in self.data.iterrows()])})
        self.figures.append({'row': 1, 'fig': go.Scatter(name='Bollinger Lower', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[row['LOWERBAND'] for index, row in self.data.iterrows()])})

    def add_figure_macd_diff(self):
        num_rows = max(figure['row'] for figure in self.figures)
        self.figures.append({'row': num_rows + 1, 'fig': go.Scatter(name='MACD_DIFF', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[row['MACD_DIFF'] for index, row in self.data.iterrows()])})
        self.figures.append({'row': num_rows + 1, 'fig': go.Scatter(name='MACD_DIFF-0', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[0.0 for index, row in self.data.iterrows()])})

    def add_figure_rsi(self):
        num_rows = max(figure['row'] for figure in self.figures)
        self.figures.append({'row': num_rows + 1, 'fig': go.Scatter(name='RSI', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[row['RSI'] for index, row in self.data.iterrows()])})
        self.figures.append({'row': num_rows + 1, 'fig': go.Scatter(name='RSI-80', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[80.0 for index, row in self.data.iterrows()])})
        self.figures.append({'row': num_rows + 1, 'fig': go.Scatter(name='RSI-20', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[20.0 for index, row in self.data.iterrows()])})

    def add_figure_future_potential(self):
        num_rows = max(figure['row'] for figure in self.figures)
        self.figures.append({'row': num_rows + 1, 'fig': go.Scatter(name='Future-Potential', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[row['FUTURE_POTENTIAL'] for index, row in self.data.iterrows()])})
        self.figures.append({'row': num_rows + 1, 'fig': go.Scatter(name='Future-Potential-1.0', x=[pandas.to_datetime(row['OPEN_TIME'], unit='ms') for index, row in self.data.iterrows()], y=[1.0 for index, row in self.data.iterrows()])})

    def add_position(self, position):
        self.positions.append(position)

    def add_figure_positions(self):
        self.figures.append({'row': 1, 'fig': go.Scatter(name='Buy Marker', mode='markers', marker=dict(size=9), x=[pandas.to_datetime(position['TIME_BUY'], unit='ms') for position in self.positions], y=[position['PRICE_BUY'] for position in self.positions])})
        self.figures.append({'row': 1, 'fig': go.Scatter(name='Sell Marker', mode='markers', marker=dict(size=9), x=[pandas.to_datetime(position['TIME_SELL'], unit='ms') for position in self.positions], y=[position['PRICE_SELL'] for position in self.positions])})

    def plot(self):
        num_rows = max(figure['row'] for figure in self.figures)
        fig = plotly.tools.make_subplots(rows=num_rows, cols=1, specs=[[{}] for i in range(num_rows)], shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.01)
        for figure in self.figures:
            fig.append_trace(figure['fig'], figure['row'], 1)

        fig['layout'].update(title='Plot', showlegend=False, xaxis=dict(title='Date', rangeslider=dict(visible=False)))
        py.plot(fig, filename=os.getcwd() + '/data/plots/plot.html')
