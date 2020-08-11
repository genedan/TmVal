"""
Contains general growth rate class, and interest-discount conversion functions
"""
from tmval.conversions import *
from tmval.constants import FORMAL_PATTERNS


class Rate:
    """
    valid pattern values should be:
    'i' or 'interest' - effective interest rate
    'd' or 'discount' - effective discount rate
    'im' or 'nomint' or APR - nominal interest rate
    'dm' or 'nomdisc' - nominal discount rate
    'delta' or 'force' - force of interest
    """

    def __init__(
            self,
            rate: float = None,
            pattern: str = None,
            freq: float = None,
            interval: float = None,
            i: float = None,  # convenience argument for effective 1-yr interest rate
            d: float = None,  # convenience argument for effective 1-yr discount rate
            delta: float = None,  # convenience argument for force of interest
            s: float = None # convenience argument for simple interest
    ):

        # check arguments

        convenience_types = [
            'i',
            'd',
            'delta',
            's'
        ]

        args = [
            rate,
            pattern,
            freq,
            interval,
            i,
            d,
            delta,
            s
        ]
        arg_not_none = [x for x in args if x is not None]

        # if a convenience method is used, make sure they are the only argument supplied
        conveniences = [i for i in convenience_types if i in arg_not_none]
        if len(conveniences) > 1:
            raise Exception("You may only supply 1 of i, d, s, or delta.")

        # handle convenience cases

        # effective interest
        # if rate is the only argument provided, compound effective interest with an interval of 1 year
        if rate is not None and arg_not_none == [rate]:
            self.rate = rate
            self.pattern = 'i'
            self.interval = 1

        elif i is not None:
            self.rate = i
            self.pattern = 'i'
            self.interval = 1

        # effective discount
        elif d is not None:
            self.rate = d
            self.pattern = 'd'
            self.interval = 1

        # force of interest
        elif delta is not None:
            self.rate = delta
            self.pattern = 'force'

        # simple interest
        elif s is not None:
            self.rate = s
            self.pattern = 's'
            self.interval =1

        else:
            self.rate = rate
            self.pattern = pattern
            self.freq = freq
            self.interval = interval

        self.formal_pattern = FORMAL_PATTERNS[self.pattern]

    def __repr__(self):

        effectives = [
            'interest',
            'discount',
            'i',
            'd',
            'APY',
            'Effective Interest',
            'Effective Discount'
        ]

        nominals = [
            'nomint',
            'nomdisc',
            'APR',
            'Nominal Interest',
            'Nominal Discount'
        ]

        simple = [
            's',
            'simp',
            'simple interest',
            'Simple Interest'
        ]

        if self.pattern in effectives:
            rep_str = 'Pattern: ' + self.formal_pattern + \
                      '\nRate: ' + str(self.rate) + \
                      '\nUnit of time: ' + str(self.interval) + ' year' + ('s' if self.interval != 1 else '')
        elif self.pattern in nominals:
            rep_str = 'Pattern: ' + self.formal_pattern + \
                      '\nRate: ' + str(self.rate) + \
                      '\nCompounding Frequency: ' + str(self.freq) + ' times per year'
        elif self.pattern in simple:
            rep_str = 'Pattern: ' + self.formal_pattern + \
                      '\nRate: ' + str(self.rate) + \
                      '\nUnit of time: ' + str(self.interval) + ' year' + ('s' if self.interval != 1 else '')
        else:
            rep_str = 'Pattern: Force of Interest' + \
                      '\nRate: ' + str(self.rate)

        return rep_str

    def convert_rate(
            self,
            pattern,
            freq: float = None,
            interval: float = None
    ):
        compounds = [
            'Effective Interest',
            'Effective Discount',
            'Nominal Interest',
            'Nominal Discount',
            'Force of Interest'
        ]

        simples = [
            'Simple Interest',
            'Simple Discount'
        ]

        if FORMAL_PATTERNS[self.pattern] not in compounds and pattern in compounds:
            raise Exception("Simple interest rate cannot be converted to compound patterns.")

        if FORMAL_PATTERNS[self.pattern] in compounds and pattern in simples:
            raise Exception("Compound rate cannot be converted to simple patterns.")

        if FORMAL_PATTERNS[pattern] in ['Effective Interest', 'Effective Discount']:
            if interval is None:
                raise Exception("Must provide an interval for conversions to effective rates.")
            if freq is not None:
                raise Exception("Frequency only valid for conversions to nominal rates.")
        elif FORMAL_PATTERNS[pattern] in ['Nominal Interest', 'Nominal Discount']:
            if freq is None:
                raise Exception("Must provide compounding frequency for conversions to nominal rates.")
            if interval is not None:
                raise Exception("Interval only valid for conversions to effective rates.")
        elif FORMAL_PATTERNS[pattern] in ['Simple Interest']:
            if interval is None:
                raise Exception("Must provide an interval for conversions to effective rates.")
            if freq is not None:
                raise Exception("Frequency only valid for conversions to nominal rates.")
        elif FORMAL_PATTERNS[pattern] in ['Force of Interest']:
            if freq is None or interval is None:
                raise Exception("Frequency or interval parameters are invalid for conversions to force of interest.")
            pass
        else:
            raise Exception("Invalid pattern provided.")

        if self.formal_pattern == 'Effective Interest':
            template = any_from_eff_int(
                i=self.rate,
                old_t=self.interval,
                formal_pattern=pattern,
                freq=freq,
                interval=interval
            )

        elif self.formal_pattern == 'Effective Discount':
            template = any_from_eff_disc(
                d=self.rate,
                old_t=self.interval,
                formal_pattern=pattern,
                freq=freq,
                interval=interval
            )

        elif self.formal_pattern == 'Nominal Interest':
            template = any_from_nom_int(
                im=self.rate,
                m=self.freq,
                formal_pattern=pattern,
                freq=freq,
                interval=interval
            )

        elif self.formal_pattern == 'Nominal Discount':
            template = any_from_nom_disc(
                dm=self.rate,
                m=self.freq,
                formal_pattern=pattern,
                freq=freq,
                interval=interval
            )

        elif self.formal_pattern == 'Force of Interest':
            template = any_from_delta(
                delta=self.rate,
                formal_pattern=pattern,
                freq=freq,
                interval=interval
            )
        elif self.formal_pattern == 'Simple Interest':
            rate = self.rate / self.interval * interval

            template = RateTemplate(
                rate=rate,
                formal_pattern='Simple Interest',
                interval=interval
            )

        else:
            raise Exception("Rate has an invalid formal pattern.")

        res = Rate(
            rate=template.rate,
            pattern=template.formal_pattern,
            freq=template.freq,
            interval=template.interval
        )

        return res

    def amt_func(self, k, t):

        if FORMAL_PATTERNS[self.pattern] in ['Simple Interest']:

            return k * (1 + self.rate / self.interval * t)

        elif FORMAL_PATTERNS[self.pattern] in [
            'Effective Interest',
            'Effective Discount',
            'Nominal Interest',
            'Nominal Discount',
            'Force of Interest'
        ]:
            i = self.convert_rate(
                pattern='Effective Interest',
                interval=1
            ).rate

            return k * ((1 + i) ** t)

    def acc_func(self, t):

        return self.amt_func(k=1, t=t)
