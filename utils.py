from order import get_portfolio, get_balance, is_above_ema1d200
from config import penalization
from logger import log
import math

def weights_to_percent(weights):
    summed = sum(weights.values())
    percent = {}
    for a, w in weights.items():
        percent[a] = (100 * w / summed)
    return percent

def _order_assets_by_usdt(settings, portfolio):
    diffs = []
    for a, p in portfolio.items():
        diff = settings[a] - portfolio[a]
        diffs.append({
            'd': diff,
            'a': a,
            'should_have': settings[a],
            'has': portfolio[a]
        })
    suma = 0
    for d in diffs:
        if d['d'] > 0: suma += d['d']

    for d in diffs:
        if d['d'] > 0:
            d['multiplier'] = (d['d'] * 100 / suma) / 100
        else:
            d['multiplier'] = 0
    
    return sorted(diffs, key=lambda k: k['d'], reverse = True)

def order_assets_by_weights_and_usdt(weights, logging = True):

    portfolio_settings = weights_to_percent(weights)

    log('Getting your portfolio...')
    portfolio = get_portfolio(portfolio_settings)
    if logging:
        log('*** Portfolio ***')
        for a, p in portfolio.items(): log('%s has %.2f, should have %.2f' % (a, p, portfolio_settings[a]))
        log('***')

    return _order_assets_by_usdt(portfolio_settings, portfolio)

def set_amounts(from_asset, assets):

    balance = get_balance(from_asset)

    log('You have %.2f %s' % (balance, from_asset))
    saved = 0
    not_penalized = []
    above_ema_cached = {}
    for j in range(len(assets)):
        if 'amount' not in assets[j]: assets[j]['amount'] = 0
    for j in range(len(assets)):
        #j = i % len(assets)

        above_ema = None
        if assets[j]['a'] not in above_ema_cached:
            above_ema = is_above_ema1d200(assets[j]['a'])
            above_ema_cached[assets[j]['a']] = above_ema
        else:
            above_ema = above_ema_cached[assets[j]['a']]

        amount = balance * assets[j]['multiplier']
        if amount < 10: continue

        if above_ema is not None and above_ema:
            penalize = penalization / 100
            assets[j]['amount'] += amount * penalize
            saved += (amount - (amount * penalize))
        else:
            assets[j]['amount'] = amount
            if assets[j]['a'] not in not_penalized and amount > 0:
                not_penalized.append(assets[j]['a'])

    if len(not_penalized) > 0:
        saved_each = saved / len(not_penalized)
        for a in not_penalized:
            for j, ao in enumerate(assets):
                if ao['a'] == a:
                    assets[j]['amount'] += saved_each

    return assets


