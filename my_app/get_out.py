import robin_stocks.robinhood as rh
import variables
import pyotp
import datetime
import time
import pandas as pd
import numpy as np
import requests
import pickle
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

# Int buying power calculation
# buying_power divided by the current price of XLM 
#buying_power = round(float(buying_power ), 2)
XLM_buying_power = float(buying_power) // float(rh.get_crypto_quote("XLM")["mark_price"])
#print("Crypto buying power: XLM", int(XLM_buying_power))

# Get crypto positions
crypto_positions = rh.get_crypto_positions()
#print(crypto_positions)

# Selling power
selling_power = crypto_positions[0]["quantity"]
#print("Crypto selling power: $", float(selling_power))

######################
### Everything below is strategy variables ###
######################

# Get the current price of XLM
XLM_price = rh.get_crypto_quote("XLM")["mark_price"]
#print("Current XLM price: $", float(XLM_price))
        
# Create an empty dataframe to store the date and price
loop_df = pd.DataFrame(columns=["Date and Time", "Current Price", "SMA_5", "SMA_10"])
#print(loop_df)

# Create empty lists to store the date and price
date_list = []
price_list = []

# Create an empty dataframe to store the trade signals
loop_buy_df = pd.DataFrame(columns=["Signal", "Position"])
loop_sell_df = pd.DataFrame(columns=["Signal", "Position"])

# Current date and time
now = datetime.datetime.now()
#print("Current date and time: ", now)

# Global sleep variable
sleepSeconds = (1 * 60) - (now.second + ((now.minute % 1) * 60))

# Make pickle files global variables
pkl_asset_df = pd.read_pickle("loop_df.pkl")
pkl_buy_df = pd.read_pickle("loop_buy_df.pkl")
pkl_sell_df = pd.read_pickle("loop_sell_df.pkl")


# Define sleep first function
def sleep_first():
    # How many more seconds do i need to sleep?
    sleepSeconds = (5 * 60) - (now.second + ((now.minute % 5) * 60))
    #print(f"sleep for {sleepSeconds} seconds")
    if ( sleepSeconds == 300 ):
        print(f"just get this done on the dot {now.minute}:{now.second}")
    else:
        time.sleep(sleepSeconds) #snooze till the magic minute
    
##  # Call on load_data to start new data collection cycle
    data_loop()


# Start new data collection cycle
def data_loop():
    # Run the loop on every 15th minute of the hour forever
    while True:
        # Load previous script run data from pickle files
    ##  # To load from pickle file, use the following:
        pkl_asset_df = pd.read_pickle("loop_df.pkl")
        with open('loop_df.pkl', 'rb') as f:
            pkl_asset_df = pickle.load(f)

        pkl_buy_df = pd.read_pickle("loop_buy_df.pkl")
        with open('loop_buy_df.pkl', 'rb') as f:
            pkl_buy_df = pickle.load(f)

        pkl_sell_df = pd.read_pickle("loop_sell_df.pkl")
        with open('loop_sell_df.pkl', 'rb') as f:
            pkl_sell_df = pickle.load(f)

        # Make pickle files into pandas df
        pkl_asset_df = pd.DataFrame(pkl_asset_df)
        pkl_buy_df = pd.DataFrame(pkl_buy_df)
        pkl_sell_df = pd.DataFrame(pkl_sell_df)
        
 
    ##  # Print the pickled dataframe from the file
        print('XLM DataFrame', '\n', pkl_asset_df, '\n')
    
        pkl_buy_df['Position'] = 0.0
        print('Previous Buy DataFrame', '\n', pkl_buy_df, '\n')
    
        pkl_sell_df['Position'] = 0.0
        print('Previous Sell DataFrame', '\n', pkl_sell_df, '\n')
    
###     # Get values for useage in other scripts
        my_portfolio = rh.load_phoenix_account()
        #print(my_portfolio)

###     # Total portfolio value
        portfolio_vlue = my_portfolio["portfolio_equity"]["amount"]
        #round to nearest 2 decimal places
        portfolio_vlue = round(float(portfolio_vlue), 2)
        print("Current portfolio value: $", float(portfolio_vlue))

###     # Buying power
        buying_power = my_portfolio["account_buying_power"]["amount"]
        #round to nearest 2 decimal places
        #buying_power = round(float(buying_power), 2)
        #print("Crypto buying power: $", float(buying_power))
        
###     # Int buying power calculation for XLM
        XLM_buying_power = float(buying_power) // float(rh.get_crypto_quote("XLM")["mark_price"])
        print("Crypto buying power: XLM", int(XLM_buying_power))

###     # Get crypto positions
        crypto_positions = rh.get_crypto_positions()
        #print(crypto_positions)

###     # Selling power
        selling_power = crypto_positions[0]["quantity"]
        print("Crypto selling power: XLM", float(selling_power), '\n')

###     # Get the current price of XLM
        XLM_price = rh.get_crypto_quote("XLM")["mark_price"]
        #print("Current XLM price: $", float(XLM_price))

###     # Get the current date and time
        now = datetime.datetime.now()
        #print("Current date and time: ", now)

