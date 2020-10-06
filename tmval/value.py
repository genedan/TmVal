import functools
import itertools
import numpy as np
import warnings

from numpy import ndarray
from scipy.interpolate import approximate_taylor_polynomial
from scipy.misc import derivative
from scipy.optimize import newton

from itertools import groupby

from typing import (
    Callable,
    Iterable,
    Iterator,
    List,
    Union
)

from tmval.growth import (
    Accumulation,
    Amount,
    compound_solver,
    standardize_acc,
    TieredBal,
    TieredTime
)

from tmval.rate import (
    Rate,
    standardize_rate
)


class Payments:
    """
    A collection of payments, and corresponding growth object. If no growth object (an interest rate, Rate object, \
    Accumulation object) is provided, the payments are assumed to be undiscounted. The payments class serves as the \
    backbone for major types of financial instruments, such as annuities and bonds. It provides methods for \
    calculating net present value, internal rate of return (dollar weighted yield), equated time, equated value, \
     and time-weighted yield.

    :param amounts: a list of payment amounts.
    :type amounts: list, Iterable, Callable
    :param times: a list of payment times.
    :type times: list, Iterable, Callable
    :param gr: a growth rate object, can be supplied as a float, a Rate object, or an Accumulation object.
    :type gr: float, Rate, or Accumulation

    """
    def __init__(
        self,
        amounts: Union[
            list,
            Iterable,
            Callable
        ],
        times: Union[
            list,
            Iterable,
            Callable
        ],
        gr: Union[
            float,
            Rate,
            Accumulation,
            TieredBal,
            TieredTime
        ] = None
    ):
        if isinstance(amounts, (list, Iterable)) \
                and isinstance(times, (list, Iterable)) \
                and (len(amounts) != len(times)):

            raise Exception("Amounts and times must be of the same length.")

        self.amounts = amounts
        self.times = times
        self.gr = None
        if gr is not None:
            self.set_accumulation(gr=gr)

    def __add__(self, other):
        self.append(amounts=other.amounts, times=other.times)

    def set_accumulation(self, gr: Union[float, Rate, Accumulation, TieredBal, TieredTime]):

        # if float, assume compound annual effective
        if isinstance(gr, (float, Rate, TieredTime)):
            acc = standardize_acc(gr=gr)
        elif isinstance(gr, Accumulation):
            acc = standardize_acc(gr=gr) if gr.is_compound else gr
        elif isinstance(gr, TieredBal):
            acc = gr
        else:
            raise Exception("Invalid growth rate object provided.")

        self.gr = acc

    def append(
            self,
            amounts: list,
            times: list
    ):

        if len(amounts) != len(times):
            raise Exception("Amounts and times must be of the same length.")

        self.amounts += amounts
        self.times += times

    def paymentize(self, other, gr=None):
        if gr is None:
            gr = self.gr

        if isinstance(other, Payments):
            if (
                isinstance(self.times, list) and
                isinstance(self.amounts, list) and
                isinstance(other.times, list) and
                isinstance(other.amounts, list)
            ):

                times = self.times + other.times
                amounts = self.amounts + other.amounts
            else:
                raise ValueError("Invalid object passed to argument 'other'.")

        elif isinstance(other, list):
            times = []
            amounts = []
            for x in other:
                times += x.times
                amounts += x.amounts
        else:
            raise ValueError("Invalid object passed to argument 'other'.")

        grouped = Payments(
            times=times,
            amounts=amounts
        ).group_payments()

        times = [k for k in grouped.keys()]
        amounts = [grouped[k] for k in grouped.keys()]

        pmts = Payments(
            times=times,
            amounts=amounts,
            gr=gr
        )

        return pmts

    def group_payments(self) -> dict:
        times = self.times.copy()
        amounts = self.amounts.copy()

        payments = [[x, y] for x, y in zip(times, amounts)]
        payments.sort()
        payments_grouped = []
        for i, g in groupby(payments, key=lambda x: x[0]):
            payments_grouped.append([i, sum(v[1] for v in g)])

        payments_dict = {x[0]: x[1] for x in payments_grouped}

        return payments_dict

    def npv(self, gr=None):
        if gr is None:
            if self.gr is None:
                raise Exception("Growth rate object not set.")
            else:
                acc = self.gr
        else:
            acc = standardize_acc(gr=gr)

        pv = sum([acc.discount_func(t=t, fv=fv) for t, fv in zip(self.times, self.amounts)])

        return pv

    def irr(
        self,
        x0: float = 1.05
    ) -> list:
        """
        Calculates the internal rate of return, also known as the yield rate or dollar-weighted return. If the \
        payment amounts and times result in a polynomial equation of value, the yield is solved by calculating the \
        roots of the polynomial via the NumPy roots function. If the equation of value is not a polynomial, than \
        Newton's method from the SciPy package is used.

        :param x0: A starting guess when using Newton's method, defaults to 1.05.
        :type x0: float
        :return: A list of real roots, if found.
        :rtype: list
        """
        payments_dict = self.group_payments()

        degree = max(payments_dict, key=int)
        is_poly = all(isinstance(x, int) for x in payments_dict)

        # if times are integral, equation of value is polynomial, might be solved with NumPy roots
        if is_poly:
            coefficients = [(payments_dict[i] if i in payments_dict else 0) for i in range(degree + 1)]
            roots = np.roots(coefficients)
            reals = roots[np.isreal(roots)]

            if len(reals) == 0:
                warnings.warn("Unable to find real roots.")

            i_s = [np.real(x) - 1 for x in reals]

        # if times are fractional, use Newton's method:
        else:
            def f(x):
                return sum([payments_dict[k] * (x ** - k) for k in payments_dict.keys()])

            roots = newton(func=f, x0=x0)

            if isinstance(roots, ndarray):
                pass
            else:
                roots = np.array(roots)
            reals = roots[np.isreal(roots)]

            i_s = [(np.real(x)) - 1 for x in reals]

        return i_s

    def equated_time(
        self,
        c: float
    ) -> float:

        """
        Method of equated time. Finds :math:`T` so that a single payment of :math:`C = \sum_{k=1}^n C_{t_k}` \
        at time :math:`T` has the same value at :math:`t = 0` as the sequence of :math:`n` contributions.

        While this method is formally defined to have C equal the sum of the contributions, it actually works when
        C is not equal to the sum of the contributions.

        :param c: The single payment C.
        :type c: float
        :return: The time T.
        :rtype: float
        """

        acc = self.gr

        num = np.log(self.npv() / c)

        denom = np.log(1 / (1 + acc.interest_rate.rate))

        t = num / denom

        return t

    def pt_bal(self, t: float) -> float:

        payments_dict = self.group_payments()
        times = list(payments_dict.keys())
        times = [x for x in times if x < t]
        times.sort()
        times.append(t)
        bal = payments_dict[times[0]]
        for index, time in enumerate(times):
            if time == t:
                pass

            else:
                next_t = times[index + 1]
                interval = next_t - time

                if isinstance(self.gr, TieredBal):
                    amt = Amount(gr=self.gr, k=bal)
                    bal = amt.val(interval)
                else:
                    bal = bal * self.gr.val(interval)

                if next_t in payments_dict:
                    bal = bal + payments_dict[next_t]

        return bal

        # return bal

    def eq_val(self, t: float, gr=None) -> float:
        if gr is None:
            if self.gr is None:
                raise Exception("Growth rate object not set.")
            else:
                acc = self.gr
        else:
            acc = standardize_acc(gr=gr)

        b = sum([c * acc.val(t) / acc.val(tk) for c, tk in zip(self.amounts, self.times)])

        return b

    def dw_approx(
        self,
        a: float = None,
        b: float = None,
        w_t: float = None,
        k_approx: bool = False,
        k: float = .5,
        annual: bool = False
    ) -> Rate:

        """
        Calculates the approximate dollar-weighted yield rate by standardizing the investment time to 1:

        .. math::

           j \\approx \\frac{I}{A + \\sum_{t \\in (0, 1)} C_t(1-t)}

        Where A is the beginning balance, I is interest earned, and the Cs are the contributions. When k_approx is
        set to true, k is assumed to be a fixed constant within the investment window:

        .. math::

           j \\approx \\frac{I}{A + C(1-k)}

        The default value for k is 1/2, simplifying the above expression to:

           j \\approx \\frac{2I}{A + B - I}

        Where B is the withdrawal balance. When arguments a, b, and w_t (corresponding to A, B, and the \
        the withdrawal time) are not provided, a is assumed to be the first payment in the parent object, and b is \
        calculated to be the last.

        :param a: The initial balance.
        :type a: float
        :param b: The withdrawal balance.
        :type b: float
        :param w_t: The withdrawal time.
        :type w_t: float
        :param k_approx: Whether you want to use the k-approximation formula.
        :type k_approx: bool
        :param k: The value for k in the k-approximation formula, defaults to .5.
        :type k: float
        :param annual: Whether you want the results annualized.
        :type annual: bool
        :return: The approximate dollar-weighted yield rate.
        :rtype: Rate
        """

        if [a, b, w_t].count(None) not in [0, 3]:
            raise Exception("a, b, w_t must all be provided or left none.")

        times = self.times.copy()
        amounts = self.amounts.copy()

        if a is None:
            w_t = times.pop()
            b = - amounts.pop()
            a = amounts.pop(0)
            times.pop(0)

        c = sum(amounts)
        i = b - a - c

        if k_approx:

            j = i / (k * a + (1 - k) * b - (1 - k) * i)

        else:
            # normalize times
            max_t = w_t
            t_s = [t / max_t for t in times]
            j = i / (a + sum([ct * (1-t) for ct, t in zip(amounts, t_s)]))

        j = Rate(
            rate=j,
            pattern="Effective Interest",
            interval=w_t
        )

        if annual:
            j = j.convert_rate(
                pattern="Effective Interest",
                interval=1
            )

        return j

    def time_weighted_yield(
        self,
        balance_times: list,
        balance_amounts: list,
        annual: bool = False
    ):

        jtw = time_weighted_yield(
            payments=self,
            balance_times=balance_times,
            balance_amounts=balance_amounts,
            annual=annual
        )

        return jtw

    def taylor(self, gr, x, degree):

        def f(grs):
            res = []
            for i in grs:
                res += [self.npv(gr=i)]
            return res

        #approx = approximate_taylor_polynomial(f, x=x, degree=degree, scale=gr)
        return approximate_taylor_polynomial(f, x=x, degree=degree, scale=gr)

    def tangent_line_approx(self, i0, i):

        return self.npv(gr=i0) + derivative(self.npv, x0=i0, dx=1e-6) * (i - i0)

    def taylor2(self, i0, i):

        return self.tangent_line_approx(i0=i0, i=i) + \
               derivative(self.npv, x0=i0, dx=1e-5, n=2) / 2 * (i - i0) ** 2

    def relchg(self, i, i0=None, approx=False, excl_inv=True, degree=1):
        if i0 is None:
            if self.gr is not None:
                i0 = self.gr
            else:
                raise ValueError("Growth rate object not set")
        else:
            i0 = standardize_acc(gr=i0)

        if approx:
            if i0.is_compound:
                d1 = - self.modified_duration(i=i0.interest_rate, excl_inv=excl_inv) * (i - i0.interest_rate)
                if degree == 1:
                    res = d1
                elif degree == 2:
                    d2 = self.modified_convexity(i=i0.interest_rate, excl_inv=excl_inv) * ((i -i0.interest_rate) ** 2) / 2
                    res = d1 + d2
                else:
                    raise ValueError("Relative change approximation is only supported for 1st and 2nd degrees.")
            else:
                raise Exception("Relative change approximation is unsupported for non-compound interest.")
        else:
            if excl_inv:
                times = self.times.copy()
                amounts = self.amounts.copy()
                times.pop(0)
                amounts.pop(0)
                pmts = Payments(times=times, amounts=amounts, gr=self.gr)
                res = (pmts.npv(gr=i) - pmts.npv(gr=i0)) / pmts.npv(gr=i0)
            else:
                res = (self.npv(gr=i) - self.npv(gr=i0)) / self.npv(gr=i0)

        return res

    def modified_duration(self, i, m=1, excl_inv=True):

        if excl_inv:
            if m != 1:
                im = Rate(i).convert_rate(
                    pattern="Nominal Interest",
                    freq=m
                )
                return self.macaulay_duration() / (1 + im.rate / m)
            else:
                times = self.times.copy()
                amounts = self.amounts.copy()
                times.pop(0)
                amounts.pop(0)
                pmts = Payments(times=times, amounts=amounts, gr=self.gr)
                return - derivative(pmts.npv, x0=i, dx=1e-6) / pmts.npv(gr=i)
        else:

            return - derivative(self.npv, x0=i, dx=1e-6) / self.npv(gr=i)

    def macaulay_duration(self, gr=None, excl_inv=True):
        if gr is None:
            if self.gr is None:
                raise Exception("Growth rate object not set.")
            else:
                acc = self.gr
        else:
            acc = standardize_acc(gr=gr)

        if excl_inv:
            times = self.times.copy()
            amounts = self.amounts.copy()
            times.pop(0)
            amounts.pop(0)
            pmts = Payments(times=times, amounts=amounts, gr=acc)
            pv = pmts.npv()
        else:
            pv = self.npv(gr=gr)
            times = self.times
            amounts = self.amounts

        md = sum([acc.discount_func(t=t, fv=fv) * t / pv for t, fv in zip(times, amounts)])

        return md

    def modified_convexity(self, i, m=1, excl_inv=True, dx=1e-5):
        if excl_inv:
            times = self.times.copy()
            amounts = self.amounts.copy()
            times.pop(0)
            amounts.pop(0)
            pmts = Payments(times=times, amounts=amounts, gr=self.gr)
            p_double_prime = derivative(pmts.npv, x0=i, dx=dx, n=2)

            return p_double_prime / pmts.npv(gr=i)

    def macaulay_convexity(self, gr=None, excl_inv=True):

        if gr is None:
            if self.gr is None:
                raise Exception("Growth rate object not set.")
            else:
                acc = self.gr
        else:
            acc = standardize_acc(gr=gr)

        if excl_inv:
            times = self.times.copy()
            amounts = self.amounts.copy()
            times.pop(0)
            amounts.pop(0)
            pmts = Payments(times=times, amounts=amounts, gr=acc)
            pv = pmts.npv()
        else:
            pv = self.npv(gr=gr)
            times = self.times
            amounts = self.amounts

        mc = sum([acc.discount_func(t=t, fv=fv) * t ** 2 / pv for t, fv in zip(times, amounts)])

        return mc

    def check_redington(self, precision=4):
        if round(self.npv(), precision) == 0:
            c1 = True
        else:
            c1 = False

        if round(derivative(self.npv, x0=self.gr.interest_rate, dx=1e-6), precision) == 0.0:
            c2 = True
        else:
            c2 = False

        if round(derivative(self.npv, x0=self.gr.interest_rate, dx=1e-6, n=2), precision) >= 0.0:
            c3 = True
        else:
            c3 = False

        return c1 and c2 and c3

    def effective_duration(self, i0, h, call=None, excl_inv=True):

        if excl_inv:
            times = self.times.copy()
            amounts = self.amounts.copy()
            times.pop(0)
            amounts.pop(0)
            pmts = Payments(times=times, amounts=amounts)
        else:
            pmts = self

        if call is not None:
            p1 = call
        else:
            p1 = pmts.npv(gr=i0 - h)

        p2 = pmts.npv(gr=i0 + h)

        p0 = pmts.npv(gr=i0)

        mh = (p2 - p1) / (2 * h)

        eh = - mh / p0

        return eh


