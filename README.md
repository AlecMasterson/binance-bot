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
pip3 install python-binance
pip3 install 
pip3 install pandas
```

### Data

All data is stored in CSV files generated by the [get_history.py](https://github.com/AlecMasterson/binance-bot/blob/master/get_history.py) script. We utilize the DataFrame structure from the Pandas library.

### Running

Currently, only data acquisition is fully implemented. To run this script, simply use the following command:

```
python3 get_history.py
```

## Files

Below is a more detailed description of each of the implemented files.

#### get-history.py
- Load current saved data from existing CSV file, if any.
- Query the Binance API for data points from last saved timestamp to the current time.
  - If no saved data was loaded, use "1 Dec, 2017" as the default start time.
- Save all data to a CSV.

The bottom of the script is where you can edit what time interval you wish to use and what file name to store the data in.