###     # Append the date and price to the lists and remove index 0 if list is greater than 19
        date_list.append(datetime.datetime.now())
        if (len(date_list) > 1):
            date_list.pop(0)

        price_list.append(float(XLM_price))
        if (len(price_list) > 1):
            price_list.pop(0)

###     # Create a growing index for the dataframe
        index = range(0, len(date_list))
        #print(index)

###     # Use the index variable as the index for the dataframe
        loop_df = pd.DataFrame(index=index)

###     # Store the date and price lists in the dataframe
        loop_df["Date and Time"] = date_list
        loop_df["Current Price"] = price_list

###     # Compute a 5-candle Simple Moving Average with pandas
        loop_df['SMA_5'] = loop_df['Current Price'].rolling(window=5, min_periods=5).mean()

        # Compute a 10-candle Simple Moving Average with pandas
        loop_df['SMA_10'] = loop_df['Current Price'].rolling(window=10, min_periods=10).mean()

        # Display the last 15 entries of the dataframe
        #print(pd.DataFrame(loop_df.tail(15)), '\n')

###     # Create a pandas dataframe that is the same size as loop_df
        loop_buy_df = pd.DataFrame(index=loop_df.index)
        loop_sell_df = pd.DataFrame(index=loop_df.index)

###     # Define the intervals for the Fast and Slow Simple Moving Averages (in data points)
        short_interval = 5
        #long_interval = 10

###     # Compute the Simple Moving Averages and add it to the dateframe as new columns
        #loop_buy_df['Short'] = loop_df['Current Price'].rolling(window=short_interval, min_periods=5).mean()
        #loop_buy_df['Long'] = loop_df['Current Price'].rolling(window=long_interval, min_periods=10).mean()
        #loop_sell_df['Short'] = loop_df['Current Price'].rolling(window=short_interval, min_periods=5).mean()
        #loop_sell_df['Long'] = loop_df['Current Price'].rolling(window=long_interval, min_periods=10).mean()

###     # Create a new column populated with zeros
        ## loop_buy_df['Signal'] = 0.0
        ## loop_sell_df['Signal'] = 0.0

        # Wherever the Shorter term SMA is above the Longer term SMA, set the Signal column to 1, otherwise 0
        #loop_buy_df['Signal'] = np.where(loop_buy_df['Short'] > loop_buy_df['Long'], 1.0, 0.0)
        #loop_sell_df['Signal'] = np.where(loop_sell_df['Short'] < loop_sell_df['Long'], 1.0, 0.0)

        # Order execution through trade signals 
        #loop_buy_df['Position'] = loop_buy_df['Signal'].diff()
        #loop_sell_df['Position'] = loop_sell_df['Signal'].diff()

        # Display the last 15 entries of the dataframe    
        #print('Buy_DF', '\n', pd.DataFrame(loop_buy_df.tail(15)), '\n')
        #print('Sell_DF', '\n', pd.DataFrame(loop_sell_df.tail(15)), '\n')

        ################
        ### identify buy and sell signals ###
        ################

###     # Combine pkl_asset_df with loop_df
        Asset_Data = pd.concat([pkl_asset_df, loop_df], axis=0, ignore_index=True)
        # If the length of the dataframe is greater than 12, drop the first row
        if len(Asset_Data) > 9:
            Asset_Data = Asset_Data.drop(Asset_Data.index[0])
            # Reset the index
            Asset_Data = Asset_Data.reset_index(drop=True)
        # Recalculate moving averages
        Asset_Data['SMA_5'] = Asset_Data['Current Price'].rolling(window=5, min_periods=5).mean()
        Asset_Data['SMA_10'] = Asset_Data['Current Price'].rolling(window=10, min_periods=10).mean()
        print('Asset DataFrame', '\n', Asset_Data, '\n')

###     # Combine pkl_buy_df with loop_buy_df
        Buy_Signal = pd.concat([pkl_buy_df, loop_buy_df], axis=0, ignore_index=True)
        # If the length of the dataframe is greater than 12, drop the first row
        if len(Buy_Signal) > 9:
            Buy_Signal = Buy_Signal.drop(Buy_Signal.index[0])
            # Reset the index
            Buy_Signal = Buy_Signal.reset_index(drop=True)
        # Recalculate moving averages
        Buy_Signal['Current Price'] = Asset_Data['Current Price']
        Buy_Signal['MA1'] = Asset_Data['Current Price'].rolling(window=short_interval, min_periods=5).mean()
        # Wherever the current price is greater than MA1 and MA1 index 9 is greater than MA2 index 8, set the Signal column to 1, otherwise 0
##      Buy_Signal['Signal'] = np.where(Buy_Signal['Current Price'][9] > Buy_Signal['MA1'][9] and Buy_Signal['MA1'][9] > Buy_Signal['MA1'][8], 1.0, 0.0)
##      Buy_Signal['Signal'][9] = np.where(Buy_Signal['MA1'][9] > Buy_Signal['MA1'][8], 1.0, 0.0)
        Buy_Signal['Signal'] = np.where(Buy_Signal['MA1'].diff() > 0, 1.0, 0.0)
        # Order execution through trade signals 
        Buy_Signal['Position'] = Buy_Signal['Signal'].diff()
        print('Buy DataFrame', '\n', Buy_Signal, '\n')

