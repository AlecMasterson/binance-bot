import pandas, glob, numpy

if __name__ == "__main__":
    combined = []
    for file in glob.glob('data/*.csv'):
        data = pandas.read_csv(file)
        coinPair = file.split('/')[1].split('.')[0]
        if coinPair == 'ALL': continue

        data.set_index('Open Time', inplace=True)
        data = data.drop(columns=['Volume', 'Quote Asset Volume', 'Number Trades', 'Taker Base Asset Volume', 'Take Quote Asset Volume', 'Ignore'])
        data = data.rename(columns={'Open': 'open-' + coinPair, 'High': 'high-' + coinPair, 'Low': 'low-' + coinPair, 'Close': 'close-' + coinPair, 'Close Time': 'cTime-' + coinPair})
        combined.append(data)
    for i in range(len(combined)):
        if i == 0: continue
        combined[0] = pandas.merge(combined[0], combined[i], left_index=True, right_index=True, how='outer')

    combined[0] = combined[0].replace(numpy.nan, numpy.nan).ffill()

    combined[0].to_csv('data/ALL.csv')
