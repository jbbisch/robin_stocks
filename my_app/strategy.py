# PythonCryptoTrader
import robin_stocks.robinhood as rh
import pandas as pd
import numpy as np
#from matplotlib import pyplot as plt 
#from matplotlib.dates import DateFormatter

# Retrieve last 5 days of DOGECOIN to USD exchange rates with a 5 minute interval and save the dataframe to a variable.
DOGE_USD = rh.get_latest_price(tickers='DOGE-USD', period='5d', interval='5m')

DOGE_USD.head()
print(pd.DataFrame(DOGE_USD.head()))

# Compute a 5-candle Simple Moving Average with pandas
DOGE_USD['SMA_5'] = DOGE_USD['Close'].rolling(window=5, min_periods=1).mean()

# Compute a 10-candle Simple Moving Average with pandas
DOGE_USD['SMA_10'] = DOGE_USD['Close'].rolling(window=10, min_periods=1).mean()

# Display the last 5 entries of the dataframe
DOGE_USD.tail()
print(pd.DataFrame(DOGE_USD.tail()))

# Create a pandas dataframe that is the same size as the DOGE_USD dataframe and covers the same dates
trade_signals = pd.DataFrame(index=DOGE_USD.index)

# Define the intervals for the Fast and Slow Simple Moving Averages (in days)
short_interval = 5
long_interval = 10

# Compute the Simple Moving Averages and add it to the dateframe as new columns
trade_signals['Short'] = DOGE_USD['Close'].rolling(window=short_interval, min_periods=1).mean()
trade_signals['Long'] = DOGE_USD['Close'].rolling(window=long_interval, min_periods=1).mean()

# Create a new column populated with zeros
trade_signals['Signal'] = 0.0

# Wherever the Shorter term SMA is above the Longer term SMA, set the Signal column to 1, otherwise 0
trade_signals['Signal'] = np.where(trade_signals['Short'] > trade_signals['Long'], 1.0, 0.0)   

# Order execution through trade signals 
trade_signals['Position'] = trade_signals['Signal'].diff()