def npv(
        payments: list,
        gr: Union[Accumulation, float, Rate]
) -> float:
    """
    Calculates the net present value for a stream of payments.

    :param payments: a list of :class:`Payment` objects.
    :type payments: list
    :param gr: a growth rate object, can be interest rate as a float, Accumulation object, or Rate
    :type gr: Accumulation, float, or Rate
    :return: the net present value
    :rtype: float
    """
    if isinstance(gr, Accumulation):
        acc = Accumulation
    elif isinstance(gr, float):
        acc = Accumulation(gr)
    elif isinstance(gr, Rate):
        i = gr.convert_rate(
            pattern="Effective Interest",
            freq=1
        )
        acc = Accumulation(i)
    else:
        raise Exception("Invalid type passed to gr.")

    discount_func = acc.discount_func

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
        gr: Union[Accumulation, float, Rate] = None
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
    :param gr: A growth rate object.
    :type gr: Callable
    :return: Returns either the npv, a missing payment amount, a missing time of payment, or missing discount factor.
    :rtype: float
    """

    args = [npval, payments, gr]
    if args.count(None) > 1:
        raise Exception("Only one argument can be missing.")

    if gr:
        gr = standardize_rate(gr)
        acc = Accumulation(gr=gr)

    # exclude missing payment

    payments_excl_missing = [x for x in payments if x.time is not None]
    missing_pmt = [x for x in payments if x.time is None].pop()
    payments_excl_missing_npv = npv(payments=payments_excl_missing, gr=gr)

    missing_pmt_pv = npval - payments_excl_missing_npv
    res = np.log(missing_pmt.amount / missing_pmt_pv) / np.log(acc.discount_func(1) ** -1)

    return res


def payment_solver(payments: Payments, t: float) -> float:
    # gr = standardize_acc(gr)

    # all_other_pv = - npv(payments=payments, gr=gr)

    all_other_pv = -payments.npv()

    p = compound_solver(pv=all_other_pv, t=t, gr=payments.gr.interest_rate)

    return p


def interest_solver(payments: Payments, fv: float, tfv: float) -> float:

    coefficients = [payment for payment in payments.amounts]

    # latest payment time in payments
    max_t = max([payment for payment in payments.times])

    # if gap between fv time and max_t, fill in with zeroes
    zero_to_add = tfv - max_t
    zeros = [0] * zero_to_add
    coefficients = coefficients + zeros

    coefficients[-1] = coefficients[-1] + fv

    roots = np.roots(coefficients)
    reals = roots[np.isreal(roots)]

    if len(reals) == 0:
        raise Exception("Unable to find real roots.")

    i = max(reals) - 1
    i = np.real(i)

    return i


def time_solver(amounts: list, gr: Rate) -> list:

    coefficients = amounts
    coefficients.reverse()

    n_periods = len(coefficients) - 1

    roots = np.roots(coefficients)
    reals = roots[np.isreal(roots)]

    if len(reals) == 0:
        raise Exception("Unable to find real roots.")

    x = max(reals)
    v = 1 / (1 + gr.rate)

    t = np.log(x) / np.log(v)

    return [t * (x + 1) for x in range(n_periods)]


def equated_time(payments: list, gr: Rate, c: float) -> float:

    num = np.log(npv(payments=payments, gr=gr) / c)

    denom = np.log(1/(1+gr.rate))

    t = num / denom

    return t


def dollar_weighted_yield(
        payments: Payments = None,
        times: list = None,
        amounts: list = None,
        a: float = None,
        b: float = None,
        i: float = None,
        w_t: float = None,
        k_approx: bool = False,
        annual: bool = False
) -> Rate:
    if [a, b, w_t].count(None) not in [0, 3] and k_approx is False:
        raise Exception("a, b, w_t must all be provided or left none.")

    if payments:
        times = payments.times.copy()
        amounts = payments.amounts.copy()
    elif times and amounts:
        times = times
        amounts = amounts
    elif k_approx:
        pass
    else:
        raise Exception("Must supply a payments object or list of payment times and amounts if not "
                        "using k-approximation.")

    if a is None:
        w_t = times.pop()
        b = amounts.pop()
        a = amounts.pop(0)
        times.pop(0)

    if amounts is not None:
        c = sum(amounts)

    if i is None:
        i = b - a - c

    if k_approx:

        j = (2 * i) / (a + b - i)

    else:
        # normalize times
        max_t = w_t
        t_s = [t / max_t for t in times]
        j = i / (a + sum([ct * (1 - t) for ct, t in zip(amounts, t_s)]))

    j = Rate(
        rate=j,
        pattern="Effective Interest",
        interval=w_t
    )

    if annual:
        j = j.convert_rate(
            pattern="Effective Interest",
            interval=1
        )

    return j


def dollar_weighted_time(a, b, i, j):

    c = b - a - i

    k = 1 - (i / j - a) / c

    return k


def time_weighted_yield(
    balance_times: list,
    balance_amounts: list,
    payments: Payments = None,
    payment_times: list = None,
    payment_amounts: list = None,
    annual: bool = False
) -> Rate:
    """
    Given a list of balances and payments, returns the time-weighted yield. If annual is set to True, returns the
    rate as an annual rate. Otherwise, the rate is effective over the investment term.

    You may supply a Payments object, or specify the components separately.

    :param balance_times: A list of balance times.
    :type balance_times: list
    :param balance_amounts: A list of balance amounts, corresponding to the balance times.
    :type balance_amounts: list
    :param payments: A Payments object.
    :type payments: Payments
    :param payment_times: A list of payment times.
    :type payment_times: list
    :param payment_amounts: A list of payment amounts, corresponding to the payment times.
    :type payment_amounts: list
    :param annual: Whether you want the time-weighted yield to be annualized.
    :type annual: bool, defaults to False
    :return: The time-weighted yield.
    :rtype: Rate
    """
    # group payments by time

    if payments:
        payment_times = payments.times
        payment_amounts = payments.amounts
    else:
        payment_times = payment_times
        payment_amounts = payment_amounts

    payments = [[x, y] for x, y in zip(payment_times, payment_amounts)]
    payments.sort()
    payments_grouped = []
    for i, g in groupby(payments, key=lambda x: x[0]):
        payments_grouped.append([i, sum(v[1] for v in g)])

    payments_dict = {x[0]: x[1] for x in payments_grouped}

    balance_zip = zip(balance_times, balance_amounts)
    balance_dict = {x[0]: x[1] for x in balance_zip}

    j_factors = []
    for t_prior, t in pairwise(balance_dict.keys()):

        if t_prior == 0:
            j_factor = balance_dict[t] / balance_dict[t_prior]
        else:
            j_factor = balance_dict[t] / (balance_dict[t_prior] + payments_dict[t_prior])

        j_factors.append(j_factor)

    jtw = functools.reduce(lambda x, y: x*y, j_factors) - 1

    jtw = Rate(
        rate=jtw,
        pattern="Effective Interest",
        interval=max(balance_times)
    )

    if annual:
        jtw = jtw.convert_rate(
            pattern="Effective Interest",
            interval=1
        )

    return jtw


def pairwise(iterable: Iterable) -> Iterator:
    """
    Helper function to enable pairwise iteration.

    :param iterable: An iterable object.
    :type iterable: iterable
    :return: An iterator.
    :rtype: Iterator
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def extract_flows(payments: Union[Payments, List[Payments]]) -> Payments:

    if isinstance(payments, Payments):
        payments = [payments]
    amounts = []
    times = []
    for pmts in payments:
        amounts += pmts.amounts
        times += pmts.times

    res = Payments(
        amounts=amounts,
        times=times
    )

    return res


