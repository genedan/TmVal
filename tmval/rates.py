"""
Contains general growth rate class, and interest-discount conversion functions
"""

from typing import Union

from tmval.conversions import (
    any_from_eff_int,
    any_from_eff_disc,
    any_from_nom_int,
    any_from_nom_disc,
    any_from_delta,
    any_from_simp_int,
    any_from_simp_disc
)

from tmval.constants import (
    COMPOUNDS,
    FORMAL_PATTERNS,
    SIMPLES
)


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
            s: float = None,  # convenience argument for simple interest
            sd: float = None
    ):

        # check arguments

        convenience_types = [
            'i',
            'd',
            'delta',
            's',
            'sd'
        ]

        args = [
            rate,
            pattern,
            freq,
            interval,
            i,
            d,
            delta,
            s,
            sd
        ]
        arg_not_none = [x for x in args if x is not None]

        # if a convenience method is used, make sure they are the only argument supplied
        conveniences = [i for i in convenience_types if i in arg_not_none]
        if len(conveniences) > 1:
            raise Exception("You may only supply 1 of i, d, s, sd, or delta.")

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
            self.interval = 1

        elif sd is not None:
            self.rate = sd
            self.pattern = 'sd'
            self.interval = 1

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
            'Simple Interest',
            'Simple Discount',
            'sd',
            'simpdisc',
            'simple discount'
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

    # allow arithmetic operations using the rate attribute

    def __add__(self, other):
        return self.rate + other

    def __radd__(self, other):
        return other + self.rate

    def __sub__(self, other):
        return self.rate - other

    def __rsub__(self, other):
        return other - self.rate

    def __mul__(self, other):
        return self.rate * other

    def __rmul__(self, other):
        return other * self.rate

    def __truediv__(self, other):
        return self.rate / other

    def __rtruediv__(self, other):
        return other / self.rate

    def __pow__(self, other):
        return self.rate ** other

    def __rpow__(self, other):
        return other ** self.rate

    def __floordiv__(self, other):
        return self.rate // other

    def __rfloordiv__(self, other):
        return other // self.rate

    def __mod__(self, other):
        return self.rate % other

    def __rmod__(self, other):
        return other % self.rate

    def __neg__(self):
        return - self.rate

    def __pos__(self):
        return + self.rate

    def __abs__(self):
        return abs(self.rate)

    def __round__(self, ndigits):
        return round(self.rate, ndigits=ndigits)

    # relational comparisons

    def __eq__(self, other):
        # if not isinstance(other, Rate):
        #     raise TypeError("Comparisons only supported if both objects are type Rate.")
        if other is None:
            return False

        elif isinstance(other, float):
            self_std = self.standardize()
            if self_std.rate == other:
                return True
            else:
                return False

        elif isinstance(other, Rate):

            if self.formal_pattern in COMPOUNDS and other.formal_pattern in COMPOUNDS:

                self_std = self.convert_rate(
                    pattern="Effective Interest",
                    interval=1
                )

                other_std = other.convert_rate(
                    pattern="Effective Interest",
                    interval=1
                )

                if self_std.rate == other_std.rate:
                    return True
                else:
                    return False

            elif self.formal_pattern in SIMPLES and other.formal_pattern in SIMPLES:

                self_std = self.convert_rate(
                    pattern="Simple Interest",
                    interval=1
                )

                other_std = other.convert_rate(
                    pattern="Simple Interest",
                    interval=1
                )

                if self_std.rate == other_std.rate:
                    return True
                else:
                    return False

    def __gt__(self, other):
        if not isinstance(other, Rate):
            raise TypeError("Comparisons only supported if both objects are type Rate.")

        if self.formal_pattern in COMPOUNDS and other.formal_pattern in COMPOUNDS:

            self_std = self.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            return self_std.rate > other_std.rate

        elif self.formal_pattern in SIMPLES and other.formal_pattern in SIMPLES:

            self_std = self.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            return self_std.rate > other_std.rate
        else:
            raise TypeError("> only supported if both rates are compound or simple.")

    def __ge__(self, other):
        if not isinstance(other, Rate):
            raise TypeError("Comparisons only supported if both objects are type Rate.")

        if self.formal_pattern in COMPOUNDS and other.formal_pattern in COMPOUNDS:

            self_std = self.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            return self_std.rate >= other_std.rate

        elif self.formal_pattern in SIMPLES and other.formal_pattern in SIMPLES:

            self_std = self.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            return self_std.rate >= other_std.rate
        else:
            raise TypeError("> only supported if both rates are compound or simple.")

    def __lt__(self, other):
        if not isinstance(other, Rate):
            raise TypeError("Comparisons only supported if both objects are type Rate.")

        if self.formal_pattern in COMPOUNDS and other.formal_pattern in COMPOUNDS:

            self_std = self.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            return self_std.rate < other_std.rate

        elif self.formal_pattern in SIMPLES and other.formal_pattern in SIMPLES:

            self_std = self.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            return self_std.rate < other_std.rate
        else:
            raise TypeError("> only supported if both rates are compound or simple.")

    def __le__(self, other):
        if not isinstance(other, Rate):
            raise TypeError("Comparisons only supported if both objects are type Rate.")

        if self.formal_pattern in COMPOUNDS and other.formal_pattern in COMPOUNDS:

            self_std = self.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

            return self_std.rate <= other_std.rate

        elif self.formal_pattern in SIMPLES and other.formal_pattern in SIMPLES:

            self_std = self.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            other_std = other.convert_rate(
                pattern="Simple Interest",
                interval=1
            )

            return self_std.rate <= other_std.rate
        else:
            raise TypeError("> only supported if both rates are compound or simple.")

    def __ne__(self, other):
        return not self.__eq__(other)

    def convert_rate(
            self,
            pattern,
            freq: float = None,
            interval: float = None
    ):

        if FORMAL_PATTERNS[self.pattern] not in COMPOUNDS and pattern in COMPOUNDS:
            raise Exception("Simple interest/discount rate cannot be converted to compound patterns.")

        if FORMAL_PATTERNS[self.pattern] in COMPOUNDS and pattern in SIMPLES:
            raise Exception("Compound rate cannot be converted to simple patterns.")

        if (FORMAL_PATTERNS[self.pattern] in ['Simple Interest'] and pattern in ['Simple Discount']) or \
                (FORMAL_PATTERNS[self.pattern] in ['Simple Discount'] and pattern in ['Simple Interest']):

            raise Exception("Cannot convert between simple interest and simple discount.")

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
        elif FORMAL_PATTERNS[pattern] in ['Simple Interest', 'Simple Discount']:
            if interval is None:
                raise Exception("Must provide an interval for conversions to effective rates.")
            if freq is not None:
                raise Exception("Frequency only valid for conversions to nominal rates.")
        elif FORMAL_PATTERNS[pattern] in ['Force of Interest']:
            if freq is not None or interval is not None:
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

            template = any_from_simp_int(
                s=self.rate,
                old_t=self.interval,
                formal_pattern=pattern,
                interval=interval
            )

        elif self.formal_pattern == 'Simple Discount':

            template = any_from_simp_disc(
                d=self.rate,
                old_t=self.interval,
                formal_pattern=pattern,
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

        elif FORMAL_PATTERNS[self.pattern] in ['Simple Discount']:

            return k / (1 - self.rate / self. interval * t)

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

    def standardize(self):
        if self.formal_pattern in COMPOUNDS:
            rate = self.convert_rate(
                pattern="Effective Interest",
                interval=1
            )
        elif self.formal_pattern == "Simple Interest":
            rate = self.convert_rate(
                pattern="Simple Interest",
                interval=1
            )
        elif self.formal_pattern == "Simple Discount":
            rate = self.convert_rate(
                pattern="Simple Discount",
                interval=1
            )
        else:
            raise Exception("Unable to convert rate.")

        return rate


def standardize_rate(gr: Union[float, Rate]):
    if isinstance(gr, float):
        gr = Rate(gr)
    elif isinstance(gr, Rate):
        gr = gr.standardize()
    else:
        raise TypeError("Invalid type passed to gr, got ", str(type(gr)) + " instead. "
                        "You must supply a float or a Rate object to gr. ")

    return gr
