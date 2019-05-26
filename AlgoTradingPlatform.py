from DataGrabbing.DataGrabber import DataGrabber
from DataViewing.DataViewing import DataViewing
import argparse


def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api_key", help="Sets the api key to connect to AlphaVantage")
    return parser.parse_args(arg_list)


# My API Key = AGFVK8HO7O4A8022
def main(args):
    # args = parse_args(args)
    ticker = "SPY"
    grabber = DataGrabber(api_key="AGFVK8HO7O4A8022", cache_dir=r"/TickerDataCache")
    data_frame = grabber.getTickerData(ticker, "1min", "2019-05-10 10:00:00", "2019-05-24 16:00:00")
    print(data_frame)
    # viewer = DataViewing()
    # viewer.TimeValueChart(data_frame, ticker)

