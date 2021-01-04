from order import get_portfolio, connect
from utils import weights_to_percent
from config import weights
from logger import log

connect()
log('Getting your portfolio...')

portfolio_settings = weights_to_percent(weights)
portfolio = get_portfolio(portfolio_settings)
log('*** Portfolio ***')
for a, p in portfolio.items(): log('%s has %.2f, should have %.2f' % (a, p, portfolio_settings[a]))
log('***')

