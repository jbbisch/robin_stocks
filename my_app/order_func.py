import get_robin
from strategy import trade_signals, DOGE_USD
import robin_stocks.robinhood as rh

# Path: robin_stocks-1\my_app\order_func.py
# Create a function to execute a buy order
def buy_crypto(DOGE_USD, buying_power):
    # Get the current price of DOGE
    current_price = DOGE_USD["Close"].iloc[-1]
    # Execute the buy order
    rh.order_buy_crypto_by_price(symbol=DOGE_USD, amountInDollars=buying_power)
    # Print the current price and the amount purchased
    print("Buying DOGE at: $", current_price)
    print("Bought: ", buying_power)

# Create a function to execute a sell order
def sell_crypto(DOGE_USD, selling_power):
    # Get the current price of DOGE
    current_price = DOGE_USD["Close"].iloc[-1]
    # Execute the sell order
    rh.order_sell_crypto_by_price(symbol=DOGE_USD, amountInDollars=selling_power)
    # Print the current price and the amount sold
    print("Selling DOGE at: $", current_price)
    print("Sold: ", selling_power)
     
# Create a variable to keep track of the last trade
last_trade = None

# Loop through the trade signals
for index, signal in trade_signals.iterrows():
    # If the last trade was a buy order, check if we should sell
    if last_trade == "buy":
        # If the signal is 0, execute a sell order
        if signal["Signal"] == 0:
            sell_crypto(DOGE_USD, get_robin.selling_power)
            last_trade = "sell"
    # If the last trade was a sell order, check if we should buy
    elif last_trade == "sell":
        # If the signal is 1, execute a buy order
        if signal["Signal"] == 1:
            buy_crypto(DOGE_USD, get_robin.buying_power)
            last_trade = "buy"
    # If we haven't made a trade yet, check if we should buy
    elif last_trade is None:
        # If the signal is 1, execute a buy order
        if signal["Signal"] == 1:
            buy_crypto(DOGE_USD, get_robin.buying_power)
            last_trade = "buy"
# Print the current signal and last trade
print("Signal: {} | Last Trade: {}".format(signal["Signal"], last_trade))

