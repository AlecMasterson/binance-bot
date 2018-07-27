import utilities, argparse, os

if __name__ == '__main__':
    argparse.ArgumentParser(description='Main Script Used for the Binance Bot').parse_args()

    # TODO: Keep a counter of failed script attempts.
    # TODO: Setup email notifications if counter is > N.
    while True:
        result = os.system('python scripts/orders.py')
        result = os.system('python scripts/positions.py')
        result = os.system('python scripts/balances.py')
