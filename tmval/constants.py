"""
This file contains aliases and other values that might be referenced throughout the package, such as the build version.
"""

# The build version is referenced by the setup file and documentation.
BUILD_VERSION = '0.0.12'

# Formal patterns refer to canonical names of different types of growth rates and their aliases.
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

# Various names to refer to compound growth rates.
COMPOUNDS = [
            'Effective Interest',
            'Effective Discount',
            'Nominal Interest',
            'Nominal Discount',
            'Force of Interest'
        ]

# Various names to refer to simple growth rates.
SIMPLES = [
    'Simple Interest',
    'Simple Discount'
]

# Various names to refer to nominal growth rates.
NOMINALS = [
    'Nominal Interest',
    'Nominal Discount'
]

# Various names to refer to effective growth rates.
EFFECTIVES = [
    'Effective Interest',
    'Effective Discount',
    'Simple Interest',
    'Simple Discount'
]