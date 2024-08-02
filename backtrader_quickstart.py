from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader as bt
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)

    logging.info(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")

    cerebro.run()

    logging.info(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")