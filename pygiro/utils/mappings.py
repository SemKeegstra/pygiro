# Packages:
from collections import OrderedDict

# Account Statement Related:
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

# Something:
PANDAS_FREQ_MAPPING = dict(D='D', M='MS', Q='QS', A='YS')