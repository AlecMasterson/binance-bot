from util.decor import main
from models.History import History
import models.History
import models.Symbol
import util.binance
import util.db
import util.util
import argparse
import datetime
import os


@main(name='download_history')
def download(upload, *, logger):
    projectPath = os.environ['PROJECT_PATH']
    logger.info('Project Path = {}'.format(projectPath))

    client = util.binance.binance_connect(logger=logger)
    db = util.db.db_connect(logger=logger)
    config = util.util.load_config(logger=logger)

    intervals = config['symbol_data']['intervals']
    originalStartDate = config['symbol_data']['start_date']
    logger.info('Config Attributes Loaded:\n\tIntervals = {}\n\tStartDate = {}'.format(intervals, originalStartDate))

    symbols = models.Symbol.get_active(db=db)
    logger.info('Active Symbols Found = {}'.format(len(symbols)))

    logger.info('Downloading Historical Data...')
    for symbol in symbols:
        for interval in intervals:
            logPrefix = '(Symbol,Interval) - ({},{}) - '.format(symbol, interval)

            try:
                startDate = originalStartDate
                intervalTimeDelta = datetime.timedelta(hours=int(interval.split('h')[0]))

                mostRecent = models.History.get_recent_by_interval(db=db, symbol=symbol, interval=interval, length=1)
                mostRecentCloseTime = mostRecent['closeTime'][0] if len(mostRecent) > 0 else None
                logger.info('{}Most Recent Entry = \'{}\''.format(logPrefix, mostRecentCloseTime if mostRecentCloseTime is not None else 'N/A'))

                if mostRecentCloseTime is not None:
                    startDate = max(startDate, mostRecentCloseTime - (intervalTimeDelta * 16))
                logger.info('{}Updating From \'{}\''.format(logPrefix, startDate))

                data = util.binance.get_historical_data(
                    logger=logger,
                    client=client,
                    symbol=symbol,
                    interval=interval,
                    startDate=startDate.strftime('%Y-%m-%d %H:%M:%S')
                )

                logger.info('{}Downloaded Data Info:\n\tData Length = {}\n\tStart DateTime = \'{}\'\n\tEnd DateTime = \'{}\''.format(
                    logPrefix,
                    len(data), data['open_time'].iloc[0], data['close_time'].iloc[-1]
                ))

                outputPath = util.util.get_file_path(
                    create=True,
                    directoryTree=(projectPath, 'data', 'history', symbol),
                    fileName='{}.csv'.format(interval)
                )
                data.to_csv(outputPath, index=False)
                logger.info('{}Saved to CSV at Location: {}'.format(logPrefix, outputPath))

                if upload:
                    for item in [History(row) for row in data.to_dict(orient='records')]:
                        if not models.History.exists(db=db, symbol=symbol, interval=interval, openTime=item.openTime):
                            db.add(item)
                    db.commit()
            except Exception as e:
                logger.exception('{}Unexpected Error:\n{}'.format(logPrefix, e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading Historical Data from the Binance Exchange')
    parser.add_argument('-u', '--upload', help='include if uploading data to the DB', action='store_true', dest='UPLOAD', required=False)
    args = parser.parse_args()

    download(args.UPLOAD)
