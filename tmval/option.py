from tmval.value import Payments

class Call:
    def __init__(
        self,
        n,
        k,
        price,
    ):

        self.n = n
        self.k = k
        self.price = price

    def intrinsic_value(self, stp):
        return self.n * (stp - self.k)

    def time_premium(self, stp):
        return self.price - self.intrinsic_value(stp=stp)

    def yld(self, stp, t, x0=1.05):
        times = [0, t]
        amounts = [-self.price, (stp - self.k) * self.n]

        pmts = Payments(
            times=times,
            amounts=amounts
        )

        return pmts.irr(x0=x0)


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
