import requests
import json
import os
import numpy as np
import datetime
import pandas as pd


class DataGrabber():
    def __init__(self, api_key="demo", cache_dir=None):
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.intra_day_time_series = ["1min", "5min", "15min", "30min", "60min"]
        self.time_series = self.intra_day_time_series + ["1day", "7day"]
        self.multi_day_series = ["7day"]
        self.increment = {
            "1min": 60,
            "5min": 300,
            "15min": 900,
            "30min": 1800,
            "60min": 3600,
            "1day": 86400,
            "7day": 604800,        # NOTE! if a sample is missing, it will extend to 2 weeks (or 3, etc.).
        }

    def getTickerData(self, ticker, interval, start_time, end_time):
        ticker_data = None
        cache_file = os.path.join(str(self.cache_dir), ticker + ".json")
        if (self.cache_dir is not None and os.path.exists(cache_file)):
            with open(cache_file, "r") as f:
                ticker_data = json.load(f)

        last_refresh = None
        if (ticker_data is not None and ticker_data["Meta Data"][interval + "_refresh"] is not None):
            if (" " in ticker_data["Meta Data"][interval + "_refresh"]):
                last_refresh = datetime.datetime.strptime(
                    ticker_data["Meta Data"][interval + "_refresh"], "%Y-%m-%d %H:%M:%S")
            else:
                last_refresh = datetime.datetime.strptime(ticker_data["Meta Data"][interval + "_refresh"], "%Y-%m-%d")

        loading_new_data = False
        if (ticker_data is not None and (last_refresh is None or last_refresh < MostUpdatedSampleDate())):
            loading_new_data = True
            self.UpdateTickerData(ticker_data, ticker, interval)
        elif (ticker_data is None):     # New ticker .csv!
            loading_new_data = True
            ticker_data = {
                "Meta Data": {
                    "Symbol": ticker,
                },
            }
            for time_interval in self.time_series:
                ticker_data["Meta Data"][time_interval + "_refresh"] = None
                ticker_data[time_interval] = {}
            self.UpdateTickerData(ticker_data, ticker, interval)

        if (self.cache_dir is not None and loading_new_data):
            with open(cache_file, "w") as f:
                json.dump(ticker_data, f, indent=4, sort_keys=True)

        return self.transformMarketDataToDataFrame(ticker_data[interval], interval, start_time, end_time)

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

    # def transformMarketDataToNumpyArray(self, data, interval, start_time, end_time):
    #     data_stream = {
    #         "date": [],
    #         "1. open": [],
    #         "2. high": [],
    #         "3. low": [],
    #         "4. close": [],
    #         "5. volume": []
    #     }
    #
    #     seconds_interval = self.increment[interval]
    #     if (" " in start_time and (interval in ["1day", "1week"])):
    #         start_time = start_time.split(" ")[0]
    #         end_time = end_time.split(" ")[0]
    #     if (" " in start_time):
    #         time_included = True
    #         initial_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    #         final_datetime = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    #     else:
    #         time_included = False
    #         initial_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d")
    #         final_datetime = datetime.datetime.strptime(end_time, "%Y-%m-%d")
    #
    #     while (start_time not in data.keys() and initial_datetime <= final_datetime):
    #         initial_datetime += datetime.timedelta(seconds=seconds_interval)
    #         if (time_included):
    #             start_time = initial_datetime.strftime("%Y-%m-%d %H:%M:%S")
    #         else:
    #             start_time = initial_datetime.strftime("%Y-%m-%d")
    #     while (initial_datetime <= final_datetime):
    #         if (start_time in data.keys()):
    #             data_stream["date"].append(start_time)
    #             for _key in ["1. open", "2. high", "3. low", "4. close", "5. volume"]:
    #                 data_stream[_key].append(data[start_time][_key])
    #         initial_datetime += datetime.timedelta(seconds=seconds_interval)
    #         if (time_included):
    #             start_time = initial_datetime.strftime("%Y-%m-%d %H:%M:%S")
    #         else:
    #             start_time = initial_datetime.strftime("%Y-%m-%d")
    #     for _key in data_stream:
    #         data_stream[_key] = np.array(data_stream[_key])
    #     return data_stream

    def transformMarketDataToDataFrame(self, data, interval, start_time, end_time):
        seconds_interval = self.increment[interval]
        if (" " in start_time and (interval not in self.intra_day_time_series)):
            start_time = start_time.split(" ")[0]
            end_time = end_time.split(" ")[0]
        if (" " in start_time):
            time_included = True
            initial_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            final_datetime = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        else:
            time_included = False
            initial_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d")
            final_datetime = datetime.datetime.strptime(end_time, "%Y-%m-%d")

        while (start_time not in data.keys() and initial_datetime <= final_datetime):
            initial_datetime += datetime.timedelta(seconds=seconds_interval)
            if (time_included):
                start_time = initial_datetime.strftime("%Y-%m-%d %H:%M:%S")
            else:
                start_time = initial_datetime.strftime("%Y-%m-%d")

        return self.GetDataStream(data, initial_datetime, final_datetime, seconds_interval,
                                                      interval, time_included)

    def GetDataStream(self, data, initial_datetime, final_datetime, seconds_interval, interval, time_included=True):
        start_time = initial_datetime
        data_stream = []
        while (initial_datetime <= final_datetime):
            if (start_time in data.keys()):
                if (interval in self.multi_day_series):
                    next_datetime = initial_datetime + datetime.timedelta(seconds=seconds_interval)

                    temp_data_stream = self.GetDataStream(data, initial_datetime, next_datetime,
                                                          self.increment["1day"], "1day", time_included=False)
                    open = temp_data_stream["Open"][0]
                    high = np.max(temp_data_stream["High"])
                    low = np.min(temp_data_stream["Low"])
                    close = temp_data_stream["Close"][temp_data_stream.index[-1]]
                    volume = np.sum(temp_data_stream["Volume"])
                    data_stream.append([
                        initial_datetime.strftime("%Y-%m-%d %H:%M"), initial_datetime, open, high, low, close, volume
                    ])
                else:
                    data_stream.append([
                        initial_datetime.strftime("%Y-%m-%d %H:%M"),
                        initial_datetime,
                        float(data[start_time]["1. open"]),
                        float(data[start_time]["2. high"]),
                        float(data[start_time]["3. low"]),
                        float(data[start_time]["4. close"]),
                        float(data[start_time]["5. volume"])
                    ])
            initial_datetime += datetime.timedelta(seconds=seconds_interval)
            if (time_included):
                start_time = initial_datetime.strftime("%Y-%m-%d %H:%M:%S")
            else:
                start_time = initial_datetime.strftime("%Y-%m-%d")
        return pd.DataFrame.from_records(np.array(data_stream),
                                         columns=["Date String", "Date", "Open", "High", "Low", "Close", "Volume"])


    def UpdateTickerData(self, ticker_data, ticker, interval):
        interval_ticker_data = self.getAlphaVantageData(ticker, interval)
        temp_interval = interval
        if (temp_interval not in self.intra_day_time_series):
            temp_interval = "Daily"
        if (ticker_data["Meta Data"][interval + "_refresh"] is None):
            ticker_data[interval] = interval_ticker_data["Time Series (%s)" % temp_interval]
        else:
            data = interval_ticker_data["Time Series (%s)" % temp_interval]
            for key_date in data.keys():
                if (key_date not in ticker_data[interval].keys()):
                    ticker_data[interval][key_date] = data[key_date]
        ticker_data["Meta Data"][interval + "_refresh"] = interval_ticker_data["Meta Data"]["3. Last Refreshed"]
        return ticker_data


