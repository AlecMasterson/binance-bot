import pandas, sys, math
import matplotlib.pyplot as plt
import numpy as np

def round_down(x):
	return float(math.floor(x * 1000) / 1000)

def buy(trading, row):
	return trading.append(
		{
			"Type": "buy",
			"Close Time": row["Close Time"],
			"Close": row["Close"],
			"BTC": trading.iloc[-1]["BTC"] - round_down(trading.iloc[-1]["BTC"]),
			"ETH": trading.iloc[-1]["ETH"] + (round_down(trading.iloc[-1]["BTC"]) / row["Close"])*0.999
		}, ignore_index=True
	)

def sell(trading, row):
	return trading.append(
		{
			"Type": "sell",
			"Close Time": row["Close Time"],
			"Close": row["Close"],
			"BTC": trading.iloc[-1]["BTC"] + (round_down(trading.iloc[-1]["ETH"]) * row["Close"])*0.999,
			"ETH": trading.iloc[-1]["ETH"] - round_down(trading.iloc[-1]["ETH"])
		}, ignore_index=True
	)

def predict_sell(trading, val, args):
	change = trading.iloc[len(trading.index) - 2]["BTC"] / (trading.iloc[-1]["BTC"] + (round_down(trading.iloc[-1]["ETH"]) * val)*0.999)
	if change < args["low"] or change > args["hi"]:
		return True
	return False

def backtest(file_name, interval_name, args):

	# --------------------------------------------------------------------------
	# SETUP
	# --------------------------------------------------------------------------

	print("\nPROC: Back-Test " + interval_name + " Interval Data...\n")

	try:
		print("IO: Looking For Existing Data...")
		df = pandas.read_csv(file_name)
		print("Found!")
	except:
		print("ERROR: No Existing Data Found!")
		sys.exit()

	trading = pandas.DataFrame(
		data={"Type": "sell", "Close Time": 0, "Close": 0, "BTC": 0.04, "ETH": 0.0},
		index=[0]
	)

	# --------------------------------------------------------------------------
	# ANALYSIS
	# --------------------------------------------------------------------------

	for index, row in df.iterrows():
		if index > 2:
			section = df[index-3:index]
			line = np.poly1d(np.polyfit(section["Close Time"], section["Close"], 2))

			if line.c[0] < 0 and row["Close"] < df.iloc[index-3]["Close"] and line.c[0] < float(args["thin"] * -1/100000000000000000):
				if row["Close"] < df.iloc[index-1]["Close"] and trading.iloc[-1]["Type"] is "sell":
					trading = buy(trading, row)
				if row["Close"] > df.iloc[index-1]["Close"] and trading.iloc[-1]["Type"] is "buy" and predict_sell(trading, row["Close"], args):
					trading = sell(trading, row)

				# Additional Plotting
				plot_x = np.linspace(section.iloc[0]["Close Time"], section.iloc[len(section.index)-1]["Close Time"])
				plt.plot(pandas.to_datetime(plot_x, unit="ms"), line(plot_x))

			if line.c[0] > 0 and row["Close"] > df.iloc[index-3]["Close"] and line.c[0] > float(args["thin"] * 1/100000000000000000):
				if row["Close"] < df.iloc[index-1]["Close"] and trading.iloc[-1]["Type"] is "sell":
					trading = buy(trading, row)
				if row["Close"] > df.iloc[index-1]["Close"] and trading.iloc[-1]["Type"] is "buy" and predict_sell(trading, row["Close"], args):
					trading = sell(trading, row)

				# Additional Plotting
				plot_x = np.linspace(section.iloc[0]["Close Time"], section.iloc[len(section.index)-1]["Close Time"])
				plt.plot(pandas.to_datetime(plot_x, unit="ms"), line(plot_x))

	# --------------------------------------------------------------------------
	# SAVE ANALYSIS
	# --------------------------------------------------------------------------

	try:
		print("IO: Writing " + interval_name + " Back-Tested Data to backtest_" + interval_name + ".csv")
		trading.to_csv("backtest_" + interval_name + ".csv", columns=["Type", "Close Time", "Close", "BTC", "ETH"], index=False)
		print("Success!")
	except:
		print("ERROR: Failed Writing to File!")
		sys.exit()

	# --------------------------------------------------------------------------
	# RESULTS
	# --------------------------------------------------------------------------

	print("\nRESULTS...\n")
	print("BTC: "+str(trading.iloc[-1]["BTC"])+"\nETH: "+str(trading.iloc[-1]["ETH"]))
	final = trading.iloc[-1]["BTC"] + (trading.iloc[-1]["ETH"] * trading.iloc[-1]["Close"])
	print("Final in BTC: "+str(final)+"\nPercent Increase: "+str(final/0.04))

	# --------------------------------------------------------------------------
	# PLOTTING
	# --------------------------------------------------------------------------

	df["Close Time"] = pandas.to_datetime(df["Close Time"], unit="ms")
	trading["Close Time"] = pandas.to_datetime(trading["Close Time"], unit="ms")

	bought = pandas.DataFrame(columns=["Close Time", "Close"])
	sold = pandas.DataFrame(columns=["Close Time", "Close"])
	for index, row in trading.iloc[1:].iterrows():
		if row["Type"] is "buy":
			bought = bought.append(row, ignore_index=True)
		else:
			sold = sold.append(row, ignore_index=True)

	x, y = bought.as_matrix(["Close Time", "Close"]).T
	a, b = sold.as_matrix(["Close Time", "Close"]).T

	plt.plot(df["Close Time"], df["Close"], linestyle="dashed")
	plt.scatter(x, y, color="red")
	plt.scatter(a, b, color="green")
	plt.show()

backtest("data_hour.csv", "1-Hour", {"thin": 2, "low": 0.998, "hi": 1.05})