"""
Contains general amount functions implemented as Amount and Accumulation classes.
The simple and compound interest cases are represented as subclasses SimpleAmt and CompoundAmt, respectively.
"""
from __future__ import annotations

import datetime as dt
import numpy as np
import warnings

from typing import Callable


class Amount:
    """
    The Amount class is an implementation of the amount function, which describes how much an invested
    amount of money grows over time.

    The amount function's methods can return things like the valuation of an investment after a
    specified time, and effective interest and discount rates over an interval.

    The accumulation function, which is a special case of the amount function where k=1, can be extracted
    from the amount function using the get_accumulation() method.


    :param f: a amount function, which must take the parameters t for time and k for principal.
    :type f: Callable
    :param k: the principal, or initial investment.
    :type k: float

    :return: An amount object, which can be used like an amount function in interest theory.
    :rtype: Amount

    """
    def __init__(
            self,
            f: Callable,
            k: float
    ):
        self.func = f
        self.k = k

    def val(self, t: float) -> float:
        """
        Calculates the value of the investment at a point in time.

        :param t:evaluation date. The date at which you would like to know the value of the investment.
        :type t: float
        :return: the value of the investment at time t.
        :rtype: float
        """
        k = self.k
        return self.func(t=t, k=k)

    def interest_earned(
        self,
        t1: float,
        t2: float
    ) -> float:
        """
        Calculates the amount of interest earned over a time period.

        :param t1: beginning of the period.
        :type t1: float
        :param t2: end of the period.
        :type t2: float
        :return: The amount of interest earned over the time period.
        :rtype: float
        """
        if t2 < t1:
            raise Exception("t2 must be greater than t1")
        if t1 < 0 or t2 < 0:
            raise Exception("each time period must be greater than 0")

        interest_earned = self.val(t=t2) - self.val(t=t1)
        return interest_earned

    def effective_interval(
            self,
            t1: float,
            t2: float
    ) -> float:
        """
        Calculates the effective interest rate over a time period.

        :param t1: the beginning of the period.
        :type t1: float
        :param t2: the end of the period.
        :type t2: float
        :return: the effective interest rate over the time period.
        :rtype: float
        """
        effective_rate = (self.val(t=t2) - self.val(t=t1)) / self.val(t=t1)
        return effective_rate

    def effective_rate(
            self,
            n: int
    ) -> float:
        """
        Calculates the effective interest rate for the n-th time period.

        :param n: the n-th time period.
        :type n: int
        :return: the effective interest rate for the n-th timer period.
        :rtype: float
        """
        t1 = n - 1
        t2 = n
        effective_rate = self.effective_interval(
            t1=t1,
            t2=t2
        )
        return effective_rate

    def discount_interval(
        self,
        t1: float,
        t2: float
    ) -> float:
        """
        Calculates the effective discount rate over a time period.

        :param t1: the beginning of the time period.
        :type t1: float
        :param t2: the end of the time period.
        :type t2: float
        :return: the effective discount rate over the time period.
        :rtype: float
        """

        discount_rate = (self.val(t=t2) - self.val(t=t1)) / self.val(t=t2)
        return discount_rate

    def effective_discount(
        self,
        n: int
    ) -> float:
        """
        Calculates the effective discount rate for the n-th time period.

        :param n: the n-th time period.
        :type n: int
        :return: the effective discount rate for the n-th time period.
        :rtype: float
        """
        t1 = n - 1
        t2 = n
        effective_discount = self.discount_interval(
            t1=t1,
            t2=t2
        )
        return effective_discount

    def get_accumulation(self) -> Accumulation:
        """
        Extracts the :term:`accumulation function`, a special case of the amount function where k=1.

        :return: the accumulation function.
        :rtype: Accumulation
        """
        amt_func = self.func

        def acc_func(t):
            return amt_func(k=1, t=t)

        accumulation = Accumulation(f=acc_func)
        return accumulation