###     # Combine pkl_sell_df with loop_sell_df
        Sell_Signal = pd.concat([pkl_sell_df, loop_sell_df], axis=0, ignore_index=True)
        # If the length of the dataframe is greater than 12, drop the first row
        if len(Sell_Signal) > 9:
            Sell_Signal = Sell_Signal.drop(Sell_Signal.index[0])
            # Reset the index
            Sell_Signal = Sell_Signal.reset_index(drop=True)
        # Recalculate moving averages
        Sell_Signal['Current Price'] = Asset_Data['Current Price']
        Sell_Signal['MA1'] = Asset_Data['Current Price'].rolling(window=short_interval, min_periods=5).mean()
        # Wherever the current price is less than MA1 and MA1 index 9 is less than MA2 index 8, set the Signal column to 1, otherwise 0
##      Sell_Signal['Signal'] = np.where(Sell_Signal['Current Price'][9] < Sell_Signal['MA1'][9] and Sell_Signal['MA1'][9] < Sell_Signal['MA1'][8], 1.0, 0.0)
##      Sell_Signal['Signal'][9] = np.where(Sell_Signal['MA1'][9] < Sell_Signal['MA1'][8], 1.0, 0.0)
        Sell_Signal['Signal'] = np.where(Sell_Signal['MA1'].diff() < 0, 1.0, 0.0) 
        # Order execution through trade signals 
        Sell_Signal['Position'] = Sell_Signal['Signal'].diff()
        print('Sell DataFrame', '\n', Sell_Signal, '\n')
        

###     # Use pickle to save the dataframe to a file for next script run

        Asset_Data.to_pickle("loop_df.pkl")
        # To append to a pickle file, use the following:
        with open('loop_df.pkl', 'ab') as f:
            pickle.dump(loop_df, f)

        Buy_Signal.to_pickle("loop_buy_df.pkl")
        # To append to a pickle file, use the following:
        with open('loop_buy_df.pkl', 'ab') as f:
            pickle.dump(loop_buy_df, f)

        Sell_Signal.to_pickle("loop_sell_df.pkl")
        # To append to a pickle file, use the following:
        with open('loop_sell_df.pkl', 'ab') as f:
            pickle.dump(loop_sell_df, f)

        ###     # Use the dataframe to buy and sell based on last index value
        if Buy_Signal['Position'][9] == 1:
            buy_order()
        else: None

        if Sell_Signal['Position'][9] == 1:
            sell_order()
        else: None


############# SLEEPY TIME #############

        # How many more seconds do i need to sleep?
        sleepSeconds = (5 * 60) - (now.second + ((now.minute % 5) * 60))
        #print(f"sleep for {sleepSeconds} seconds")
        if ( sleepSeconds == 300 ):
            print(f"just get this done on the dot {now.minute}:{now.second}")
        else:
            time.sleep(sleepSeconds) #snooze till the magic minute


###################
### these work ### ///figure out the order rejection issue///
###################

def buy_order():
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            buying_power = my_portfolio["account_buying_power"]["amount"]
            XLM_buying_power = float(buying_power) // float(rh.get_crypto_quote("XLM")["mark_price"])
            if (float(XLM_buying_power) > 300):
                requests.post(rh.orders.order_crypto(symbol='XLM', side='buy', quantityOrPrice=int(float(XLM_buying_power) * 0.94), amountIn='quantity', limitPrice=None, timeInForce='gtc', jsonify=True))   
            totp = pyotp.TOTP(variables.MFA_Code).now()
            #print("Current OTP:", totp)
            login =rh.login(variables.RH_Login, variables.RH_Pass, mfa_code=totp, store_session=True) 
            break
        except Exception as e:
            print(f"Buy order failed, retrying {retry_count} of {max_retries}")
            print(f"error details: {e}")
            retry_count += 1
    if retry_count == max_retries:
        print("Buy order failed after max retries")
    pass
    
def sell_order():
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            selling_power = crypto_positions[0]["quantity"]
            if (float(selling_power) > 3.01):
                requests.post(rh.orders.order_crypto(symbol='XLM', side='sell', quantityOrPrice=int(float(selling_power) - 3.00), amountIn='quantity', limitPrice=None, timeInForce='gtc', jsonify=True))
            totp = pyotp.TOTP(variables.MFA_Code).now()
            #print("Current OTP:", totp)
            login =rh.login(variables.RH_Login, variables.RH_Pass, mfa_code=totp, store_session=True) 
            break
        except Exception as e:
            print(f"Sell order failed, retrying {retry_count} of {max_retries}")
            print(f"error details: {e}")
            retry_count += 1
    if retry_count == max_retries:
        print("Sell order failed after max retries")
    pass

#####################
### loop the file ###
#####################

while True:
    sleep_first()

