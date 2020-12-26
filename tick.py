from datetime import datetime
from config import script_root

def last_tick():
    filename = script_root + "tick.txt"
    last = None
    try:
        with open(filename, 'r') as fp:
            last_key = fp.read().strip()
            last = datetime.strptime(last_key, '%Y-%m-%d %H:%M:%S')
            return last
    except FileNotFoundError as e:
        last = None
    return last

def tick_weekly():
    t = last_tick()
    return t is None or t.isocalendar()[1] != datetime.now().isocalendar()[1]

def tick_touch():
    filename = script_root + "tick.txt"
    with open(filename, 'w') as fp:
        fp.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


