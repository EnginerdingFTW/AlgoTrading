import requests
import json
import os
import numpy as np
import datetime


class DataGrabber():
    def __init__(self, api_key="demo", cache_dir=None):
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.intra_day_time_series = ["1min", "5min", "15min", "30min", "60min"]
        self.time_series = self.intra_day_time_series + ["1day", "1week"]

    def getTickerData(self, ticker, interval, start_time, end_time):
        ticker_data = None
        cache_file = os.path.join(str(self.cache_dir), ticker + ".json")
        if (self.cache_dir is not None and os.path.exists(cache_file)):
            with open(cache_file, "r") as f:
                ticker_data = json.load(f)

        loading_new_data = False
        if (ticker_data is not None and ticker_data["Meta Data"][interval + "_refresh"] is not None):
            print("start_time = " + str(start_time) + "  end_time = " + str(end_time))
            # check if the refresh time has the most recent data
        else:
            loading_new_data = True
            interval_ticker_data = self.getAlphaVantageData(ticker, interval)
            ticker_data = {
                "Meta Data": {
                    "Symbol": ticker,
                },
            }
            for time_interval in self.time_series:
                ticker_data["Meta Data"][time_interval + "_refresh"] = None
                ticker_data[time_interval] = {}
            ticker_data["Meta Data"][interval + "_refresh"] = interval_ticker_data["Meta Data"]["3. Last Refreshed"]
            ticker_data[interval] = interval_ticker_data["Time Series (%s)" % interval]

        if (self.cache_dir is not None and loading_new_data):
            with open(cache_file, "w") as f:
                json.dump(ticker_data, f, indent=4)
        return self.transformMarketDataToNumpyArray(ticker_data[interval], interval, start_time, end_time)

    def getAlphaVantageData(self, ticker, interval):
        if (interval in self.intra_day_time_series):
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=%s&" \
                  "outputsize=full&apikey=%s" % (ticker, interval, self.api_key)
        else:
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s"\
                  % (ticker, self.api_key)
        request_data = requests.get(url)
        interval_ticker_data = json.loads(request_data.text)
        return interval_ticker_data

    def transformMarketDataToNumpyArray(self, data, interval, start_time, end_time):
        data_stream = {
            "date": [],
            "1. open": [],
            "2. high": [],
            "3. low": [],
            "4. close": [],
            "5. volume": []
        }

        increment = {
            "1min": 60,
            "5min": 300,
            "15min": 900,
            "30min": 1800,
            "60min": 3600,
            "1day": 86400,
            "1week": 604800
        }
        seconds_interval = increment[interval]

        initial_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        final_datetime = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        while (start_time not in data.keys() and initial_datetime <= final_datetime):
            initial_datetime += datetime.timedelta(seconds=seconds_interval)
            start_time = initial_datetime.strftime("%Y-%m-%d %H:%M:%S")
        while (initial_datetime != final_datetime):
            if (start_time in data.keys()):
                data_stream["date"].append(start_time)
                for _key in ["1. open", "2. high", "3. low", "4. close", "5. volume"]:
                    data_stream[_key].append(data[start_time][_key])
            initial_datetime += datetime.timedelta(seconds=seconds_interval)
            start_time = initial_datetime.strftime("%Y-%m-%d %H:%M:%S")
        for _key in data_stream:
            data_stream[_key] = np.array(data_stream[_key])
        return data_stream
