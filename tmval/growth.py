from typing import Callable


class Amount:
    """
    Accepts an amount growth function and starting principal,
    can return valuation at time t and effective interest rate on an interval
    """
    def __init__(
            self,
            f: Callable,
            k: float
    ):
        self.func = f
        self.k = k

    def val(self, t):
        k = self.k
        return self.func(t=t, k=k)

    def interest_earned(
        self,
        t1,
        t2
    ):
        if t2 < t1:
            raise Exception("t2 must be greater than t1")
        if t1 < 0 or t2 < 0:
            raise Exception("each time period must be greater than 0")

        interest_earned = self.val(t=t2) - self.val(t=t1)
        return interest_earned

    def effective_interval(
            self,
            t1,
            t2
    ):
        k = self.k
        effective_rate = (self.val(t=t2) - self.val(t=t1)) / self.val(t=t1)
        return effective_rate

    def effective_rate(
            self,
            n
    ):
        t1 = n - 1
        t2 = n
        effective_rate = self.effective_interval(
            t1=t1,
            t2=t2
        )
        return effective_rate


class Accumulation(Amount):
    """
    Special case of Amount function where k=1,
    Accepts an accumulation growth function,
    can return valuation at time t and effective interest rate on an interval
    """
    def __init__(
        self,
        f: Callable,
    ):
        Amount.__init__(
            self,
            f,
            k=1
        )

    def val(self, t):
        return self.func(t=t)


class SimpleAmt(Amount):
    """
    Simple interest scenario, special case of amount function where growth function is linear
    """
    def __init__(
            self,
            k: float,
            s: float
    ):
        self.principal = k
        self.interest_rate = s

        Amount.__init__(
            self,
            f=self.amt_func,
            k=k
        )

    def amt_func(self, k, t):
        return k * (1 + self.interest_rate * t)


class SimpleAcc(Accumulation):
    """
        Simple interest scenario, special case of accumulation function where growth function is linear
        """
    def __init__(
            self,
            s: float
    ):
        self.interest_rate = s

        Accumulation.__init__(
            self,
            f=self.acc_func
        )

    def acc_func(self, t):
        return 1 + self.interest_rate * t

