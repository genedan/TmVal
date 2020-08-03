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

    def discount_func(self, t: float, fv: float = None) -> float:
        """
        The discount function is the reciprocal of the accumulation function. Returns the discount
        factor at time t, which can be used to get the present value of an investment.

        :param t: the time at which you would like to get the discount factor.
        :type t: float
        :param fv: float: the future value. Assumed to be 1 if not provided.
        :type fv: float, optional
        :return: the discount factor at time t
        :rtype: float
        """
        if fv is None:
            fv = 1

        return fv / self.val(t)

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


def get_simple_amt(
    pv: float = None,
    fv: float = None,
    s: float = None,
    t: float = None
) -> SimpleAmt:
    """
    Simple amount solver for when one variable is missing - returns a simple amount amount class

    :param pv: the present value of the investment
    :type pv: float
    :param fv: the future value of the investment
    :type fv: float
    :param s: the interest rate
    :type s: float
    :param t: the time of the investment
    :type t: float
    """
    args = [pv, fv, s, t]

    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if pv is None:
        pv = fv / (1 + t * s)
    elif s is None:
        s = (fv / pv - 1) / t
    else:
        pass

    simple_amt = SimpleAmt(k=pv, s=s)

    return simple_amt


def simple_solver(
    pv: float = None,
    fv: float = None,
    s: float = None,
    t: float = None
):
    """
    Simple interest solver for when one variable is missing - returns missing value. You need to supply
    three out of the four arguments, and the function will solve for the missing one.

    :param pv: the present value
    :type pv: float
    :param fv: the future value
    :type fv: float
    :param s: the interest rate
    :type s: float
    :param t: the time
    :type t: float
    :return: the present value, future value, interest rate, or time - whichever is missing.
    :rtype: float
    """
    args = [pv, fv, s, t]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if pv is None:
        res = fv / (1 + t * s)
    elif fv is None:
        res = pv * (1 + t * s)
    elif s is None:
        res = (fv / pv - 1) / t
    else:
        res = (fv / pv - 1) / s

    return res


def osi(
        beg_dt: dt.datetime,
        end_dt: dt.datetime,
        frac=True
) -> float:
    """
    Calculate the number of days using the ordinary simple interest or 30/360 rule.
    Set frac=True to return days as a percentage of year.

    :param beg_dt: beginning date
    :type beg_dt: datetime.datetime
    :param end_dt: ending date
    :type end_dt: datetime.datetime
    :param frac: whether you want the answer in number of days or fraction of a year, defaults to True
    :type frac: bool, optional
    :return: the number of days using the ordinary simple interest or 360 rule, or the percentage of year \
    if frac=True
    :rtype: float
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


def bankers_rule(
        beg_dt: dt.datetime,
        end_dt: dt.datetime,
        frac=True
) -> float:
    """
    Calculate the number of days using the Banker's rule or actual/360 rule.
    Set frac=True to return days as a percentage of year.

    :param beg_dt: the beginning date
    :type beg_dt: datetime.datetime
    :param end_dt: the ending date
    :type end_dt: datetime.datetime
    :param frac: whether you want the answer in number of days or fraction of a year, defaults to True
    :type frac: bool, optional
    :return: the number of days or percent of a year between two dates using the Banker's rule or actual/360 rule, \
    depending on frac
    :rtype: float
    """

    delta = end_dt - beg_dt

    days = delta.days

    if frac:
        return days / 360
    else:
        return days


class CompoundAmt(Amount):
    """
    Compound interest scenario, special case of amount function where amount function is geometric. \
    :class:`CompoundAmt` is a subclass of the :class:`Amount` class in the case of compound interest. If \
    your problem involves compound interest, you should probably use this class or the :class:`CompoundAcc` class
    instead of the more general classes of :class:`Amount` and :class:`Accumulation`.

    With this class, you do not need to supply a growth function, just pass an interest rate and and the growth \
    function will be constructed automatically.

    :param k: principal, or the initial investment.
    :type k: float
    :param i: the interest rate.
    :type i: float
    :return: a CompoundAmt object.
    :rtype: CompoundAmt
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
        """
        The amount function of the :class:`CompoundAmt` class.
        Automatically applied to the :class:`Amount` class
        by providing a compound growth function, instead of a user-defined one.

        :param k: the principal, or initial investment.
        :type k: float
        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of k at time t, invested at time 0.
        :rtype: float
        """
        return k * ((1 + self.interest_rate) ** t)


