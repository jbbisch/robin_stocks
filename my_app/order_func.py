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
        print("Order placed for {} {} at ${}.".format(amount, symbol, order["price"]))
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
        print("Order placed for {} {} at ${}.".format(amount, symbol, order["price"]))
        return order
    except Exception as e:
        print("Error: {}".format(e))
        return None
     
#Use the trade signals to execute orders
if trade_signals['Position'] == 1.0:
    buy_crypto(DOGE_USD, get_robin.buying_power)
elif trade_signals['Position'] == -1.0:
    sell_crypto(DOGE_USD, get_robin.selling_power)
else: trade_signals['Position'] == 0.0   