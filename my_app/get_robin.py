import robin_stocks.robinhood as rh
import variables
import pyotp

totp = pyotp.TOTP(variables.MFA_Code).now()
#print("Current OTP:", totp)
login =rh.login(variables.RH_Login, variables.RH_Pass, mfa_code=totp, store_session=True)


# Get values for useage in other scripts
my_portfolio = rh.load_phoenix_account()
#print(my_portfolio)

# Total portfolio value
portfolio_vlue = my_portfolio["portfolio_equity"]["amount"]
print("Current portfolio value: $", portfolio_vlue)
# Buying power
buying_power = my_portfolio["crypto_buying_power"]["amount"]
print("Crypto buying power: $", buying_power)
# Selling power
selling_power = my_portfolio["crypto"]["market_value"]["amount"]
print("Crypto selling power: $", selling_power)
