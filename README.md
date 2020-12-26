# Binance Dollar Cost Averaging with trend penalization

This is a tool/script that automatically buys crypto assets based on defined portfolio and sends the assets into your wallets each week.

## Requirements

It uses Binance ( https://www.binance.com/en ) to buy the crypto assets. You can configure a standing order in your bank account to periodically deposit money. This tool handles the rest.

You also need a computer where the script will be running. We suggest to use Raspberry Pi. We also suggest to use a Ledger hardware wallet to secure your funds.

## How the algorithm works?

You can specify weights for your assets as follows:

```
BTC: 100
ETH: 50
```

These are translated into percentages as follows:

```
BTC: 66%
ETH: 33%
```

If the system detects funds in a fiat currency or any other (you can specify this in variable `from_asset`), the algorithm starts buying assets:

* that have lower percent proportion in your portfolio than the calculated percentage above.

For example, if you deposit 200 euros, the system will use the following algorithm to balance the deposited euros:

The system buys the calculated percentage of the deposited euros if the amount of BTC in your portfolio is less than 66% and:

1. The asset is below EMA 200 1d
2. Or there is not enough data to calculate EMA 200 1d

The system applies a penalization mechanism if the asset is above EMA 200 1d.

The penalization is 50% of the percentage (can be specified in the `penalization` variable).

For example, if your deposit is 200 euros and the percentage based on your weights is 66%, which is 132 euros, and the asset price is above EMA 200 1d, then the 50% penalization applies to this asset, so the system buys the asset with `132 * 0.5 = 66` euros. The other 66 euros are distributed equally to the assets, which prices are below EMA 200 1d.

The idea behind this is that if the asset is in a downtrend (defined by the EMA), we buy more of the asset at a discounted price to maximize profits.

The assets are withdrawn into your wallets (variable `addresses`). We suggest to use Ledger hardware wallet addresses.

## Setup

You need to create file `config.py` with your configuration (and replace `PATH-TO-PROJECT`):

```
binance_config = {
    'api_key': 'YOUR BINANCE API KEY',
    'api_secret': 'YOUR BINANCE API SECRET'
}

addresses = {
    'BTC': 'YOUR BTC WITHDRAWAL ADDRESS',
    'ETH': 'YOUR ETH WITHDRAWAL ADDRESS'
}

from_asset = 'EUR'
weights = {
    'BTC': 100,
    'ETH': 50,
    'XRP': 5 # if the withdrawal address is not specified for this asset, then the funds are not withdrawn
}
penalization = 50

gmail_user = 'YOUR GMAIL ADDRESS' # set to None if you want to disable this
gmail_password = 'YOUR GMAIL PASSWORD'
to_email = 'EMAIL ADDRESS WHERE THE SYSTEM SENDS LOGS'

debug = False
script_root = '/PATH-TO-PROJECT/' # where the script is located
```

### Binance setup

You need to do a bit of configuration on Binance:

1. Add all your addresses into a white list ( https://www.binance.com/en/my/security/address-management )
2. After creating your API keys ( https://www.binance.com/en/my/settings/api-management ), you need to enable withdrawals for trusted IPs (you can find out your IP at https://whatismyipaddress.com/ )

### Gmail setup

The logs are sent from a gmail account. To enable this feature you need to allow Less secure apps at https://support.google.com/accounts/answer/6010255?hl=en
We suggest to create a new gmail account for this purpose.

## Installation

Install the python packages:

```
pip3 install -r requirements.txt
```

## First run

Deposit your asset and run:

```
python3 run.py
```

## Automation

Add a cron job (replace `PATH-TO-PROJECT`):

```
* * * * * /usr/bin/python3 /PATH-TO-PROJECT/run.py  >> /tmp/invest-cron.log
```

Or run in bash after boot:

```
nohup bash -c "while [ 1 ]; do /usr/bin/python3 /PATH-TO-PROJECT/run.py  >> /tmp/invest-cron.log; sleep 60; done" &
```

## Author

https://tradiny.com

If you find this script useful, please consider joining our trading community at tradiny.com


