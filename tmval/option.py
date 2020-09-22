from tmval.growth import Accumulation
from tmval.value import Payments


class Call:
    def __init__(
        self,
        n,
        k,
        t,
        s0=None,
        c0=None
    ):

        self.n = n
        self.k = k
        self.c0 = c0
        self.t = t
        self.s0 = s0

    def intrinsic_value(self, stp):
        return self.n * (stp - self.k)

    def time_premium(self, stp):
        return self.c0 - self.intrinsic_value(stp=stp)

    def yld(self, stp, t, x0=1.05):
        times = [0, t]
        amounts = [-self.c0, (stp - self.k) * self.n]

        pmts = Payments(
            times=times,
            amounts=amounts
        )

        return pmts.irr(x0=x0)

    def binomial_price(self, u, d, gr):
        rf_fac = Accumulation(gr=gr).val(self.t)
        vd = max(d - self.k, 0)
        vu = max(u - self.k, 0)
        c0 = (u * vd - d * vu) / ((u - d) * rf_fac) + (vu - vd) / (u - d) * self.s0
        return c0

    def binomial_d(self, u, gr):
        rf_fac = Accumulation(gr=gr).val(self.t)
        vu = max(u - self.k, 0)
        c0 = self.c0
        s0 = self.s0

        return (c0 * u - vu * s0) / (c0 - vu / rf_fac)


class Put:
    def __init__(
        self,
        n,
        k,
        price
    ):

        self.n = n
        self.k = k
        self.price = price

    def payoff(self, stp, cost):
        return self.n * max(stp, self.k) - self.price - cost
