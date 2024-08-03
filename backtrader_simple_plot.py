from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import matplotlib.pyplot as plt

class St(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data)


data = bt.feeds.BacktraderCSVData(dataname='datas/orcl-1995-2014.txt')

cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.addstrategy(St)
cerebro.run()

plt.rcParams['figure.figsize'] = [20, 10]
fig = cerebro.plot(style='candlestick')[0][0]

# Save the plot to a file
fig.savefig('backtrader_plot.png')