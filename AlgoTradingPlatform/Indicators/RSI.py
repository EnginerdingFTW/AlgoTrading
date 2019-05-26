import numpy as np
from .Utility import moving_average
from .Indicator import Indicator


class RSI(Indicator):
    def __init__(self):
        self.value = None
        self.last_period = None

    def calculate(self, data_stream, N=14):
        print(data_stream)
        delta = np.diff(data_stream)
        dUp = delta.copy()
        dDown = delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0

        RS1 = moving_average(dUp, N) / moving_average(np.abs(dDown), N)
        self.value = 100.0 - (100 / (1.0 + RS1))
        self.last_period = N
        return self.value
