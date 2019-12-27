from util.decor import main
import util.binance
import util.db
import util.util
import argparse
import json
import tqdm


def download(*, logger, config, client, db, symbol, upload):
    for width in config['symbol_data']['widths']:
        data = util.util.get_historical_data(
            logger=logger,
            client=client,
            symbol=symbol,
            interval=width
        )

        if upload:
            util.db.insert_data(
                logger=logger,
                db=db,
                tableName='history',
                qualifier='{}_{}'.format(symbol, width),
                data=data
            )

        data.to_csv(
            util.util.get_file_path(
                create=True,
                directoryTree=('./data/history/', symbol),
                fileName='{}.csv'.format(width)
            ),
            index=False
        )


@main(name='download_history')
def run(symbols, upload, *, logger):
    client = util.binance.binance_connect(logger=logger)
    db = util.db.db_connect(logger=logger)
    config = json.load(open('./scripts/config.json'))

    logger.info('Downloading {} Symbols...'.format(len(symbols)))

    errors = []
    for symbol in tqdm.tqdm(symbols):
        try:
            download(
                logger=logger,
                config=config,
                client=client,
                db=db,
                symbol=symbol,
                upload=upload
            )
        except Exception as e:
            errors.append('{}: {}'.format(symbol, e))

    if len(errors) > 0:
        logger.error('Error(s) Downloading Historical Data for {} Symbol(s):\n{}'.format(len(errors), '\n'.join(errors)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading Historical Data from the Binance Exchange')
    parser.add_argument('-s', '--symbols', help='a list of symbols to download', type=str, nargs='+', dest='SYMBOLS', required=True)
    parser.add_argument('-u', '--upload', help='include if uploading data to the DB', action='store_true', dest='UPLOAD', required=False)
    args = parser.parse_args()

    run(args.SYMBOLS, args.UPLOAD)
