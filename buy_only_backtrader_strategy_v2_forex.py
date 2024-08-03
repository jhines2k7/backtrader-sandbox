from __future__ import (absolute_import, division, print_function, unicode_literals)

from datetime import datetime  # For datetime objects
import os  # To manage paths
import sys  # To find out the script name (in argv[0])
import logging

# Import the backtrader platform
import backtrader as bt

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('exitbars', 10),
        ('decimal_places', 15)
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.5f, NET %.5f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.5f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            current_close = self.dataclose[0]
            prev_close = self.dataclose[-1]
            prev_prev_close = self.dataclose[-2]

            if current_close < prev_close and prev_close < prev_prev_close:
                self.log(f'BUY CREATE, {current_close:.5f}')
                self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + self.params.exitbars):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.5f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

logs_dir = 'logs'
symbol = 'GBPJPY'
data_dir = 'yahoo-data'
log_file_name = f"{symbol}_strategy.log"
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{logs_dir}/{log_file_name}")

# Set up logging
log_file = f"{logs_dir}/{log_file_name}"

# delete the log file if it exists
if os.path.exists(log_file):
    os.remove(log_file)
    
# create the logs folder if it does not exist
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger()
logger.addHandler(file_handler)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, f"{data_dir}/{symbol}_M1_7_days.csv")

    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        nullvalue=0.0,
        dtformat=('%Y-%m-%d %H:%M:%S%z'),
        timeframe=bt.TimeFrame.Minutes, 
        compression=5,
        fromdate=datetime(2024, 7, 30, 00, 00, 00),
        todate=datetime(2024, 7, 30, 23, 59, 00),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        openinterest=-1,
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100) # 3 decimal places for 0.001, 5 decimal places for 0.00001

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.002) # 3 decimal places for 0.001, 5 decimal places for 0.00001

    # Print out the starting conditions
    logging.info('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    logging.info('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())