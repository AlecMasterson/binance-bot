# Binance Bot

This bot is used for the automation of trading cryptocurrencies on the Binance Exchange. Currently enabled for trading between ETH and BTC.

The assumption is that you are using a Unix-Based system such as Linux or OSX, but it will work with Windows.

### Requirements

- [Binance Account](https://www.binance.com/register.html) and [API Access](https://www.binance.com/userCenter/createApi.html)
- [Python 3](https://www.python.org/downloads/)
- [Python-Binance API](https://github.com/sammchardy/python-binance)
- [Pandas](https://pandas.pydata.org)

### Installation

The installation guide here will use a package manager, [Pip](https://pip.pypa.io/en/stable/). This is an optional requirement, but very encouraged.

```
apt-get install python3-pip
pip3 install python-binance pandas
```

### Trade Data

Trade Data is created by your unique bot and stored in a CSV file for later analysis. Follow the below Pandas.DataFrame column structure:

**NOTE:** Each row in the DataFrame will represent a trade during backtesting.

| type | time | price | quantity | btc | eth |
| ---- | -----| ----- | -------- | --- | --- |

- Type is either 'buy' or 'sell' to indicate the type of trade
- Time is the time at which a trade occured stored in milliseconds based on the UTC time zone.
- Price is the current price at which the trade occured.
- Quantity is a float (0.0, 1.0] that represents what percent of your existing btc/eth wallet do you wish to buy/sell.
- BTC and ETH represents how much your wallet contains of each coin after the trade occurred.

# Files

### [get_history.py](https://github.com/AlecMasterson/binance-bot/blob/master/get_history.py)
This automated script will obtain historical data from Binance to be used in backtesting. It will obtain data for (currently) five different coin-pairs.

### Usage:
The script can be used in one of two ways, standalone or as an imported function into another script. Below shows the easiest of the two possibilities, as a standalone script:

```
python3 get_history.py
```

If you choose to import the get_history.py functionality into a separate script, you will be calling the **get_data()** function. This requires three arguments:
- Arg1 - The coin-pair you wish to use as a String
- Arg2 - The client object used for the API
- Arg3 - The API associated with the time interval you wish to use

Below shows an example of how this could be done:

```
from binance.client import Client
from get_history import get_data

arg1 = 'ETHBTC'
arg2 = Client('', '')
arg3 = Client.KLINE_INTERVAL_1HOUR

get_data(arg1, arg2, arg3)
```
### Notes:
- Loads currently saved data from existing CSV files, if any.
- Queries the Binance API for data points from the last saved timestamp to the current time.
  - If no saved data was loaded, use "1 Dec, 2017" UTC as the default start date.
- All data is stored inside the *./data/* directory with a name corresponding to the coin-pair.
  - We follow the pandas.DataFrame structure with the below columns provided by the Binance API.
  - *Open Time* and *Close Time* are represented in milliseconds.

| Open Time | Open | High | Low | Close | Volume | Close Time | Quote Asset Volume | Number Trades | Taker Base Asset Volume | Take Quote Asset Volume | Ignore |
| --------- | ----| ----- | --- | ----- | ------ | ---------- | ------------------ | ------------- | ----------------------- | ----------------------- | ------ |

### Customize:
If you edit the file you find the following lines toward the bottom. This is where you can manually edit the time interval your data reflects and which coin-pairs you use.
- [This](https://python-binance.readthedocs.io/en/latest/constants.html) includes a list of valid time intervals you could use.
- For a list of valid coin-pairs, please refer to the Binance exchange on their website.

```
# Manually edit this for different time intervals.
api = Client.KLINE_INTERVAL_1HOUR

# Manually edit this for different coin pairs.
coins = ['ETHBTC', 'BNBBTC', 'XRPBTC', 'LTCBTC', 'ADABTC']
```

#### [analyze.py](https://github.com/AlecMasterson/binance-bot/blob/master/analyze.py)
This script will analyze your backtesting results.
```
python3 analyze.py <price-data> <trade-data>
```
- 'price-data' is the CSV file created from [get_history.py](https://github.com/AlecMasterson/binance-bot/blob/master/get_history.py)
- 'trade-data' is the CSV file created from your unique bot that contains all trades made during backtesting.