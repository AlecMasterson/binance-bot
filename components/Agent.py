import sys, os, collections, pandas, argparse
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import utilities, helpers, signals, Backtest, Plot


class Agent:

    data, windows = {}, {}

    def __init__(self, coinpairs, plot):
        self.coinpairs, self.plot = coinpairs, plot

        for coinpair in self.coinpairs:
            self.data[coinpair] = helpers.read_file('data/history/' + coinpair + '.csv')
            self.windows[coinpair] = collections.deque(maxlen=utilities.WINDOW_SIZE)

        self.backtest = Backtest.Backtest(self.data, utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.BACKTEST_CANDLE_INTERVAL, utilities.STARTING_BALANCE, utilities.MAX_POSITIONS, 24)

    def run(self):
        state, reward, isDone, info = self.backtest.reset()
        while not isDone:
            action = self.act(state)
            state, reward, isDone, info = self.backtest.step(action)
        print('Final Balance: {}\nPotential Reward: {}\n'.format(reward['BALANCE'], reward['POTENTIAL']))

        if self.plot: self.plotting(info)

    def act(self, state):
        action = {}
        for key in state:
            self.windows[key].append(state[key])
            if len(self.windows[key]) != utilities.WINDOW_SIZE: action[key] = False
            elif self.brain(self.windows[key]): action[key] = True
            else: action[key] = False
        return action

    def brain(self, data):
        return signals.cheating(data)

    def plotting(self, info):
        for key in self.data:
            plotting = Plot.Plot(key, self.data[key])
            plotting.add_figure_future_potential()
            plotting.add_figure_rsi()
            plotting.add_figure_macd_diff()

            for position in [position for position in info['FINAL_POSITIONS'] if position.data['COINPAIR'] == key]:
                plotting.add_position(position.data)
            plotting.add_figure_positions()

            plotting.plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Testing an Agent')
    parser.add_argument('-c', '--coinpairs', help='a list of coinpairs to backtest', type=str, nargs='+', dest='coinpairs', required=True)
    parser.add_argument('-p', '--plot', help='used if you want to plot the results', action='store_true', required=False)
    args = parser.parse_args()

    agent = Agent(args.coinpairs, args.plot)
    agent.run()
