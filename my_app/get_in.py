import robin_stocks.robinhood as rh
import variables
import pyotp
import datetime
import time
import pandas as pd
import numpy as np
import requests
import pickle
#import multiprocessing
from robin_stocks.robinhood.orders import *
from robin_stocks.robinhood.urls import *

totp = pyotp.TOTP(variables.MFA_Code).now()
#print("Current OTP:", totp)
login =rh.login(variables.RH_Login, variables.RH_Pass, mfa_code=totp, store_session=True)

# Get values for useage in other scripts
my_portfolio = rh.load_phoenix_account()
#print(my_portfolio)

# Total portfolio value
portfolio_vlue = my_portfolio["portfolio_equity"]["amount"]
#print("Current portfolio value: $", float(portfolio_vlue))

# Buying power
buying_power = my_portfolio["account_buying_power"]["amount"]
#print("Crypto buying power: $", float(buying_power))

# get crypto positions
crypto_positions = rh.get_crypto_positions()
#print(crypto_positions)

# Selling power
selling_power = crypto_positions[1]["quantity"]
#print("Crypto selling power: $", float(selling_power))

######################
# Everything below is strategy
######################

# Get the current price of ETH
ETH_price = rh.get_crypto_quote("ETH")["mark_price"]
#print("Current ETH price: $", float(ETH_price))
        
# Create an empty dataframe to store the date and price
ETH_df = pd.DataFrame(columns=["Date and Time", "Current Price", "SMA_5", "SMA_7"])
#print(ETH_df)

# Create empty lists to store the date and price
date_list = []
price_list = []

# Create an empty dataframe to store the trade signals
buy_signals = pd.DataFrame(columns=["Short", "Long", "Signal", "Position"])
sell_signals = pd.DataFrame(columns=["Short", "Long", "Signal", "Position"])

now = datetime.datetime.now()
#print("Current date and time: ", now)
sleepSeconds = (1 * 60) - (now.second + ((now.minute % 1) * 60))

def data_loop():
    # Run the loop on every 5th minute of the hour forever
    while True:
        # Get values for useage in other scripts
        my_portfolio = rh.load_phoenix_account()
        #print(my_portfolio)

        # Total portfolio value
        portfolio_vlue = my_portfolio["portfolio_equity"]["amount"]
        #round to nearest 2 decimal places
        portfolio_vlue = round(float(portfolio_vlue), 2)
        print("Current portfolio value: $", float(portfolio_vlue))

        # Buying power
        buying_power = my_portfolio["account_buying_power"]["amount"]
        #round to nearest 2 decimal places
        buying_power = round(float(buying_power), 2)
        print("Crypto buying power: $", float(buying_power))

        # get crypto positions
        crypto_positions = rh.get_crypto_positions()
        #print(crypto_positions)

        # Selling power
        selling_power = crypto_positions[1]["quantity"]
        #round to nearest 2 decimal places
        selling_power = float(selling_power)
        print("Crypto selling power: ETH", float(selling_power), '\n')

        # Get the current price of ETH
        ETH_price = rh.get_crypto_quote("ETH")["mark_price"]
        #print("Current ETH price: $", float(ETH_price))

        now = datetime.datetime.now()
        #print("Current date and time: ", now)

        # Append the date and price to the lists and remove index 0 if list is greater than 19
        date_list.append(datetime.datetime.now())
        if (len(date_list) > 19):
            date_list.pop(0)

        price_list.append(float(ETH_price))
        if (len(price_list) > 19):
            price_list.pop(0)

        # Create a growing index for the dataframe
        index = range(0, len(date_list))
        #print(index)

        # Use the index variable as the index for the dataframe
        ETH_df = pd.DataFrame(index=index)

        # Store the date and price lists in the dataframe
        ETH_df["Date and Time"] = date_list
        ETH_df["Current Price"] = price_list

        # Compute a 5-candle Simple Moving Average with pandas
        ETH_df['SMA_5'] = ETH_df['Current Price'].rolling(window=5, min_periods=1).mean()

        # Compute a 10-candle Simple Moving Average with pandas
        ETH_df['SMA_7'] = ETH_df['Current Price'].rolling(window=7, min_periods=1).mean()

        # Display the last 15 entries of the dataframe
        #print(pd.DataFrame(ETH_df.tail(15)), '\n')

        # Create a pandas dataframe that is the same size as ETH_df
        buy_signals = pd.DataFrame(index=ETH_df.index)
        sell_signals = pd.DataFrame(index=ETH_df.index)

        # Define the intervals for the Fast and Slow Simple Moving Averages (in data points)
        short_interval = 5
        long_interval = 7

        # Compute the Simple Moving Averages and add it to the dateframe as new columns
        buy_signals['Short'] = ETH_df['Current Price'].rolling(window=short_interval, min_periods=1).mean()
        buy_signals['Long'] = ETH_df['Current Price'].rolling(window=long_interval, min_periods=1).mean()
        sell_signals['Short'] = ETH_df['Current Price'].rolling(window=short_interval, min_periods=1).mean()
        sell_signals['Long'] = ETH_df['Current Price'].rolling(window=long_interval, min_periods=1).mean()

        # Create a new column populated with zeros
        buy_signals['Signal'] = 0.0
        sell_signals['Signal'] = 0.0

        # Wherever the Shorter term SMA is above the Longer term SMA, set the Signal column to 1, otherwise 0
        buy_signals['Signal'] = np.where(buy_signals['Short'] > buy_signals['Long'], 1.0, 0.0)
        sell_signals['Signal'] = np.where(sell_signals['Short'] < sell_signals['Long'], 1.0, 0.0)

        # Order execution through trade signals 
        buy_signals['Position'] = buy_signals['Signal'].diff()
        sell_signals['Position'] = sell_signals['Signal'].diff()

        # Display the last 15 entries of the dataframe    
        #print('Buy_DF', '\n', pd.DataFrame(buy_signals.tail(15)), '\n')
        #print('Sell_DF', '\n', pd.DataFrame(sell_signals.tail(15)), '\n')

        # Use pickle to save the dataframe to a file for later use (in other scripts)
        ETH_df.to_pickle("ETH_df.pkl")
        # To append to a pickle file, use the following:
        with open('ETH_df.pkl', 'ab') as f:
            pickle.dump(ETH_df, f)

        buy_signals.to_pickle("buy_signals.pkl")
        # To append to a pickle file, use the following:
        with open('buy_signals.pkl', 'ab') as f:
            pickle.dump(buy_signals, f)

        sell_signals.to_pickle("sell_signals.pkl")
        # To append to a pickle file, use the following:
        with open('sell_signals.pkl', 'ab') as f:
            pickle.dump(sell_signals, f)


        load_data()


        ###############
        ### identify buy and sell signals ###
        ###############

        # if the position is 1, buy
        #if (buy_signals[0:-1] == 1):
        #    #print("Buy")
        #    buy_order()
        #else: None
            
        # if the position is 1, sell
        #if (sell_signals[0:-1] == 1):
        #    #print("Sell")
        #    sell_order()
        #else: None

