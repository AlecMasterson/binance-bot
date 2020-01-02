from util.decor import main
from models.History import History
import util.binance
import util.db
import util.util
import argparse
import collections
import datetime
import numpy
import os
import pandas


@main(name='download_history')
def download(symbols, upload, *, logger):
    client = util.binance.binance_connect(logger=logger)
    db = util.db.db_connect(logger=logger)
    config = util.util.get_config(logger=logger)

    intervals = config['symbol_data']['intervals']
    originalStartDate = datetime.datetime.strptime(config['symbol_data']['start_date'], '%Y-%m-%d %H:%M:%S')
    logger.info('Config Attributes Loaded:\n\tIntervals = {}\n\tStartDate = {}'.format(intervals, originalStartDate))

    logger.info('Downloading Historical Data for {} Symbol(s)...'.format(len(symbols)))
    for symbol in symbols:
        for interval in intervals:
            logPrefix = '(Symbol,Interval) - ({},{}) - '.format(symbol, interval)

            try:
                startDate = originalStartDate
                intervalTimeDelta = datetime.timedelta(hours=int(interval.split('h')[0]))

                # BB will download history from the latest candle minus (32 * <interval>).
                # First, determine if there is any existing data.
                mostRecent = db.query(History).filter(
                    History.symbol == symbol
                ).filter(
                    History.width == interval
                ).order_by(History.open_time.desc()).first()
                logger.info('{}Most Recent Entry = \'{}\''.format(logPrefix, mostRecent.open_time if mostRecent is not None else 'N/A'))

                # If there's existing data in the DB, set the startDate accordingly (mentioned above).
                if mostRecent is not None:
                    startDate = max(startDate, mostRecent.close_time - (intervalTimeDelta * 32))
                logger.info('{}Updating From \'{}\''.format(logPrefix, startDate))

                # Actually download the historical data from the Binance Exchange.
                # The util function automatically formats the data as necessary.
                data = util.util.get_historical_data(
                    logger=logger,
                    client=client,
                    symbol=symbol,
                    interval=interval,
                    startDate=startDate.strftime('%Y-%m-%d %H:%M:%S')
                )

                # Create a validation array to compare the resulting historical data against.
                # The data downloaded should include (no extra values) all entries in this array.
                expectedOpenTimes = numpy.arange(
                    startDate,
                    datetime.datetime.utcnow() - intervalTimeDelta,
                    intervalTimeDelta
                ).astype(pandas.Timestamp)

                # If the downloaded data doesn't match the expected array above, attempt to fix it.
                # This block simply interpolates any holes in the timeline.
                # However, it does NOT interpolate the tail (most recent) candles.
                if collections.Counter(data['open_time']) != collections.Counter(expectedOpenTimes):
                    logger.warning('{}Downloaded Data Missing Entries. Attempting to Fix...'.format(logPrefix))

                    data = data.set_index('open_time').reindex(
                        pandas.Index(expectedOpenTimes, name='open_time')
                    ).reset_index().fillna(numpy.nan).interpolate(limit_direction='backward')
                    data['close_time'].fillna(data['open_time'] + intervalTimeDelta, inplace=True)
                    data['symbol'] = symbol
                    data['width'] = interval
                    data.dropna(inplace=True)
                    data = util.db.organize_table_history(data=data)

                # If the downloaded data STILL doesn't match the expected array above, raise an Exception.
                if collections.Counter(data['open_time']) != collections.Counter(expectedOpenTimes):
                    raise Exception('Downloaded Data Missing Entries')

                # Log the finalized data.
                logger.info('{}Downloaded Data Info:\n\tData Length = {}\n\tStart DateTime = \'{}\'\n\tEnd DateTime = \'{}\''.format(
                    logPrefix,
                    len(data),
                    data['open_time'].iloc[0],
                    data['open_time'].iloc[-1]
                ))

                # Export the data to a CSV file for alternative use.
                outputPath = util.util.get_file_path(
                    create=True,
                    directoryTree=('{}/data/history/'.format(os.environ['PROJECT_PATH']), symbol),
                    fileName='{}.csv'.format(interval)
                )
                data.to_csv(outputPath, index=False)
                logger.info('{}Saved to CSV at Location: {}'.format(logPrefix, outputPath))

                # BB will only upload to the DB if the script argument was given.
                if upload:
                    util.db.insert_data(
                        logger=logger,
                        db=db,
                        tableName='history',
                        qualifier='{}_{}'.format(symbol, interval),
                        data=data
                    )
            except Exception as e:
                logger.exception('{}Unexpected Error:\n{}'.format(logPrefix, e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading Historical Data from the Binance Exchange')
    parser.add_argument('-s', '--symbols', help='a list of symbols to download', type=str, nargs='+', dest='SYMBOLS', required=True)
    parser.add_argument('-u', '--upload', help='include if uploading data to the DB', action='store_true', dest='UPLOAD', required=False)
    args = parser.parse_args()

    download(args.SYMBOLS, args.UPLOAD)
