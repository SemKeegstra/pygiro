# Packages:
from collections import OrderedDict

# Account Statement Related:
STATEMENT_COLS = ['date', 'time', 'currency_date', 'name', 'ISIN', 'description', 'FX', 'mutation', 'amount', 'currency', 'balance', 'order_id']
NUMERIC_COLS = ['FX', 'amount', 'balance']
LINE_TYPES = OrderedDict({
    'deposit': {'ideal deposit', 'sofort deposit'},
    'withdrawal': {'ideal withdrawal', 'sofort withdrawal'},
    'fx': {'valuta debitering', 'valuta creditering'},
    'sell': {'verkoop'},
    'buy': {'koop'},
    'dividend': {'dividend'},
    'interest': {'flatex interest income'},
    'rebate': {'verrekening promotie'},
    'cost': {'degiro transactiekosten', 'degiro aansluitingskosten', 'externe kosten', 'stamp duty'},
    'other': {}
})
