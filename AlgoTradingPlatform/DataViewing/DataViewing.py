import numpy as np
import mpl_finance
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import datetime


class DataViewing():
    def __init__(self):
        self.plotDict = {}
        self.candle_keys = ["1. open", "2. high", "3. low", "4. close", "5. volume"]

    def TimeValueChart(self, ticker_data_frame, ticker):
        fig = plt.figure()
        ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=6, colspan=1)
        mpl_finance.candlestick2_ochl(
            ax1,
            opens=ticker_data_frame["Open"],
            closes=ticker_data_frame["Close"],
            highs=ticker_data_frame["High"],
            lows=ticker_data_frame["Low"],
            colorup='g',
            colordown='r',
            width=1 / (24 * 60) * 1
        )
        ax1.set_xticks(np.arange(len(ticker_data_frame["Date"])))
        ax1.set_xticklabels(ticker_data_frame['Date'], fontsize=6, rotation=-90)

        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title(ticker)
        plt.show()

        self.plotDict[fig] = {
            "figure": fig,
            "axis": ax1,
        }
        return fig

    def Plot(self, ticker_data_frame, frame_column):
        fig = plt.figure()
        ax1 = plt.subplot2grid((1, 1), (0, 0), rowspan=1, colspan=1)

        plt.plot(ticker_data_frame[frame_column])

        ax1.set_xticks(np.arange(len(ticker_data_frame["Date"])))
        ax1.set_xticklabels(ticker_data_frame['Date'], fontsize=6, rotation=-90)

        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title(frame_column)
        plt.show()

        self.plotDict[fig] = {
            "figure": fig,
            "axis": ax1,
        }
        return fig
