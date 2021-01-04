from order import trade, withdraw, get_balance, find_pair, connect, get_portfolio
from tick import tick_touch, tick
from logger import log, send_logged
from utils import order_assets_by_weights_and_usdt, set_amounts, weights_to_percent
from config import addresses, from_asset, debug, weights, to_email, withdraw_period
import time


if debug or tick('every_week'):
    tick_touch('every_week')

    connect()

    assets = order_assets_by_weights_and_usdt(weights)
    assets = set_amounts(from_asset, assets)

    for o in assets:
        asset = o['a']
        amount = o['amount']

        if amount > 0:

            log('Will buy asset %s with %.2f %s' % (asset, amount, from_asset))

            p = find_pair(from_asset, asset)
            if p is not None:
                amount = trade(from_asset, asset, {'amount': amount, 'asset': from_asset})
            else:
                amount = trade(from_asset, 'USDT', {'amount': amount, 'asset': from_asset})
                amount = trade('USDT', asset, {'amount': amount, 'asset': 'BTC'})


    if debug or withdraw_period == 'every_week' or tick(withdraw_period):
        tick_touch(withdraw_period)

        for o in assets:
            asset = o['a']
            amount = o['amount']

            balance = get_balance(asset)
            if asset == 'BNB': balance -= 1 # leave some BNB so that we can make cheaper transactions

            if balance > 0 and amount > 0 and asset in addresses:
                withdraw(asset, addresses[asset], balance)
                log('Sleeping 60s after withdrawal')
                time.sleep(60)

    log('Getting your portfolio...')
    portfolio_settings = weights_to_percent(weights)
    portfolio = get_portfolio(portfolio_settings)
    log('*** Portfolio ***')
    for a, p in portfolio.items(): log('%s has %.2f, should have %.2f' % (a, p, portfolio_settings[a]))
    log('***')

    log('Done')

    send_logged(to_email)



