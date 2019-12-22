from util.decor import main
import trading_models.alpha as model


@main(name='analyze')
def run(logger, config):
    model.analyze(
        logger=logger,
        config=config,
        data=None
    )


if __name__ == '__main__':
    run()
