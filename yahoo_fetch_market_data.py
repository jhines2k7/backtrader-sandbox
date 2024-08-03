import yfinance as yf
import pandas as pd
import shutil
import os

from datetime import datetime, timedelta

end_date = datetime.today()
start_date = end_date - timedelta(days=6)

# Define the path to the data folder
data_folder = 'yahoo-data'

# create the data folder if it exists
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

symbols = [
    'GBPUSD',
    'EURUSD',
    'USDCHF',
    'USDJPY',
    'USDCAD',
    'AUDUSD',
    'EURJPY',
    'GBPJPY',
    'GBPCHF',
    'USDMXN',
    'EURGBP'
]

for symbol in symbols:
    # Download historical data for the financial instrument
    data = yf.download(f"{symbol}=X", start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval='1m')

    # Convert index to datetime and then to seconds since the epoch
    data.reset_index(inplace=True)
    data.set_index('Datetime', inplace=True)

    # Save to CSV
    data.to_csv(f"{data_folder}/{symbol}_M1_7_days.csv")

    print(f"Data saved to {data_folder}/{symbol}_M1_7_days.csv")