############# SLEEPY TIME #############

        # how many more seconds do i need to sleep?
        sleepSeconds = (5 * 60) - (now.second + ((now.minute % 5) * 60))
        #print(f"sleep for {sleepSeconds} seconds")
        if ( sleepSeconds == 300 ):
            print(f"just get this done on the dot {now.minute}:{now.second}")
        else:
            time.sleep(sleepSeconds) #snooze till the magic minute

ETH_df = pd.read_pickle("ETH_df.pkl")
buy_signals = pd.read_pickle("buy_signals.pkl")
sell_signals = pd.read_pickle("sell_signals.pkl")

def load_data():
    # To load from pickle file, use the following:
    # Load the updated dataframe from the file
    ETH_df = pd.read_pickle("ETH_df.pkl")
    with open('ETH_df.pkl', 'rb') as f:
        ETH_df = pickle.load(f)
    print('ETH DataFrame', '\n', ETH_df, '\n')

    buy_signals = pd.read_pickle("buy_signals.pkl")
    with open('buy_signals.pkl', 'rb') as f:
        buy_signals = pickle.load(f)
    print('Buy DataFrame', '\n', buy_signals, '\n')

    sell_signals = pd.read_pickle("sell_signals.pkl")
    with open('sell_signals.pkl', 'rb') as f:
        sell_signals = pickle.load(f)
    print('Sell DataFrame', '\n', sell_signals, '\n')

    # Use the dataframe to buy and sell
    for i in range(0, len(buy_signals['Position'])):
        if buy_signals['Position'][i] == 1:
            buy_order()

    for i in range(0, len(sell_signals['Position'])):
        if sell_signals['Position'][i] == 1:
            sell_order()


###################
### these work ### figure out the price randomness issue, maybe make multiple order attempts
###################

def buy_order():
    if (float(buying_power) > 1.00):
        requests.post(rh.orders.order_crypto(symbol='ETH', side='buy', quantityOrPrice=(float(buying_power) - 0.50), amountIn="price", limitPrice=None, timeInForce='gtc', jsonify=True))   
    totp = pyotp.TOTP(variables.MFA_Code).now()
    #print("Current OTP:", totp)
    login =rh.login(variables.RH_Login, variables.RH_Pass, mfa_code=totp, store_session=True) 
    pass
    
def sell_order():
    if (float(selling_power) > 0.0008):
        requests.post(rh.orders.order_crypto(symbol='ETH', side='sell', quantityOrPrice=(float(selling_power) - 0.000799), amountIn="quantity", limitPrice=None, timeInForce='gtc', jsonify=True))
    totp = pyotp.TOTP(variables.MFA_Code).now()
    #print("Current OTP:", totp)
    login =rh.login(variables.RH_Login, variables.RH_Pass, mfa_code=totp, store_session=True) 
    pass


#####################
### loop the file ###
#####################

while True:
    data_loop()