# Account Statement Related:
STATEMENT_COLS = ['date', 'time', 'currency_date', 'name', 'ISIN', 'description', 'FX', 'mutation', 'amount', 'currency', 'balance', 'order_id']
NUMERIC_COLS = ['FX', 'amount', 'balance']

LINE_TYPES = ['deposit', 'withdrawal', 'fx', 'cost', 'dividend', 'interest', 'rebate', 'sell', 'buy', 'other']
DEPOSITS = {'ideal deposit', 'sofort deposit'}
WITHDRAWALS = {'ideal withdrawal', 'sofort withdrawal'}
FX = {'valuta debitering', 'valuta creditering'}
SELL = {'verkoop'}
BUY = {'koop'}
DIVIDENDS = {'dividend'}
INTEREST = {'flatex interest income'}
REBATE = {'verrekening promotie'}
COSTS = {'degiro transactiekosten', 'degiro aansluitingskosten', 'externe kosten', 'stamp duty'}