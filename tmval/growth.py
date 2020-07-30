"""
Contains general growth functions implemented as Amount and Accumulation classes.
The simple and compound interest cases are represented as subclasses SimpleAmt and CompoundAmt, respectively.
"""

import datetime as dt
import numpy as np
import warnings

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

    def discount_interval(
        self,
        t1,
        t2
    ):

        discount_rate = (self.val(t=t2) - self.val(t=t1)) / self.val(t=t2)
        return discount_rate

    def effective_discount(
        self,
        n
    ):
        t1 = n - 1
        t2 = n
        effective_discount = self.discount_interval(
            t1=t1,
            t2=t2
        )
        return effective_discount

    def get_accumulation(self):
        amt_func = self.func

        def acc_func(t):
            return amt_func(k=1, t=t)

        accumulation = Accumulation(f=acc_func)
        return accumulation


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

    def discount_func(self, t):
        return 1 / self.val(t)

    def future_principal(self, fv, t1, t2):
        """
        Finds the principal needed at t1 to get fv at t2

        :param fv: future value
        :param t1: time of investment
        :param t2: time of goal
        :return: amount of money needed at t1 to get fv at t2
        """

        future_principal = fv * self.discount_func(t2) * self.val(t1)

        return future_principal

    def npv(self, payments: list):
        discount_func = self.discount_func

        res = npv(payments=payments, discount_func=discount_func)

        return res


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


def get_simple_amt(pv=None, fv=None, interest=None, n=None):
    """
    Simple amount solver for when one variable is missing - returns a simple amount growth class
    """
    args = [pv, fv, interest, n]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if pv is None:
        pv = fv / (1 + n * interest)
    elif fv is None:
        fv = pv * (1 + n * interest)
    elif interest is None:
        interest = (fv / pv - 1) / n
    else:
        pass

    simple_amt = SimpleAmt(k=pv, s=interest)

    return simple_amt


def simple_solver(pv=None, fv=None, s=None, n=None):
    """
        Simple amount solver for when one variable is missing - returns missing value
        """
    args = [pv, fv, s, n]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if pv is None:
        res = fv / (1 + n * s)
    elif fv is None:
        res = pv * (1 + n * s)
    elif s is None:
        res = (fv / pv - 1) / n
    else:
        res = (fv / pv - 1) / s

    return res


def osi(beg_dt: dt.datetime, end_dt: dt.datetime, frac=True):
    """
    Calculate the number of days using the ordinary simple interest or 30/360 rule.
    Set frac=True to return days as a percentage of year.
    """

    y1 = beg_dt.year
    y2 = end_dt.year

    m1 = beg_dt.month
    m2 = end_dt.month

    d1 = beg_dt.day
    d2 = end_dt.day

    days = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)

    if frac:
        return days / 360
    else:
        return days


def bankers_rule(beg_dt: dt.datetime, end_dt: dt.datetime, frac=True):
    """
    Calculate the number of days using the Banker's rule or actual/360 rule.
    Set frac=True to return days as a percentage of year
    """

    delta = end_dt - beg_dt

    days = delta.days

    if frac:
        return days / 360
    else:
        return days


class CompoundAmt(Amount):
    """
    Compound interest scenario, special case of amount function where growth function is geometric
    """
    def __init__(
            self,
            k: float,
            i: float
    ):
        self.principal = k
        self.interest_rate = i

        Amount.__init__(
            self,
            f=self.amt_func,
            k=k
        )

    def amt_func(self, k, t):
        return k * ((1 + self.interest_rate) ** t)


class CompoundAcc(Accumulation):
    """
    Compound interest scenario, special case of accumulation function where growth function is geometric
    """
    def __init__(
            self,
            i: float
    ):
        self.interest_rate = i

        Accumulation.__init__(
            self,
            f=self.acc_func
        )

    @property
    def discount_factor(self):
        discount_factor = 1 / (1 + self.interest_rate)
        return discount_factor

    def acc_func(self, t):
        return (1 + self.interest_rate) ** t


def compound_solver(pv=None, fv=None, i=None, t=None):

    args = [pv, fv, i, t]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if pv is None:
        res = fv / ((1 + i) ** t)
    elif fv is None:
        res = pv * ((1 + i) ** t)
    elif i is None:
        res = ((fv / pv) ** (1 / t)) - 1
    else:
        res = np.log(fv / pv) / np.log(1 + i)

    return res


