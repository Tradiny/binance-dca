from datetime import datetime
import os
script_root = os.path.dirname(os.path.abspath(__file__)) + '/'

def last_tick(key):
    filename = script_root + key +  "tick.txt"
    last = None
    try:
        with open(filename, 'r') as fp:
            last_key = fp.read().strip()
            last = datetime.strptime(last_key, '%Y-%m-%d %H:%M:%S')
            return last
    except FileNotFoundError as e:
        last = None
    return last

def tick(key):
    t = last_tick(key)
    if key == 'every_week':
        return t is None or t.isocalendar()[1] != datetime.now().isocalendar()[1]
    if key == 'every_month':
        return t is None or t.month != datetime.now().month
    if key == 'every_2nd_month':
        nmonth = t.month + 1
        if nmonth == 13: nmonth = 1
        return t is None or (t.month != datetime.now().month and nmonth != datetime.now().month)

def tick_touch(key):
    filename = script_root + key + "tick.txt"
    with open(filename, 'w') as fp:
        fp.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