class Accumulation(Amount):
    """
    Special case of Amount function where k=1,
    Accepts an accumulation amount function,
    can return valuation at time t and effective interest rate on an interval

    :param f: a function or callable that must take a single parameter, the time t.
    :type f: Callable
    :return: an accumulation object.
    :rtype: Accumulation
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

    def val(self, t: float) -> float:
        """
        Calculates the value of the investment at a point in time.

        :param t: evaluation date. The date at which you would like to know the value of the investment.
        :type t: float
        :return: the value of the investment at time t.
        :rtype: float
        """
        return self.func(t=t)

    def discount_func(self, t: float) -> float:
        """
        The discount function is the reciprocal of the accumulation function. Returns the discount
        factor at time t, which can be used to get the present value of an investment.

        :param t: the time at which you would like to get the discount factor.
        :type t: float
        :return: the discount factor at time t
        :rtype: float
        """
        return 1 / self.val(t)

    def future_principal(
            self,
            fv: float,
            t1: float,
            t2: float
    ) -> float:
        """
        Finds the principal needed at t1 to get fv at t2.

        :param fv: future value.
        :type fv: float
        :param t1: time of investment.
        :type t1: float
        :param t2: time of goal.
        :type t2: float
        :return: amount of money needed at t1 to get fv at t2.
        :rtype: float
        """

        future_principal = fv * self.discount_func(t2) * self.val(t1)

        return future_principal

    def npv(
            self,
            payments: list
    ) -> float:
        """
        Returns the net present value of a given list of payments.

        :param payments: a list of payment objects.
        :type payments: list
        :return: the net present value of the payments.
        """
        discount_func = self.discount_func

        res = npv(payments=payments, discount_func=discount_func)

        return res


class SimpleAmt(Amount):
    """
    The ``SimpleAmt`` class is a subclass of the :class:`Amount` class, where the amount function is linear.

    :param k: the principal, or initial investment amount.
    :type k: float
    :param s: the interest rate.
    :type s: float
    :return: a SimpleAmt object
    :rtype: SimpleAmt
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

    def amt_func(self, k: float, t: float) -> float:
        """
        The amount function of the :class:`SimpleAmt` class.
        Automatically applied to the :class:`Amount` class
        by providing a linear growth function, instead of a user-defined one.

        :param k: the principal, or initial investment.
        :type k: float
        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of k at time t, invested at time 0.
        :rtype: float
        """

        return k * (1 + self.interest_rate * t)


