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
            delta: float = None  # convenience argument for force of interest
    ):

        # check arguments
        convenience_types = ['i', 'd', 'delta']
        args = [rate, pattern, freq, interval, i, d, delta]
        arg_not_none = [x for x in args if x is not None]

        # if a convenience method is used, make sure they are the only argument supplied
        conveniences = [i for i in convenience_types if i in arg_not_none]
        if len(conveniences) > 1:
            raise Exception("You may only supply 1 of i, d, or delta.")

        # handle convenience cases

        # effective interest

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

        else:
            self.rate = rate
            self.pattern = pattern
            self.freq = freq
            self.interval = interval

        self.formal_pattern = FORMAL_PATTERNS[self.pattern]

    def __repr__(self):
        effectives = ['interest', 'discount', 'i', 'd', 'APY', 'Effective Interest', 'Effective Discount']
        nominals = ['nomint', 'nomdisc', 'APR', 'Nominal Interest', 'Nominal Discount']

        if self.pattern in effectives:
            rep_str = 'Pattern: ' + self.formal_pattern + \
                      '\nRate: ' + str(self.rate) + \
                      '\nUnit of time: ' + str(self.interval) + ' year' + ('s' if self.interval != 1 else '')
        elif self.pattern in nominals:
            rep_str = 'Pattern: ' + self.formal_pattern + \
                      '\nRate: ' + str(self.rate) + \
                      '\nCompounding Frequency: ' + str(self.freq) + ' times per year'
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
        else:
            raise Exception("Rate has an invalid formal pattern.")

        res = Rate(
            rate=template.rate,
            pattern=template.formal_pattern,
            freq=template.freq,
            interval=template.interval
        )

        return res