class TieredBal:
    """
    Tiered investment account
    """
    def __init__(
        self,
        tiers: list,
        rates: list
    ):
        self.tiers = tiers
        self.rates = rates

    def __call__(
        self,
        k: float,
        t: float
    ):
        # determine jump balances and rates
        jump_balances = [i for i in self.tiers if i > k]
        if len(jump_balances) == 0:
            jump_rates = []
        else:
            jump_rates = self.rates[:len(self.rates) - 1]
            jump_rates = jump_rates[-len(jump_balances):]

        # determine jump times
        jump_times = []
        pv = k
        t_base = 0
        for fv, i in zip(jump_balances, jump_rates):
            jump_increment = compound_solver(pv=pv, fv=fv, i=i)
            jump_times.append(t_base + jump_increment)
            t_base = t_base + jump_increment
            pv = fv

        # find applicable tiers
        jump_times.insert(0, 0)
        jump_rates = self.rates[-len(jump_times):]
        jump_tiers = self.tiers[-len(jump_times):]

        # construct growth function and calculate balance
        index = len([i for i in jump_times if i <= t]) - 1
        lower_t = jump_times[index]
        base_amt = max(jump_tiers[index], k)
        rate = jump_rates[index]
        time = t - lower_t

        bal = base_amt * ((1 + rate) ** time)

        return bal


class TieredTime:
    """
    Tiered time investment account. Interest varies with time.
    """

    def __init__(
            self,
            tiers: list,
            rates: list
    ):
        self.tiers = tiers
        self.rates = rates

    def __call__(
            self,
            k: float,
            t: float
    ):
        # find the cumulative tiers that apply at time t
        jump_times = np.cumsum(self.tiers)
        jump_times = [i for i in jump_times if i < t]

        rates = self.rates[:len(jump_times)]
        times = self.tiers[:len(jump_times)]
        times.pop(0)
        times.append(t - max(jump_times))

        # for each tier that applies, calculate the cumulative balance
        bal = k
        for rate, time in zip(rates, times):
            bal = bal * ((1 + rate) ** time)

        return bal


def k_solver(f: Callable, fv=None, t=None):
    res = fv / f(t)
    return res


def interest_from_discount(d):
    i = d / (1 - d)
    return i


def discount_from_interest(i):
    d = i / (1 + i)
    return d


class Payment:
    def __init__(
        self,
        time,
        amount,
        discount_factor
    ):
        self.time = time
        self.amount = amount
        self.discount_factor = discount_factor


def create_payments(times: list, amounts: list, discount_factors: list = None, discount_function: Callable = None):

    if not (len(times) == len(amounts)):
        raise Exception("Times and amounts must be the same length.")

    if discount_factors:
        if not (len(times) == len(amounts) == len(discount_factors)):
            raise Exception("Each argument must be the same length.")

    if [discount_factors, discount_function].count(None) == 0:
        raise Exception("You may supply a list of discount factors, a discount function, but not both.")

    if discount_function:
        discount_factors = [discount_function(x) for x in times]

    if (discount_factors is None) and (discount_function is None):
        discount_factors = [None] * len(amounts)

    payments = []

    for time, amount, discount_factor in zip(times, amounts, discount_factors):
        payment = Payment(
            time=time,
            amount=amount,
            discount_factor=discount_factor
        )
        payments.append(payment)

    return payments


def npv(payments: list, discount_func: Callable):

    factor_none = [x.discount_factor for x in payments].count(None)

    if (factor_none != len(payments)) and discount_func:
        warnings.warn("When discount factors are supplied with a discount function, "
                      "the discount function will override the discount factors.")

    payment_amounts = [x.amount for x in payments]

    payment_times = [x.time for x in payments]

    if discount_func:
        factors = [discount_func(t) for t in payment_times]
    else:
        factors = [x.discount_factor for x in payments]

    res = sum([a * b for a, b in zip(payment_amounts, factors)])

    return res


def npv_solver(npval: float = None, payments: list = None, discount_func: Callable = None):
    """

    :param npval: The net present value.
    :param payments: A list of payments
    :param discount_func: A discount function
    :return: Returns either the npv, a missing payment amount, a missing time of payment, or missing discount factor
    """

    args = [npval, payments, discount_func]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if npval is None:
        res = npv(payments=payments, discount_func=discount_func)

    # exclude missing payment

    payments_excl_missing = [x for x in payments if x.time is not None]
    missing_pmt = [x for x in payments if x.time is None].pop()
    payments_excl_missing_npv = npv(payments=payments_excl_missing, discount_func=discount_func)

    missing_pmt_pv = npval - payments_excl_missing_npv
    res = np.log(missing_pmt.amount / missing_pmt_pv) / np.log(discount_func(1) ** -1)

    return res
