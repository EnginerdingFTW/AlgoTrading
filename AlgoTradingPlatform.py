from DataGrabbing.DataGrabber import DataGrabber
import argparse


def parse_args(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", help="Sets the api key to connect to AlphaVantage")
    return parser.parse_args(arg_list)


def main(args):
    # args = parse_args(args)
    print("made it")
    grabber = DataGrabber(cache_dir=r"C:\Test")
    data = grabber.getTickerData("MSFT", "5min", "2019-05-17 09:35:00", "2019-05-17 16:00:00")
    print(data)

