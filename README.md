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

#### [get_history.py](https://github.com/AlecMasterson/binance-bot/blob/master/get_history.py)
This automated script will obtain historical data from Binance to be used in backtesting. It will obtain data for (currently) five different coin-pairs.
```
python3 get_history.py
```
- Loads currently saved data from existing CSV files, if any.
- Queries the Binance API for data points from the last saved timestamp to the current time.
  - If no saved data was loaded, use "1 Dec, 2017" UTC as the default start date.
- All data is stored inside the *./data/* directory with a name corresponding to the coin-pair.
  - We follow the pandas.DataFrame structure with the below columns provided by the Binance API.
  - *Open Time* and *Close Time* are represented in milliseconds.

| Open Time | Open | High | Low | Close | Volume | Close Time | Quote Asset Volume | Number Trades | Taker Base Asset Volume | Take Quote Asset Volume | Ignore |
| --------- | ----| ----- | --- | ----- | ------ | ---------- | ------------------ | ------------- | ----------------------- | ----------------------- | ------ |

#### [analyze.py](https://github.com/AlecMasterson/binance-bot/blob/master/analyze.py)
This script will analyze your backtesting results.
```
python3 analyze.py <price-data> <trade-data>
```
- 'price-data' is the CSV file created from [get_history.py](https://github.com/AlecMasterson/binance-bot/blob/master/get_history.py)
- 'trade-data' is the CSV file created from your unique bot that contains all trades made during backtesting.