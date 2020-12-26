import logging
import smtplib
from config import script_root, gmail_user, gmail_password

logging.basicConfig(handlers=[logging.FileHandler(filename=script_root + "invest.log",
                                                 encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S", 
                    level=logging.DEBUG)

logged = ""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_log(s, t):
    if t == 'warning':
        print(bcolors.WARNING + s + bcolors.ENDC)
    elif t == 'error':
        print(bcolors.FAIL + s + bcolors.ENDC)
    elif t == 'critical':
        print(bcolors.FAIL + s + bcolors.ENDC)
    else:
        print(s)

def log(s, t = 'debug'):
    global logged

    print_log(s, t)
    logged += "%s\n" % s

    if t == 'debug':
        logging.debug(s)
    elif t == 'info':
        logging.info(s)
    elif t == 'warning':
        logging.warning(s)
    elif t == 'error':
        logging.error(s)
    elif t == 'critical':
        logging.critical(s)

def send_logged(email):
    global logged
    if gmail_user is not None:
        sent_from = gmail_user
        to = [email]
        subject = 'Invest log'
        body = logged

        email_text = """\
From: %s
To: %s
Subject: %s

%s
        """ % (sent_from, ", ".join(to), subject, body)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()

            server.login(gmail_user, gmail_password)

            server.sendmail(sent_from, to, email_text)
            server.close()
        except Exception as e:
            print('Error:', e)
    

