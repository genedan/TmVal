"""
Contains general amount functions implemented as Amount and Accumulation classes.
The simple and compound interest cases are represented as subclasses SimpleAmt and CompoundAmt, respectively.
"""
from __future__ import annotations

import datetime as dt
import numpy as np

from dateutil.relativedelta import relativedelta
from inspect import signature
from numpy import ndarray
from scipy.misc import derivative
from scipy.optimize import newton
from typing import Callable, Iterable, Tuple, Union

from tmval.constants import COMPOUNDS, SIMPLES
from tmval.rate import Rate, standardize_rate


class Amount:
    """
    The Amount class is an implementation of the amount function, which describes how much an invested
    amount of money grows over time.

    The amount function's methods can return things like the valuation of an investment after a
    specified time, and effective interest and discount rates over an interval.

    The accumulation function, which is a special case of the amount function where k=1, can be extracted
    from the amount function using the get_accumulation() method.


    :param gr: a growth object, which can either be a function that must take the parameters t \
    for time and k for principal, or a Rate object representing an interest rate.
    :type gr: Callable, float, Rate
    :param k: the principal, or initial investment.
    :type k: float

    :return: An amount object, which can be used like an amount function in interest theory.
    :rtype: Amount

    """
    def __init__(
            self,
            gr: Union[Callable, Rate, float],
            k: float
    ):
        self.gr = gr
        self.func = self._extract_func()
        self.k = k
        self._validate_func()
        self.is_compound = self.__is_compound()
        if self.is_compound:
            self.interest_rate = self.effective_rate(1)

        self.is_level = self.__check_level()

    def _extract_func(self) -> Callable:

        if isinstance(self.gr, Callable):
            return self.gr
        elif isinstance(self.gr, (float, Rate)):
            return standardize_rate(self.gr).amt_func
        else:
            raise Exception("Growth object must be a callable or Rate object.")

    def _validate_func(self):
        """
        Check if func object is properly formed.
        """
        sig = signature(self.func)

        # check return type
        # if not isinstance(sig.return_annotation, float):
        #     raise TypeError("Growth function must return a float, got type " + str(sig.return_annotation))

        # check arguments
        if 'k' not in sig.parameters:
            raise Exception("Growth function must take a parameter k for the principal.")

        if 't' not in sig.parameters:
            raise Exception("Growth function must take a parameter t for time.")

    def __is_compound(self):
        if isinstance(self.gr, float):
            return True

        elif isinstance(self.gr, Rate) and self.gr.formal_pattern in COMPOUNDS:
            return True

        elif isinstance(self.gr, Callable):
            for i in range(10):
                try:
                    cond = round(self.val(i) / self.val(i - 1), 5) != round(self.val(i + 1) / self.val(i), 5)
                except ValueError:
                    return False
                except ZeroDivisionError:
                    return False
                if cond:
                    return False
                else:
                    continue

            return True
        else:
            return False

    def __check_level(self):
        """
        Checks if the interest rate is the same for up to 100 periods
        :return:
        :rtype:
        """
        if isinstance(self.gr, float):
            return True
        elif isinstance(self.gr, Rate) and self.gr.formal_pattern in COMPOUNDS:
            return True
        elif isinstance(self.gr, Rate) and self.gr.formal_pattern in SIMPLES:
            return False
        elif isinstance(self.gr, (TieredBal, TieredTime, SimpleLoan)):
            return False
        elif isinstance(self.gr, Callable):
            try:
                rates = [round(self.effective_rate(x + 1), 5) for x in range(100)]
            except (ZeroDivisionError, OverflowError):
                return False
            return rates[1:] == rates[:-1]

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
            t2: float,
            t1: float = 0,
            annualized: bool = False
    ) -> Rate:
        """
        Calculates the effective interest rate over a time period.

        :param t1: the beginning of the period.
        :type t1: float
        :param t2: the end of the period.
        :type t2: float
        :return: the effective interest rate over the time period.
        :rtype: float
        :param annualized: whether you want the results to be annualized.
        :rtype annualized: bool
        """

        interval = t2 - t1
        effective_rate = (self.val(t=t2) - self.val(t=t1)) / self.val(t=t1)

        effective_rate = Rate(
            rate=effective_rate,
            pattern="Effective Interest",
            interval=interval
        )

        if annualized:
            effective_rate = effective_rate.standardize()

        return effective_rate

    def effective_rate(
            self,
            n: Union[float, int]
    ) -> Rate:
        """
        Calculates the effective interest rate for the n-th time period.

        :param n: the n-th time period.
        :type n: float, int
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

        accumulation = Accumulation(gr=acc_func)
        return accumulation

    def solve_t(self, fv, pv=None, x0=range(100), precision=5):

        if pv is None:
            t0 = 0
        else:
            def f0(t):
                return pv - self.val(t)
            rs = newton(f0, x0=x0)
            if isinstance(rs, Iterable):
                t0 = list(set([round(x, precision) for x in rs]))[0]
            else:
                t0 = rs

        def f1(t):
            return fv - self.val(t)

        rs = newton(f1, x0=x0)
        if isinstance(rs, Iterable):
            t1 = list(set([round(x, precision) for x in rs]))[0]
        else:
            t1 = rs

        return t1 - t0


class Accumulation(Amount):
    """
    Special case of Amount function where k=1,
    Accepts an accumulation amount function,
    can return valuation at time t and effective interest rate on an interval

    :param gr: a growth object, which can either be a function that must take the parameters t \
    for time and k for principal, or a Rate object representing an interest rate.
    :type gr: Callable, float, Rate
    :return: an accumulation object.
    :rtype: Accumulation
    """
    def __init__(
        self,
        gr: Union[Callable, float, Rate]
    ):
        super().__init__(
            gr=gr,
            k=1
        )

        self.gr = gr
        self.func = self._extract_func()

    def _extract_func(self):

        if isinstance(self.gr, Callable):
            params = signature(self.gr).parameters

            if 'k' in params:
                def f(t: float) -> float:
                    return self.gr(t=t, k=1)
            else:
                f = self.gr

            return f

        elif isinstance(self.gr, (float, Rate)):
            return standardize_rate(self.gr).acc_func
        else:
            raise Exception("Growth object must be a callable or Rate object.")

    def _validate_func(self):
        """
        Check if func object is properly formed.
        """
        sig = signature(self.func)

        # check return type
        # if sig.return_annotation != 'float':
        #     raise TypeError("Growth function must return a float, got type " + str(sig.return_annotation))

        # check arguments

        if 't' not in sig.parameters:
            raise Exception("Growth function must take a parameter t for time.")

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

    def discount_amt(self, t: float, fv: float = None) -> float:

        pv = self.discount_func(fv=fv, t=t)

        return fv - pv

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

    def delta_t(self, t):
        if self.is_compound:
            delta_t = self.interest_rate.convert_rate(pattern="Force of Interest")
        else:
            # PyCharm seems gives a warning expecting type function, even when the argument is callable
            # noinspection PyTypeChecker
            delta_t = derivative(func=self.func, x0=t, dx=1e-6) / self.func(t)

        return delta_t

    def solve_t(self, pv, fv, x0=10):

        def f(t0):
            return self.val(t0) - fv / pv

        roots = newton(func=f, x0=x0)
        if isinstance(roots, ndarray):
            pass
        else:
            roots = np.array(roots)
        reals = roots[np.isreal(roots)]
        res = round(reals[0])

        return res


def simple_solver(
    pv: float = None,
    fv: float = None,
    gr: Union[float, Rate] = None,
    t: float = None,
    rate_res="Simple Interest",
):
    """
    Simple interest solver for when one variable is missing - returns missing value. You need to supply
    three out of the four arguments, and the function will solve for the missing one.

    :param pv: the present value
    :type pv: float
    :param fv: the future value
    :type fv: float
    :param gr: the interest rate
    :type gr: float, Rate
    :param t: the time
    :type t: float
    :param rate_res: if solving for a rate, whether you want simple discount or interest
    :type rate_res: str
    :return: the present value, future value, interest rate, or time - whichever is missing.
    :rtype: float, Rate
    """
    args = [pv, fv, gr, t]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if gr is not None:
        if isinstance(gr, float):
            gr = Rate(s=gr)
        elif isinstance(gr, Rate):
            gr = gr.standardize()
        else:
            raise TypeError("Invalid type passed to s.")

    if pv is None:
        res = fv / (1 + t * gr)

    elif fv is None:

        if gr.pattern == "Simple Interest":
            res = pv * (1 + t * gr)
        elif gr.pattern == "Simple Discount":
            res = pv / (1 - t * gr)
        else:
            raise ValueError("Invalid interest rate pattern passed to argument gr.")

    elif gr is None:
        if rate_res == "Simple Interest":
            res = (fv / pv - 1) / t
            res = Rate(s=res)
        elif rate_res == "Simple Discount":
            res = (1 - pv / fv) / t
            res = Rate(sd=res)
        else:
            raise ValueError("Invalid value passed to rate_res.")
    else:
        res = (fv / pv - 1) / gr

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


def actual_actual(
        beg_dt: dt.datetime,
        end_dt: dt.datetime,
        frac=True
):

    if not frac:
        return (end_dt - beg_dt).days
    else:
        years = relativedelta(end_dt, beg_dt).years
        print(years)
        intermediate = dt.datetime(beg_dt.year + 1, end_dt.month, end_dt.day)
        print(intermediate)
        days = (intermediate - beg_dt).days
        print(days)

        t = years + days / 365

        return t


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


def compound_solver(
    pv: float = None,
    fv: float = None,
    t: float = None,
    gr: Union[float, Rate] = None
):
    """
    Solves for a missing value in the case of compound interest supply 3/4 of: a present value, a future value \
    an interest rate (either APY or APR), and a time. If using an APR interest rate, you need to supply a compounding \
    frequency of m times per period, and you need to set the use_apr parameter to True.

    :param pv: the present value, defaults to None.
    :type pv: float
    :param fv: the future value, defaults to None.
    :type fv: float
    :param t: the time, defaults to None.
    :type t: float
    :type gr: a general growth rate.
    :type gr: Rate
    :return: either a present value, a future value, an interest rate, or a time, depending on which one is missing.
    :rtype: float
    """

    args = [pv, fv, gr, t]

    if args.count(None) > 1:
        raise Exception("You are missing either a present value (pv), future value(fv), "
                        "time (t), or growth rate.")

    if gr:
        i = standardize_rate(gr)

    else:
        i = None

    if pv is None:
        res = fv / ((1 + i) ** t)
    elif fv is None:
        res = pv * ((1 + i) ** t)
    elif gr is None:
        # get the effective rate first
        res = ((fv / pv) ** (1 / t)) - 1
        res = Rate(res)
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
            jump_increment = compound_solver(pv=pv, fv=fv, gr=Rate(i))
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
    ):
        self.tiers = tiers
        rates_std = []
        for x in rates:
            if isinstance(x, Rate):
                pass
            elif isinstance(x, float):
                x = Rate(x)
            else:
                raise TypeError("Invalid type passed to rates, \
                use either a list of floats or Rate objects.")

            rates_std.append(x)

        self.rates = rates_std

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

            rate = standardize_rate(gr=rate)
            bal = bal * rate.amt_func(k=1, t=time)

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

        self.amount_available = principal - self.discount_amt
        self.term = term

    def __call__(
        self,
        k: float,
        t: float
    ) -> float:

        if not ((t == 0) or (t == self.term)):
            raise ValueError("Simple loan has no meaning outside of origination or termination date.")

        if t == 0:
            return k - self.discount_amt

        if t == self.term:
            return k


def simple_interval_solver(
    s: float,
    es: float
) -> float:
    """
    Finds the interval at which the simple interest rate equals es

    :param s: A simple interest rate.
    :type s: float
    :param es: The desired simple interest rate.
    :type es: float
    :return: The desired interval.
    :rtype: float
    """

    return 1 / es + 1 - 1 / s


def standardize_acc(
        gr: Union[
            Accumulation,
            float,
            Rate,
            TieredTime
        ]
) -> Accumulation:

    """
    Returns an compound accumulation object. Usually used to enable more complex classes and functions to accept
    several different objects to indicate a compound interest growth rate.

    :param gr: A growth rate object.
    :type gr: Accumulation, float, Rate, or TieredTime
    :return: an Accumulation object
    :rtype: Accumulation
    """

    if isinstance(
        gr,
        Accumulation
    ):
        if not gr.is_compound:
            raise TypeError("Standardization of Accumulation class only valid for compound interest.")
        else:
            pass
    elif isinstance(gr, (float, Rate, TieredTime)):
        gr = Accumulation(gr)
    else:
        raise TypeError("Invalid type passed to gr.")

    return gr


def tt_iym(
    table: dict,
    t0: float
) -> TieredTime:
    """
    Reads an investment year method table and returns a TieredTime object. This object can then be passed to
    an Amount or an Accumulation class to represent a series of interest rates applicable to an investment.
    A table might look something like this:

    iym_table = {
    2000: [.06, .065, .0575, .06, .065],
    2001: [.07, .0625, .06, .07, .0675],
    2002: [.06, .06, .0725, .07, .0725],
    2003: [.0775, .08, .08, .0775, .0715]
    }

    :param table: A table of interest rates.
    :type table: dict
    :param t0: The year of the initial investment.
    :type t0: float
    :return: A TieredTime growth rate object.
    :rtype: TieredTime
    """

    # move to the right for each row in year t
    n_col = len(table[t0])
    # move downwards for each row greater than t
    n_row = max(table.keys()) - t0
    n_tiers = n_col + n_row
    tiers = [x for x in range(n_tiers)]
    rates = table[t0]

    # get the ultimate rates from the last column in the table
    index = t0
    for n in range(n_row):
        index += 1
        rates.append(table[index][-1])

    tt = TieredTime(tiers=tiers, rates=rates)

    return tt


def read_iym(
    table: dict,
    t0: float,
    t: float
) -> Rate:
    """
    Reads a value from a table of interest rates using the investment year method. A table might look something
    like this:

    iym_table = {
    2000: [.06, .065, .0575, .06, .065],
    2001: [.07, .0625, .06, .07, .0675],
    2002: [.06, .06, .0725, .07, .0725],
    2003: [.0775, .08, .08, .0775, .0715]
    }

    :param table: A table of interest rates as a dictionary, with years as the keys.
    :type table: dict
    :param t0: The initial investment time.
    :type t0: float
    :param t: The desired lookup time for which the rate applies.
    :type t: float
    :return: An interest rate applicable to the desired lookup time.
    :rtype: Rate
    """
    duration = t
    n_col = len(table[t0])
    row_d = duration - n_col

    if duration <= n_col:
        rate = table[t0][duration]
    else:
        row = row_d + t0
        rate = table[row][-1]

    rate = Rate(rate)

    return rate


def invsec(amt1: Amount, amt2: Amount, x0=range(100), precision=5) -> list:
    """
    Finds the point(s) at which two accumulation functions intersect.

    :param amt1:
    :type amt1:
    :param amt2:
    :type amt2:
    :param x0:
    :type x0:
    :param precision:
    :type precision:
    :return:
    :rtype:
    """
    def f(t):
        return amt1.val(t) - amt2.val(t)

    sol = newton(f, x0=x0)

    sol = [round(x, precision) for x in sol]

    res = list(set(sol))

    return res


def rate_from_earned(iex: Tuple[float, float], iey: Tuple[float, float]) -> Rate:
    """
    Given the amount of interest earned in two time periods, calculates the annualized effective interest rate.

    :param iex: Interest earned in period x, provided as (interest earned, period x).
    :type iex: Tuple[float, float]
    :param iey: Interest earned in period y, provided as (interest earned, period y).
    :type iey: Tuple[float, float]
    :return: An annualized effective interest rate.
    :rtype: Rate
    """

    x_amt = iex[0]
    x_t = iex[1]
    y_amt = iey[0]
    y_t = iey[1]

    print((1 / ((y_t - 1) - (x_t - 1)) - 1))

    gr = Rate((y_amt / x_amt) ** (1 / ((y_t - 1) - (x_t - 1))) - 1)

    return gr


def rate_from_intdisc(
    iex: Tuple[float, float],
    dex: Tuple[float, float],
    x0=np.linspace(.001, 1, 100),
    precision=5
) -> list:
    """
    Given interest earned over a time period on an unknown investment amount, and discount earned over a time period, \
    on that same amount,, solves for an annualized compound interest rate.

    :param iex: The interest earned over a time interval.
    :type iex: Tuple[float, float]
    :param dex: The discount earned over a time interval.
    :type dex: Tuple[float, float]
    :param x0: A starting guess or list of guesses for Newton's method, defaults to np.linspace(.001, 1, 100).
    :type x0:
    :param precision: rounding precision used to remove duplicates from Newton's method, defaults to 5.
    :type precision: int
    :return: a list of interest rates, if found.
    :rtype: list
    """

    i_amt = iex[0]
    d_amt = dex[0]
    i_t = iex[1]
    d_t = dex[1]

    def f(i):
        return ((1 + i) ** (i_t + d_t) - (1 + i) ** d_t) / ((1 + i) ** d_t - 1) - (i_amt / d_amt)

    sol = newton(f, x0=x0)

    if isinstance(sol, Iterable):
        sol = [round(x, precision) for x in sol]
        res = list(set(sol))

    else:

        res = [sol]

    return res


def amt_from_intdisc(
    iex: Tuple[float, float],
    dex: Tuple[float, float],
    x0: Union[float, ndarray] = np.linspace(.001, 1, 100),
    precision: int = 5
) -> Amount:

    """
    Given interest earned over a time period on an unknown investment amount, and discount earned over a time period, \
    on that same amount, generates an Amount object.

    For example, if you can earn 500 in interest in two years, and the discount in one year is 200, you can supply
    iex=[400, 2], dex=[200,1]

    :param iex: The interest earned over a time interval.
    :type iex: Tuple[float, float]
    :param dex: The discount earned over a time interval.
    :type dex: Tuple[float, float]
    :param x0: A starting guess or list of guesses for Newton's method, defaults to np.linspace(.001, 1, 100).
    :type x0:
    :param precision: rounding precision used to remove duplicates from Newton's method, defaults to 5.
    :type precision: int
    :return: An amount function.
    :rtype: Amount
    """
    rates = rate_from_intdisc(
        iex=iex,
        dex=dex,
        x0=x0,
        precision=precision
    )

    # use the min positive one:

    gr = min([x for x in rates if x > 0])

    k = iex[0] / ((1 + gr) ** iex[1] - 1)

    amt = Amount(gr=gr, k=k)

    return amt


def k_from_intdisc(
    iex: Tuple[float, float],
    dex: Tuple[float, float],
    x0: Union[float, ndarray] = np.linspace(.001, 1, 100),
    precision: int = 5
) -> float:

    """
    Given interest earned over a time period on an unknown investment amount, and discount earned over a time period, \
    on that same amount, solves for the amount.

    :param iex: The interest earned over a time interval.
    :type iex: Tuple[float, float]
    :param dex: The discount earned over a time interval.
    :type dex: Tuple[float, float]
    :param x0: A starting guess or list of guesses for Newton's method, defaults to np.linspace(.001, 1, 100).
    :type x0:
    :param precision: rounding precision used to remove duplicates from Newton's method, defaults to 5.
    :type precision: int
    :return: The investment amount.
    :rtype: float
    """

    k = amt_from_intdisc(
        iex=iex,
        dex=dex,
        x0=x0,
        precision=precision
    ).k

    return k

