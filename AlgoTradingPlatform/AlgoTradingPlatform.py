from .DataGrabbing.DataGrabber import DataGrabber
from .DataViewing.DataViewing import DataViewing
from .Indicators.RSI import RSI
import argparse
import numpy as np


def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api_key", help="Sets the api key to connect to AlphaVantage")
    return parser.parse_args(arg_list)


# My API Key = AGFVK8HO7O4A8022
def main(args):
    # args = parse_args(args)
    ticker = "SPY"
    grabber = DataGrabber(api_key="AGFVK8HO7O4A8022", cache_dir=r"/TickerDataCache")
    data_frame = grabber.getTickerData(ticker, "5min", "2019-05-17 10:00:00", "2019-05-24 16:00:00")
    print(data_frame)
    rsi = RSI()
    rsi.calculate(data_frame["Close"].values, 14)
    data_frame["RSI"] = np.zeros(data_frame["Close"].shape[0])
    data_frame["RSI"][1:] = rsi.value
    viewer = DataViewing()
    print(data_frame["RSI"])
    # viewer.TimeValueChart(data_frame, ticker)
    viewer.Plot(data_frame, "RSI")
    viewer.TimeValueChart(data_frame, ticker)

