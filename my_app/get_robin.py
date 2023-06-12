import robin_stocks.robinhood as rh
import variables
import pyotp

login = rh.login(variables.RH_Login, variables.RH_Pass, store_session=True)
totp = pyotp.TOTP("My2factorAppHere").now()
#print("Current OTP:", totp)

my_portfolio = rh.load_phoenix_account()
#print(my_portfolio)

portfolio_equity = my_portfolio["portfolio_equity"]["amount"]
print("Current portfolio value: $", portfolio_equity)

buying_power = my_portfolio["crypto_buying_power"]["amount"]
print("Crypto buying power: $", buying_power)

def buy_crypto(symbol, amount):
    buy = rh.order_buy_crypto_by_price(symbol, amount)
    print(buy)

def sell_crypto(symbol, amount):
    sell = rh.order_sell_crypto_by_price(symbol, amount)
    print(sell)

