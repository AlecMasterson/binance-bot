# Binance Bot

This bot is used for the automation of trading cryptocurrencies on the Binance exchange. Currently enabled for trading between ETH and BTC.

## Requirements

  - Binance Account and API Access
  - Python 2
  - [Python-Binance API](https://github.com/sammchardy/python-binance)

## Setup

Edit keys.txt with your API info. The file should contain two lines, first your api_key and then your api_secret. No quotation marks.

## Development

Edit the keys.txt with your API info.
Use the data.py file to manage what historical data you use.
Use the backtest.py file to manage your backtesting algorithm.

## Running

```
python binance-bot.py
```
Yes it's that simple.
