"""
Contains general growth rate class, and interest-discount conversion functions
"""


class GrowthRate:
    """
    valid pattern values should be:
    'i' or 'interest' - effective interest rate
    'd' or 'discount' - effective discount rate
    'im' or 'nomint' - nominal interest rate
    'dm' or 'nomdisc' - nominal discount rate
    'delta' or 'force' - force of interest
    """

    def __init__(
            self,
            rate: float = None,
            pattern: str = None,
            freq: float = None,
            interval: float = None,
            i: float,
            d: float,
            m:
    ):
        self.rate = rate
        self.pattern = pattern
        self.freq = freq
        self.interval = interval