class CompoundAcc(Accumulation):
    """
    Compound interest scenario, special case of accumulation function where amount function is geometric.  \
    :class:`CompoundAcc` is a subclass of the :class:`Accumulation` class in the case of compound interest. If \
    your problem involves compound interest, you should probably use this class or the :class:`CompoundAmt` class
    instead of the more general classes of :class:`Amount` and :class:`Accumulation`.

    :param i: the interest rate.
    :type i: float
    :return: a CompoundAcc object.
    :rtype: CompoundAcc
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
    def discount_factor(self) -> float:
        discount_factor = 1 / (1 + self.interest_rate)
        return discount_factor

    def acc_func(self, t) -> float:
        """
        The accumulation function of the :class:`CompoundAcc` class.
        Automatically applied to the :class:`Accumulation` class
        by providing a compound growth function, instead of a user-defined one.

        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of 1 unit of currency at time t, invested at time 0.
        :rtype: float
        """
        return (1 + self.interest_rate) ** t


def compound_solver(
    pv: float = None,
    fv: float = None,
    i: float = None,
    t: float = None,
    m: int = None,
    use_apr: bool = False
):
    """
    Solves for a missing value in the case of compound interest supply 3/4 of: a present value, a future value \
    an interest rate (either APY or APR), and a time. If using an APR interest rate, you need to supply a compounding \
    frequency of m times per period, and you need to set the use_apr parameter to True.

    :param pv: the present value, defaults to None.
    :type pv: float
    :param fv: the future value, defaults to None.
    :type fv: float
    :param i: the interest rate, either in APY or APR form, defaults to None.
    :type i: float
    :param t: the time, defaults to None.
    :type t: float
    :param m: the compounding frequency, defaults to None.
    :type m: int, optional if using APY.
    :param use_apr: toggle to True if using APR, False otherwise, defaults to False.
    :type use_apr: bool, optional if using APY.
    :return: either a present value, a future value, an interest rate, or a time, depending on which one is missing.
    :rtype: float
    """

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
            res = nom_int_from_eff_int(i=res, new_m=m)
    else:
        res = np.log(fv / pv) / np.log(1 + i)

    return res


class TieredBal:
    """
    :class:`TieredBal` is a callable growth pattern for tiered investment accounts. A tiered investment account is one \
    where the interest paid varies depending on the balance. For example, 1% for the first $1000, 2% for the next \
    $4000, and 3% afterward.

    To create a :class:`TieredBal`, supply a list of tiers and a corresponding list of interest rates for those tiers. \
    The tiers are the lower bounds for the intervals corresponding to the interest rate (the first value will \
    usually be 0).

    :param tiers: a list of tiers, for example [0, 1000, 5000].
    :type tiers: list
    :param rates: a list of interest rates, for example [.01, .02, .03].
    :type rates: list
    :return: a TieredBal object.
    :rtype: TieredBal
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
    ) -> float:
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
    ) -> list:
        """
        Calculates the times at which the interest rate is expected to change for the account, assuming \
        an initial investment of k and no further investments.

        :param k: the principal, or initial investment.
        :type k: float
        :return: a list of times at which the interest rate is expected to change for the account.
        :rtype: list
        """
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
    :class:`TieredTime` is a callable growth pattern for investment accounts in which the interest rate can vary \
    depending on how long the account stays open. For example, 1% for the first year, 2% for the next \
    year, and 3% afterward.

    To create a :class:`TieredTime`, supply a list of tiers and a corresponding list of interest rates for those \
    tiers. The tiers are the lower bounds for the intervals corresponding to the interest rate (the first value will \
    usually be 0).

    :param tiers: a list of tiers, for example [0, 1, 2].
    :type tiers: list
    :param rates: a list of interest rates, for example [.01, .02, .03].
    :type rates: list
    :return: a TieredTime object.
    :rtype: TieredTime
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
    ) -> float:
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


