from order import withdraw, get_balance, connect, get_portfolio
from logger import log
from utils import weights_to_percent
from config import addresses, weights
import time

asset = 'SNX'

connect()

balance = get_balance(asset)
if asset == 'BNB': balance -= 1 # leave some BNB so that we can make cheaper transactions

if balance > 0 and asset in addresses:
    withdraw(asset, addresses[asset], balance)

log('Getting your portfolio...')
portfolio_settings = weights_to_percent(weights)
portfolio = get_portfolio(portfolio_settings)
log('*** Portfolio ***')
for a, p in portfolio.items(): log('%s has %.2f, should have %.2f' % (a, p, portfolio_settings[a]))
log('***')

log('Done')