class SimpleAcc(Accumulation):
    """
    The ``SimpleAcc`` class is a subclass of the :class:`Accumulation` class where the amount function is linear,
    i.e., the simple interest scenario. It can also be thought of as a special case of :class:`SimpleAmt` where
    k=1, although technically it inherits from :class:`Accumulation` directly.

    :param s: the interest rate
    :type s: float
    :return: a SimpleAcc object
    :rtype: SimpleAcc

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

    def acc_func(self, t: float) -> float:
        """
        The accumulation function of the :class:`SimpleAcc` class.
        Automatically applied to the :class:`Accumulation` class
        by providing a linear growth function, instead of a user-defined one.

        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of 1 unit of currency at time t, invested at time 0.
        :rtype: float
        """
        return 1 + self.interest_rate * t


def get_simple_amt(pv=None, fv=None, interest=None, n=None):
    """
    Simple amount solver for when one variable is missing - returns a simple amount amount class
    """
    args = [pv, fv, interest, n]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if pv is None:
        pv = fv / (1 + n * interest)
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
    Compound interest scenario, special case of amount function where amount function is geometric
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
    Compound interest scenario, special case of accumulation function where amount function is geometric
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


def compound_solver(pv=None, fv=None, i=None, t=None, m=None, use_apr: bool = False):

    args = [pv, fv, i, t]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if pv is None:
        res = fv / ((1 + i) ** t)
    elif fv is None:
        res = pv * ((1 + i) ** t)
    elif i is None:
        # get the effective rate first
        res = ((fv / pv) ** (1 / t)) - 1
        # convert to nominal if use_apr is true
        if use_apr:
            res = nominal_from_eff(i=res, m=m)
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
        jump_times = self.get_jump_times(k=k)

        # find applicable tiers
        jump_times.insert(0, 0)
        jump_rates = self.rates[-len(jump_times):]
        jump_tiers = self.tiers[-len(jump_times):]

        # construct amount function and calculate balance
        index = len([i for i in jump_times if i <= t]) - 1
        lower_t = jump_times[index]
        base_amt = max(jump_tiers[index], k)
        rate = jump_rates[index]
        time = t - lower_t

        bal = base_amt * ((1 + rate) ** time)

        return bal

    def get_jump_times(
        self,
        k: float,
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

        return jump_times


class TieredTime:
    """
    Tiered time investment account. Interest varies with time.
    """

    def __init__(
            self,
            tiers: list,
            rates: list,
            frequencies: list = None,
            use_apr: bool = False
    ):
        self.tiers = tiers
        if use_apr:
            self.rates = [apy(x, m) for x, m in zip(rates, frequencies)]
        else:
            self.rates = rates

    def __call__(
            self,
            k: float,
            t: float
    ):
        # find the cumulative tiers that apply at time t
        jump_times = self.tiers
        jump_times = [i for i in jump_times if i < t]

        rates = self.rates[:len(jump_times)]
        times = jump_times[:len(jump_times)]
        times.append(t)
        times = np.diff(times)

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


def create_payments(
        times: list, amounts: list,
        discount_factors: list = None,
        discount_func: Callable = None,
        interest_rate: float = None,
        accumulation: Accumulation = None
) -> list:

    if not (len(times) == len(amounts)):
        raise Exception("Times and amounts must be the same length.")

    if discount_factors:
        if not (len(times) == len(amounts) == len(discount_factors)):
            raise Exception("Each argument must be the same length.")

    disc_args = [discount_factors, discount_func, interest_rate, accumulation]

    if disc_args.count(None) < (len(disc_args) - 1):
        raise Exception("You may supply a list of discount factors, a discount function, "
                        "an interest rate, an amount object, but only one of these.")

    if discount_func:
        discount_factors = [discount_func(x) for x in times]

    if interest_rate is not None:
        discount_factors = [(1 + interest_rate) ** (-x) for x in times]

    if accumulation:
        discount_factors = [accumulation.discount_func(x) for x in times]

    if (discount_factors is None) and (discount_func is None):
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


def npv(payments: list, discount_func: Callable = None):

    factor_none = [x.discount_factor for x in payments].count(None)

    if (factor_none != len(payments)) and discount_func:
        warnings.warn("When discount factors are supplied with a discount function, "
                      "the discount function will override the discount factors.")

    if (factor_none != 0) and discount_func is None:
        raise Exception("There is at least one missing discount factor. "
                        "Either supply the missing factors or supply a discount function instead.")

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

    # exclude missing payment

    payments_excl_missing = [x for x in payments if x.time is not None]
    missing_pmt = [x for x in payments if x.time is None].pop()
    payments_excl_missing_npv = npv(payments=payments_excl_missing, discount_func=discount_func)

    missing_pmt_pv = npval - payments_excl_missing_npv
    res = np.log(missing_pmt.amount / missing_pmt_pv) / np.log(discount_func(1) ** -1)

    return res


class SimpDiscAmt(Amount):

    def __init__(
        self,
        k: float,
        d: float
    ):
        self.principal = k
        self.discount_rate = d

        Amount.__init__(
            self,
            f=self.amt_func,
            k=k
        )

    def amt_func(self, k, t):
        return k / (1 - self.discount_rate * t)


class SimpDiscAcc(Accumulation):

    def __init__(
        self,
        d: float
    ):
        self.discount_rate = d

        Accumulation.__init__(
            self,
            f=self.acc_func
         )

    def acc_func(self, t):
        return 1 / (1 - self.discount_rate * t)


class SimpleLoan:

    def __init__(
        self,
        principal: float,
        term: float,
        discount_amt: float = None,
        discount_rate: float = None
    ):
        if [discount_amt, discount_rate].count(None) == 0:
            raise Exception("May supply discount amount, discount rate, but not both.")

        if [discount_amt, discount_rate].count(None) == 2:
            raise Exception("Please supply either a discount amount or rate.")

        self.principal = principal
        if discount_rate is not None:
            self.discount_rate = discount_rate
            self.discount_amt = principal * discount_rate
        else:
            self.discount_amt = discount_amt
            self.discount_rate = discount_amt / principal

        self.amount_available = principal - discount_amt
        self.term = term

    def __call__(
        self,
        k: float,
        t: float
    ) -> float:

        if not ((t == 0) or (t == self.term)):
            raise Exception("Simple loan has no meaning outside of origination or termination date.")

        if t == 0:
            return k - self.discount_amt

        if t == self.term:
            return k


class CompDiscAmt(Amount):

    def __init__(
        self,
        k: float,
        d: float
    ):
        self.principal = k
        self.discount_rate = d

        Amount.__init__(
            self,
            f=self.amt_func,
            k=k
        )

    def amt_func(self, k, t):
        return k * (1 - self.discount_rate) ** (-t)


class CompDiscAcc(Accumulation):

    def __init__(
        self,
        d: float
    ):
        self.discount_rate = d

        Accumulation.__init__(
            self,
            f=self.acc_func
         )

    def acc_func(self, t):
        return (1 - self.discount_rate) ** (-t)


def effective_from_nominal(im: float, m: int) -> float:

    return (1 + im / m) ** m - 1


def nominal_from_eff(i: float, m: int) -> float:

    return m * ((1 + i) ** (1 / m) - 1)


def apy(im: float, m: int) -> float:
    """
    An alias for :function:`effective_from_nominal`. Returns annual percentage yield, or
    annual effective yield (APY), given a nominal rate of interest and compounding frequency.

    :param im: the nominal rate of interest
    :type im: float
    :param m: the compounding frequency, i.e., compounded m times per year
    :type m: int
    :return: the annual percentage yield, or annual effective yield (APY)
    :rtype: float
    """

    return effective_from_nominal(im=im, m=m)


def apr(i: float, m: int) -> float:
    """
        An alias for :function:`nominal_from_eff`. Returns annual percentage rate, or
        nominal interest rate (APR), given an effective rate of interest and compounding frequency
        of the desired nominal rate.

        :param i: the effective rate of interest
        :type i: float
        :param m: the desired compounding frequency, i.e., compounded m times per year
        :type m: int
        :return: the annual percentage rate, or nominal rate of interest (APR)
        :rtype: float
        """
    return nominal_from_eff(i=i, m=m)