def k_solver(
    f: Callable,
    fv: float,
    t: float
) -> float:
    """
    Solver to get the initial investment K, given a growth pattern and future value.

    :param f: the growth pattern.
    :type f: Callable
    :param fv: the future value.
    :type fv: float
    :param t: the time.
    :type t: float
    :return: the initial investment, K
    :rtype: float
    """
    res = fv / f(t)

    return res


def interest_from_discount(d: float) -> float:
    """
    An interest/discount rate converter. Returns the interest rate, given the discount rate.

    :param d: the discount rate.
    :type d: float
    :return: the interest rate.
    :rtype: float
    """
    i = d / (1 - d)

    return i


def discount_from_interest(i: float) -> float:
    """
    An interest/discount rate converter. Returns the discount rate, given the interest rate.

    :param i: the interest rate.
    :type i: float
    :return: the discount rate.
    :rtype: float
    """
    d = i / (1 + i)
    return d


class Payment:
    """
    A payment at a point in time. Has three attributes, the time of the payment, the payment amount, and the \
    discount factor, the last of which can be used to calculate the present value of the payment.

    :param time: the payment time.
    :type time: float
    :param amount: the payment amount.
    :type amount: float
    :param discount_factor: the discount factor.
    :type discount_factor: float, optional
    :return: a Payment object
    :rtype: Payment
    """
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
        times: list,
        amounts: list,
        discount_factors: list = None,
        discount_func: Callable = None,
        interest_rate: float = None,
        accumulation: Accumulation = None
) -> list:
    """
    Can be used to create a list of :class:`Payment` objects. Each payment attribute, the times, the amounts, and \
    the discount factors, can be supplied as lists where the same indices are used to match the attributes to the \
    payment. There are several options for supplying the discount, and supplying discount is optional.

    You can supply a set of discount factors as a list, a discount function, an interest rate, or an \
    :class:`accumulation` object that has its own discount function. However, you can only supply one of these \
    discount options.

    :param times: a list of payment times.
    :type times: list
    :param amounts: a list of payment amounts.
    :type amounts: list
    :param discount_factors: a list of discount factors, defaults to None.
    :type discount_factors: list, optional
    :param discount_func: a discount function, defaults to None.
    :type discount_func: Callable, optional
    :param interest_rate: an interest rate, defaults to None.
    :type interest_rate: float, optional
    :param accumulation: an :class:`Accumulation` object
    :return: a list of :class:`Payment` objects.
    :rtype: list
    """

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


def npv(
        payments: list,
        discount_func: Callable = None
) -> float:
    """
    Calculates the net present value for a stream of payments.

    :param payments: a list of :class:`Payment` objects.
    :type payments: list
    :param discount_func: a discount function.
    :type discount_func: Callable
    :return: the net present value
    :rtype: float
    """

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


