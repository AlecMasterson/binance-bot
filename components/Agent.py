import sys, os, collections, pandas, argparse
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import utilities, helpers, signals, Backtest, Plot


class Agent:

    data, windows = {}, {}

    def __init__(self, plot=False):
        self.plot = plot
        self.backtest = Backtest.Backtest()

    def set_data(self, coinpairs):
        self.coinpairs = coinpairs
        for coinpair in self.coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            temp_data = Backtest.format_data(temp_data, utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.BACKTEST_CANDLE_INTERVAL, 24)
            if temp_data is None: return False

            self.data[coinpair] = temp_data
            self.windows[coinpair] = collections.deque(maxlen=utilities.WINDOW_SIZE)

        self.backtest.set_data(self.data)
        return True

    def run(self):
        state, reward, isDone, info = self.backtest.reset(utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.STARTING_BALANCE, utilities.BACKTEST_CANDLE_INTERVAL, utilities.MAX_POSITIONS)
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

            for position in [position for position in info['FINAL_POSITIONS'] if position.data['COINPAIR'] == key]:
                plotting.add_position(position.data)
            plotting.add_figure_positions()

            plotting.plot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Testing an Agent')
    parser.add_argument('-c', '--coinpairs', help='a list of coinpairs to backtest', type=str, nargs='+', dest='coinpairs', required=True)
    parser.add_argument('-p', '--plot', help='used if you want to plot the results', action='store_true', required=False)
    args = parser.parse_args()

    agent = Agent(plot=args.plot)
    if agent.set_data(args.coinpairs): agent.run()
