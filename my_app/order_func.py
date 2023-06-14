import get_robin
from strategy import trade_signals, DOGE_USD
import robin_stocks.robinhood as rh


# Create a function to execute buy orders
def buy_crypto(symbol, amount):
    """Executes a market order to buy a specified amount of a cryptocurrency.
    Args:
        symbol (str): A cryptocurrency ticker symbol.
        amount (float): The amount of the cryptocurrency to buy.
    Returns:
        dict: A dictionary containing information about your order.
    """
    try:
        order = rh.order_buy_crypto_by_price(symbol, amount)
        print("Order placed for {} {} at ${}.".format(symbol, amount, order["price"]))
        return order
    except Exception as e:
        print("Error: {}".format(e))
        return None
    
def sell_crypto(symbol, amount):
    """Executes a market order to sell a specified amount of a cryptocurrency.
    Args:
        symbol (str): A cryptocurrency ticker symbol.
        amount (float): The amount of the cryptocurrency to sell.
    Returns:
        dict: A dictionary containing information about your order.
    """
    try:
        order = rh.order_sell_crypto_by_price(symbol, amount)
        print("Order placed for {} {} at ${}.".format(symbol, amount, order["price"]))
        return order
    except Exception as e:
        print("Error: {}".format(e))
        return None
     
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
#print("Signal: {} | Last Trade: {}".format(signal["Signal"], last_trade))