def npv_solver(
        npval: float = None,
        payments: list = None,
        discount_func: Callable = None
):
    """
    An experimental net present value solver. Finds a missing component given a stream of payments and net present \
    value. For example, if the NPV is absent, but the rest of the payments are fully defined, this function \
    returns the NPV. If the NPV is provided, but one aspect of a payment (such as a payment value), this function \
    is planned to solve for that value.

    This function is still incomplete, please use with caution.

    :param npval: The net present value.
    :type npval: float
    :param payments: A list of payments.
    :type payments: list
    :param discount_func: A discount function.
    :type discount_func: Callable
    :return: Returns either the npv, a missing payment amount, a missing time of payment, or missing discount factor.
    :rtype: float
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
    """
    A special case of the :class:`Amount` class where discount is applied linearly. Note by discount, we mean \
    discounted interest, as in interest up front, which is not the same thing as the interest rate.

    :param k: the principal, or initial investment amount.
    :type k: float
    :param d: the discount rate.
    :type d: float
    :return: a :class:`SimpleDiscAmt` object
    :rtype: SimpDiscAmt
    """

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

    def amt_func(self, k: float, t: float) -> float:
        """
        The amount function of the :class:`SimpDiscAmt` class.
        Automatically applied to the :class:`Amount` class
        by providing a linear discount function, instead of a user-defined one.

        :param k: the principal, or initial investment.
        :type k: float
        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of k at time t, invested at time 0.
        :rtype: float
        """
        return k / (1 - self.discount_rate * t)


class SimpDiscAcc(Accumulation):
    """
    A special case of the :class:`Accumulation` class where discount is applied linearly. Note by discount, we mean \
    discounted interest, as in interest up front, which is not the same thing as the interest rate.

    :param d: the discount rate.
    :type d: float
    :return: a :class:`SimpDiscAcc` object
    :rtype: SimpDiscAcc
    """
    def __init__(
        self,
        d: float
    ):
        self.discount_rate = d

        Accumulation.__init__(
            self,
            f=self.acc_func
         )

    def acc_func(self, t: float) -> float:
        """
        The accumulation function of the :class:`SimpDiscAcc` class.
        Automatically applied to the :class:`Accumulation` class
        by providing a linear discount function, instead of a user-defined one.

        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of k at time t, invested at time 0.
        :rtype: float
        """
        return 1 / (1 - self.discount_rate * t)


class SimpleLoan:
    """
    A callable growth pattern for a simple loan, which is a lump sum loan to be paid back with a single payment \
    with interest, and possibly no explicit rate given. A common type of informal loan between two people outside the \
    banking system.

    You should supply a discount amount, a discount rate, but not both.

    :param principal: the initial investment.
    :type principal: float
    :param term: the term of the loan.
    :type term: float
    :param discount_amt: the discount amount, defaults to None.
    :type discount_amt: float
    :param discount_rate: the discount_rate, defaults to None.
    :type discount_rate: float
    :return: a :class:`SimpleLoan` object when initialized, the value when called.
    :rtype: SimpleLoan when initialized, float when called.
    """

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
    """
    A special case of the :class:`Amount` class where discount is compounded. Note by discount, we mean \
    discounted interest, as in interest up front, which is not the same thing as the interest rate.

    :param k: the principal, or initial investment amount.
    :type k: float
    :param d: the discount rate.
    :type d: float
    :return: a :class:`CompDiscAmt` object
    :rtype: CompDiscAmt
    """
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
        """
        The amount function of the :class:`CompDiscAmt` class.
        Automatically applied to the :class:`Amount` class
        by providing a linear compound function, instead of a user-defined one.

        :param k: the principal, or initial investment.
        :type k: float
        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of k at time t, invested at time 0.
        :rtype: float
        """
        return k * (1 - self.discount_rate) ** (-t)


class CompDiscAcc(Accumulation):
    """
    A special case of the :class:`Accumulation` class where discount is compounded. Note by discount, we mean \
    discounted interest, as in interest up front, which is not the same thing as the interest rate.

    :param d: the discount rate.
    :type d: float
    :return: a :class:`CompDiscAcc` object
    :rtype: CompDiscAcc
    """
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
        """
        The accumulation function of the :class:`CompDiscAcc` class.
        Automatically applied to the :class:`Accumulation` class
        by providing a compound growth function, instead of a user-defined one.

        :param t: the time as-of time for the valuation.
        :type t: float
        :return: the value of k at time t, invested at time 0.
        :rtype: float
        """
        return (1 - self.discount_rate) ** (-t)


def effective_from_nominal_int(
        nom: NominalInt = None,
        im: float = None,
        m: float = None
) -> float:
    """
    A nominal/effective interest rate converter. Given a :class:`.NominalInt` object, returns the
    effective interest rate. You may also supply the nominal interest rate and compounding frequency, but not when \
    a :class:`.NominalInt` is already supplied and vice-versa.

    :param nom: the nominal interest rate, as a NominalInt object.
    :type nom: NominalInt
    :param im: the nominal interest rate.
    :type im: float
    :param m: the compounding frequency.
    :type m: float
    :return: the effective interest rate.
    :rtype: float
    """

    if [im, m].count(None) != 2 and [im, m].count(None) > 0 and nom is None:
        raise Exception("When supplying the nominal interest rate as components, you must supply both the "
                        "nominal rate and compounding frequency, or you may supply a NominalInt object instead.")

    if nom is not None and [im, m].count(None) != 2:
        raise Exception("You may supply a NominalInt object, the components of a nominal interest rate, but not both.")

    if nom is not None:
        im = nom.val
        m = nom.m

    return (1 + im / m) ** m - 1


def effective_from_nominal_disc(
        nom: NominalDisc = None,
        dm: float = None,
        m: float = None
):

    if [dm, m].count(None) != 2 and [dm, m].count(None) > 0 and nom is None:
        raise Exception("When supplying the nominal discount rate as components, you must supply both the "
                        "nominal rate and compounding frequency, or you may supply a NominalDisc object instead.")

    if nom is not None and [dm, m].count(None) != 2:
        raise Exception("You may supply a NominalDisc object, the components of a nominal discount rate, but not both.")

    if nom is not None:
        dm = nom.val
        m = nom.m

    d = 1 - (1 - dm / m) ** m

    return d


def apy(im: float, m: float) -> float:
    """
    An alias for :func:`effective_from_nominal`. Returns annual percentage yield, or
    annual effective yield (APY), given a nominal rate of interest and compounding frequency.

    :param im: the nominal rate of interest
    :type im: float
    :param m: the compounding frequency, i.e., compounded m times per year
    :type m: float
    :return: the annual percentage yield, or annual effective yield (APY)
    :rtype: float
    """

    return effective_from_nominal_int(im=im, m=m)


def apr(i: float, m: float) -> NominalInt:
    """
    An alias for :func:`nominal_from_eff`. Returns annual percentage rate, or
    nominal interest rate (APR), given an effective rate of interest and compounding frequency
    of the desired nominal rate.

    :param i: the effective rate of interest
    :type i: float
    :param m: the desired compounding frequency, i.e., compounded m times per year
    :type m: float
    :return: the annual percentage rate, or nominal rate of interest (APR)
    :rtype: float
    """
    return nom_int_from_eff_int(i=i, new_m=m)


class NominalInt:

    def __init__(
        self,
        im: float,
        m: float
    ):
        self.val = im
        self.m = m

    def __str__(self):
        return "Nominal interest rate: " + str(self.val) + "\nCompounding Frequency: " + str(self.m)


class NominalDisc:

    def __init__(
        self,
        dm: float,
        m: float
    ):

        self.val = dm
        self.m = m

    def __str__(self):
        return "Nominal discount rate: " + str(self.val) + "\nCompounding Frequency: " + str(self.m)


# conversion formulas

def eff_int_from_eff_int(
        i: float,
        old_t: float,
        new_t: float
):
    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = (1 + i) ** (1 / old_t) - 1

    if new_t is not None:
        i = (1 + i) ** new_t - 1

    return i


def nom_int_from_eff_int(
        i: float,
        new_m: float,
        old_t: float = None
) -> NominalInt:
    """
    A nominal/effective interest rate converter. Given an effective interest rate and desired compounding frequency, \
    returns the nominal interest rate.

    :param i: the effective interest rate.
    :type i: float
    :param new_m: the desired compounding frequency.
    :type new_m: float,
    :param old_t: the interval of the effective interest rate. Assumed to be 1 if not provided.
    :type old_t: float, optional
    :return: the nominal interest rate.
    :rtype: NominalInt
    """
    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=old_t, new_t=1)

    im = new_m * ((1 + i) ** (1 / new_m) - 1)

    return NominalInt(im=im, m=new_m)


def eff_disc_from_eff_int(
        i: float,
        old_t: float = None,
        new_t: float = None
) -> float:

    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=old_t, new_t=1)

    d = discount_from_interest(i=i)

    # assume new interval is 1 if not specified
    if new_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=1, new_t=new_t)

    return d


def nom_disc_from_eff_int(
        i: float,
        m: float,
        old_t: float = None

) -> NominalDisc:
    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=old_t, new_t=1)

    d = discount_from_interest(i)

    nom = nom_disc_from_eff_disc(d=d, m=m)

    return nom


def eff_int_from_eff_disc(
        d: float,
        old_t: float = None,
        new_t: float = None
) -> float:
    # convert d to yearly effective if it is not already
    if old_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=old_t, new_t=1)

    i = interest_from_discount(d)

    # convert to new interval if given
    if new_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=1, new_t=new_t)

    return i


def nom_int_from_eff_disc(
        d: float,
        m: float,
        old_t: float = None
) -> NominalInt:

    # convert d to yearly effective if it is not already
    if old_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=old_t, new_t=1)

    i = interest_from_discount(d=d)

    im = nom_int_from_eff_int(i=i, new_m=m)

    return im


def eff_disc_from_eff_disc(
        d: float,
        old_t: float,
        new_t: float
):
    # first convert to single-period rate
    d1 = 1 - (1 - d) ** (1 / old_t)
    # then, convert to new interval
    new_d = 1 - ((1 - d1) ** new_t)

    return new_d


def nom_disc_from_eff_disc(
        d: float,
        m: float,
        old_t: float = None
):
    # convert d to yearly effective if it is not already

    if old_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=old_t, new_t=1)

    dm = m * (1 - (1 - d) ** (1 / m))

    nom = NominalDisc(dm=dm, m=m)

    return nom


def eff_int_from_nom_int(
        nom: NominalInt,
        new_t: float = None
):
    # get yearly rate first
    i = effective_from_nominal_int(nom=nom)

    if new_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=1, new_t=new_t)

    return i


def nom_int_from_nom_int(
        nom: NominalInt,
        new_m: float
) -> NominalInt:

    i = effective_from_nominal_int(nom=nom)

    new_nom = nom_int_from_eff_int(i=i, new_m=new_m)

    return new_nom


def eff_disc_from_nom_int(
    nom: NominalInt,
    new_t: float = None
) -> float:

    i = effective_from_nominal_int(nom=nom)
    d = discount_from_interest(i=i)

    if new_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=1, new_t=new_t)

    return d


def nom_disc_from_nom_int(
        nom_i: NominalInt,
        new_freq: float = None
) -> NominalDisc:

    if new_freq is None:
        new_freq = nom_i.m

    n = nom_i.m
    i_n = nom_i.val

    i = (1 + i_n / n) ** n - 1

    p = new_freq

    dp = 1 - i ** (-1 / p) * p

    nom_d = NominalDisc(dm=dp, m=p)

    return nom_d


def eff_int_from_nom_disc(
        nom: NominalDisc,
        new_t: float = None
) -> float:

    d = effective_from_nominal_disc(nom=nom)

    i = interest_from_discount(d)

    if new_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=1, new_t=new_t)

    return i


def nom_int_from_nom_disc(
        nom: NominalDisc,
        new_freq: float = None
) -> NominalInt:
    if new_freq is None:
        new_freq = nom.m

    p = nom.m
    dp = nom.val

    i = ((1 - dp / p) ** (-p)) - 1

    nom_i = nom_int_from_eff_int(i=i, new_m=new_freq)

    return nom_i


def eff_disc_from_nom_disc(
        nom: NominalDisc,
        new_t: float,
) -> float:

    d = effective_from_nominal_disc(nom=nom)

    if new_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=1, new_t=new_t)

    return d


def nom_disc_from_nom_disc(
        nom: NominalDisc,
        new_m: float
) -> NominalDisc:

    d = effective_from_nominal_disc(nom=nom)
    new_nom = nom_disc_from_eff_disc(d=d, m=new_m)

    return new_nom


def convert_rate(
        intdisc: str,
        effnom: str,
        freq: float = None,
        interval: float = None,
        i: float = None,
        d: float = None,
        nom_i: NominalInt = None,
        nom_d: NominalDisc = None,
        im: float = None,
        dm: float = None,
        m: float = None,
        t: float = 1
):
    """
    general interest-discount rate converter for nominal, effective, and multiple periods

    :return:
    """

    # check arguments

    if im is not None:
        nom_i = NominalInt(im=im, m=m)

    if dm is not None:
        nom_d = NominalDisc(dm=dm, m=m)

    # if interval not provided, assume 1
    if interval is None:
        interval = 1

    intdisc = intdisc
    effnom = effnom
    interval = interval

    if effnom == 'nominal':
        freq = freq
    else:
        freq = None

    if (i is not None) and (intdisc == 'interest') and (effnom == 'effective'):

        res = eff_int_from_eff_int(i=i, old_t=t, new_t=interval)

    elif (i is not None) and (intdisc == 'interest') and (effnom == 'nominal'):

        res = nom_int_from_eff_int(i=i, new_m=freq, old_t=t)

    elif (i is not None) and (intdisc == 'discount') and (effnom == 'effective'):

        res = eff_disc_from_eff_int(i=i, old_t=t, new_t=interval)

    elif (i is not None) and (intdisc == 'discount') and (effnom == 'nominal'):

        res = nom_disc_from_eff_int(i=i, m=freq, old_t=t)

    elif (d is not None) and (intdisc == 'interest') and (effnom == 'effective'):

        res = eff_int_from_eff_disc(d=d, old_t=t, new_t=interval)

    elif (d is not None) and (intdisc == 'interest') and (effnom == 'nominal'):

        res = nom_int_from_eff_disc(d=d, m=freq, old_t=t)

    elif (d is not None) and (intdisc == 'discount') and (effnom == 'effective'):

        res = eff_disc_from_eff_disc(d=d, old_t=t, new_t=interval)

    elif (d is not None) and (intdisc == 'discount') and (effnom == 'nominal'):

        res = nom_disc_from_eff_disc(d=d, m=freq, old_t=t)

    elif (nom_i is not None) and (intdisc == 'interest') and (effnom == 'effective'):

        res = eff_int_from_nom_int(nom=nom_i, new_t=interval)

    elif (nom_i is not None) and (intdisc == 'interest') and (effnom == 'nominal'):

        res = nom_int_from_nom_int(nom=nom_i, new_m=freq)

    elif (nom_i is not None) and (intdisc == 'discount') and (effnom == 'effective'):

        res = eff_disc_from_nom_int(nom=nom_i, new_t=interval)

    elif (nom_i is not None) and (intdisc == 'discount') and (effnom == 'nominal'):

        res = nom_disc_from_nom_int(nom_i=nom_i, new_freq=freq)

    elif (nom_d is not None) and (intdisc == 'interest') and (effnom == 'effective'):

        res = eff_int_from_nom_disc(nom=nom_d, new_t=freq)

    elif (nom_d is not None) and (intdisc == 'interest') and (effnom == 'nominal'):

        res = nom_int_from_nom_disc(nom=nom_d, new_freq=freq)

    elif (nom_d is not None) and (intdisc == 'discount') and (effnom == 'effective'):

        res = eff_disc_from_nom_disc(nom=nom_d, new_t=interval)

    elif (nom_d is not None) and (intdisc == 'discount') and (effnom == 'nominal'):

        res = nom_disc_from_nom_disc(nom=nom_d, new_m=freq)

    else:
        raise Exception("Conversion failed.")

    return res
