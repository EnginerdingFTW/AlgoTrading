from .DataGrabbing.DataGrabber import DataGrabber
from .DataViewing.DataViewing import DataViewing
from .Indicators.RSI import RSI
import argparse
import numpy as np


def parsing_args(arg_list):
    parser = argparse.ArgumentParser(description="Algo Platform to perform data analytics and modelling")
    parser.add_argument("-a", "--api_key", help="Sets the api key to connect to AlphaVantage")
    return parser.parse_args(arg_list)


# My API Key = AGFVK8HO7O4A8022
def main(args):
    args = parsing_args(args)
    ticker = "SPY"

    ## Data Grabber
                # api_key = "AGFVK8HO7O4A8022"
    grabber = DataGrabber(api_key=args.api_key, cache_dir=r"C:\Repositories\TickerCache")
    data_frame = grabber.getTickerData(ticker, "7day", "2019-02-11 8:00:00", "2020-02-14 16:00:00")
    print(data_frame)


    ## Data Analyzing
    # rsi = RSI()
    # rsi.calculate(data_frame["Close"].values, 14)
    # data_frame["RSI"] = np.zeros(data_frame["Close"].shape[0])
    # data_frame["RSI"][1:] = rsi.value




    # Data Viewing
    viewer = DataViewing()
    # print(data_frame["RSI"])
    # viewer.TimeValueChart(data_frame, ticker)
    # viewer.Plot(data_frame, "RSI")
    # viewer.TimeValueChart(data_frame, ticker)