def MostUpdatedSampleDate(current_time=None):
    if(current_time is None):
        current_time = datetime.datetime.now()

    # get friday, one week ago, at 16 o'clock
    last_friday = (current_time.date()
                   - datetime.timedelta(days=current_time.weekday())
                   + datetime.timedelta(days=4, weeks=-1))
    last_friday_at_16 = datetime.datetime.combine(last_friday, datetime.time(16))

    # if today is also friday, and after 16 o'clock, change to the current date
    one_week = datetime.timedelta(weeks=1)
    if current_time - last_friday_at_16 >= one_week:
        last_friday_at_16 += one_week

    end_of_trading_week = datetime.datetime.combine(current_time.date() - datetime.timedelta(days=current_time.weekday()) + datetime.timedelta(days=4), datetime.time(16))

    end_of_trading_day = datetime.datetime.combine(current_time.date(), datetime.time(hour=16))
    end_of_last_trading_day = end_of_trading_day - datetime.timedelta(days=1)
    start_of_trading_day = datetime.datetime.combine(current_time.date(), datetime.time(hour=9, minute=30))
    if (current_time > end_of_trading_week):
        most_updated_time = end_of_trading_week
    elif (current_time > end_of_trading_day):
        most_updated_time = end_of_trading_day
    elif (current_time < start_of_trading_day):
        most_updated_time = end_of_last_trading_day
    else:
        most_updated_time = current_time
    return most_updated_time


if __name__ == "__main__":
    print(MostUpdatedSampleDate())
    print(MostUpdatedSampleDate(datetime.datetime(2019, 5, 24, 12, 0)))
    print(MostUpdatedSampleDate(datetime.datetime(2019, 5, 23, 17, 0)))
    print(MostUpdatedSampleDate(datetime.datetime(2019, 5, 23, 11, 0)))
    print(MostUpdatedSampleDate(datetime.datetime(2019, 5, 22, 0, 0)))
    print(MostUpdatedSampleDate(datetime.datetime(2019, 5, 21, 0, 0)))
    print(MostUpdatedSampleDate(datetime.datetime(2019, 5, 19, 0, 0)))