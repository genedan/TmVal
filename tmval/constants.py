BUILD_VERSION = '0.0.11'

FORMAL_PATTERNS = {
    'interest': 'Effective Interest',
    'i': 'Effective Interest',
    'APY': 'Effective Interest',
    'apy': 'Effective Interest',
    'Effective Interest': 'Effective Interest',

    'd': 'Effective Discount',
    'Effective Discount': 'Effective Discount',

    'nomint': 'Nominal Interest',
    'nominal interest': 'Nominal Interest',
    'APR': 'Nominal Interest',
    'apr': 'Nominal Interest',
    'Nominal Interest': 'Nominal Interest',

    'nomdisc': 'Nominal Discount',
    'nominal discount': 'Nominal Discount',
    'Nominal Discount': 'Nominal Discount',

    'delta': 'Force of Interest',
    'force': 'Force of Interest',
    'Force of Interest': 'Force of Interest',

    's': 'Simple Interest',
    'simple interest': 'Simple Interest',
    'simp': 'Simple Interest',
    'Simple Interest': 'Simple Interest',

    'Simple Discount': 'Simple Discount',
    'sd': 'Simple Discount',
    'simple discount': 'Simple Discount',
    'simpdisc': 'Simple Discount'
}


COMPOUNDS = [
            'Effective Interest',
            'Effective Discount',
            'Nominal Interest',
            'Nominal Discount',
            'Force of Interest'
        ]

SIMPLES = [
    'Simple Interest',
    'Simple Discount'
]

NOMINALS = [
    'Nominal Interest',
    'Nominal Discount'
]

EFFECTIVES = [
    'Effective Interest',
    'Effective Discount',
    'Simple Interest',
    'Simple Discount'
]