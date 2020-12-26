from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException
from logger import log
from math import floor, log10
from config import binance_config, debug
import os
script_root = os.path.dirname(os.path.abspath(__file__)) + '/'
import pickle
import os.path

if not os.path.exists(script_root + 'db.pickle'):
    pickle.dump({}, open(script_root + 'db.pickle', 'wb'))

def connect():
    global client

    log('*** For more trading tools, check out tradiny.com ***')

    log('Logging into Binance...')
    client = Client(binance_config['api_key'], binance_config['api_secret'])

prod = not debug

def to_binance_price(s, p):
    global client
    info = client.get_symbol_info(s)
    precision = info['baseAssetPrecision']
    for f in info['filters']:
        if f['filterType'] == 'LOT_SIZE' and 'stepSize' in f:
            stepSize = f['stepSize']
            e = abs(get_e(float(stepSize)))
            if e is not None and e < precision:
                precision = e
    p = format_price(p)
    if '.' in p:
        p = p.split('.')
        p[1] = p[1][:precision]
        p = '.'.join(p)
    return p

def buy(asset_from, asset_to, symbol, quantity):
    global client
    qty = to_binance_price(symbol, quantity)
    log('Buying %s %s' % (qty, asset_to))
    # place a test market buy order, to place an actual order use the create_order function
    if prod:
        try:
            order = client.order_market_buy(
                symbol=symbol,
                quantity=qty)
            log(str(order))
            return float(qty)
        except Exception as e:
            log('Failed to buy %s %f: %s' % (symbol, quantity, str(e)), 'error')
    return 0

def sell(asset_from, asset_to, symbol, quantity):
    global client
    qty = to_binance_price(symbol, quantity)
    log('Selling %s %s' % (qty, asset_from))
    # place a test market buy order, to place an actual order use the create_order function
    if prod:
        try:
            order = client.order_market_sell(
                symbol=symbol,
                quantity=qty)
            log(str(order))
            return float(qty)
        except Exception as e:
            log('Failed to sell %s %f: %s' % (symbol, quantity, str(e)), 'error')
    return 0

def withdraw(asset, address, amount):
    global client
    log('Withdrawing %s %s' % (asset, format_price(amount)))
    if prod:
        try:
            result = client.withdraw(
                asset=asset,
                address=address,
                amount=amount)

            pdb = pickle.load(open(script_root + 'db.pickle', 'rb'))
            if asset not in pdb: pdb[asset] = float(0)
            pdb[asset] += amount
            pickle.dump(pdb, open(script_root + 'db.pickle', 'wb'))
        except Exception as e:
            log('Failed to withdraw %s %f: %s' % (asset, amount, str(e)), 'error')
        else:
            log('Withdraw success %s %f' % (asset, amount))

def get_balance(asset):
    global client
    b = client.get_asset_balance(asset=asset)
    if b is None: return 0
    b = float(b['free'])
    # log('%s balance %f' % (asset, b))
    return b

def get_price(symbol):
    global client
    prices = client.get_all_tickers()
    for p in prices:
        if symbol == p['symbol']:
            return float(p['price'])
    return None

def to_currency(from_asset, to_asset, amount):
    p = find_pair(from_asset, to_asset)
    if p is not None:
        if p['direction'] == -1:
            price = get_price(p['symbol'])
            return amount * price
        if p['direction'] == 1:
            return amount
    return None

def set_portfolio_amount(a, amount):
    pdb = pickle.load(open(script_root + 'db.pickle', 'rb'))
    pdb[a] = amount
    pickle.dump(pdb, open(script_root + 'db.pickle', 'wb'))


def get_whole_portfolio():
    balances = {}
    pdb = pickle.load(open(script_root + 'db.pickle', 'rb'))
    for a, p in pdb.items():
        balances[a] = to_currency(a, 'USDT', pdb[a]) + to_currency(a, 'USDT', get_balance(a))
    sum_usdt = sum(balances.values())
    portfolio = {}
    for a, p in pdb.items():
        portfolio[a] = balances[a] * 100 / sum_usdt
    return portfolio


def get_portfolio(s):
    balances = {}
    pdb = pickle.load(open(script_root + 'db.pickle', 'rb'))
    for a, p in s.items():
        in_wallet = 0
        if a in pdb:
            in_wallet = pdb[a]
        balances[a] = to_currency(a, 'USDT', in_wallet) + to_currency(a, 'USDT', get_balance(a))
    sum_usdt = sum(balances.values())
    portfolio = {}
    for a, p in s.items():
        if sum_usdt != 0:
            portfolio[a] = balances[a] * 100 / sum_usdt
        else:
            portfolio[a] = 0
    return portfolio


def get_e(p):
    p = str(p)
    if 'e' in p:
        p = p.split('e')
        return int(p[1])
    elif '.' in p:
        p = p.split('.')
        return int(len(p[1]))
    else:
        return None

def format_price(porig):
    p = str(porig)
    if 'e' in p:
        p = p.split('e')
        p1 = p[0]
        p2 = int(p[1])
        p2e = '0' * abs(p2)
        if p2 < 0:
            p1 = p1.split('.')
            if len(p1[0]) < len(p2e):
                p = '0.' + ( '0' * (len(p2e) - len(p1[0]))) + p1[0] + p1[1]
            else:
                p = str(porig)
        if p2 > 0:
            p = p1 + p2e

    if p.endswith('.0'):
        p = p[:-2]

    return p

def percent(price, percent):
    return price * (float(percent) / 100)

def get_max_position(symbol, amount):
    price = get_price(symbol)
    return amount / price

def find_pair(asset1, asset2):
    global client
    symbol1 = asset1 + asset2
    symbol2 = asset2 + asset1
    info = client.get_exchange_info()
    symbols = info['symbols']
    for s in symbols:
        if s['symbol'] == symbol1:
            return {'symbol': symbol1, 'direction': -1, 'base_asset': s['baseAsset']}
        if s['symbol'] == symbol2:
            return {'symbol': symbol2, 'direction': 1, 'base_asset': s['baseAsset']}
    return None

def trade(asset_from, asset_to, amount_o):
    p = find_pair(asset_from, asset_to)

    if p is not None:

        if p['base_asset'] == amount_o['asset']:
            amount = amount_o['amount']
        else:
            amount = get_max_position(p['symbol'], percent(amount_o['amount'], 98))

        if p and p['direction'] == 1:
            return buy(asset_from, asset_to, p['symbol'], amount)
        if p and p['direction'] == -1:
            return sell(asset_from, asset_to, p['symbol'], amount)

    return None

def is_above_ema1d200(asset):
    global client
    p = find_pair(asset, 'USDT')
    if p is not None:

        klines = client.get_historical_klines(p['symbol'], Client.KLINE_INTERVAL_1DAY, "201 day ago UTC")
        close_prices = []
        for c in klines[-201:]:
            close_prices.append(float(c[4]))
        if len(close_prices) < 200: return None
        curprice = close_prices[-1]
        e = ema(close_prices, 200)
        ema_price = e[-1]
        res = curprice > ema_price

        if p['base_asset'] == asset:
            return res
        else:
            return not res
    return None

def ema(s, n):
    """
    returns an n period exponential moving average for
    the time series s

    s is a list ordered from oldest (index 0) to most
    recent (index -1)
    n is an integer

    returns a numeric array of the exponential
    moving average
    """
    ema = []
    j = 1

    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)

    return ema

# trade('EUR', 'BTC', {'amount': 0.000023, 'asset': 'BTC'})
# trade('BTC', 'EUR', {'amount': 10, 'asset': 'EUR'})

