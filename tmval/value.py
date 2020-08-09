import numpy as np
import warnings

from itertools import groupby

from typing import Callable, Union

from tmval.growth import Accumulation, CompoundAcc, compound_solver
from tmval.rates import Rate


class Payments:
    def __init__(
        self,
        amounts: list,
        times: list,
        gr: Union[float, Rate, Accumulation] = None
    ):
        if len(amounts) != len(times):
            raise Exception("Amounts and times must be of the same length.")

        self.amounts = amounts
        self.times = times
        self.acc = None
        if gr is not None:
            self.set_accumulation(gr=gr)

    def set_accumulation(self, gr: Union[float, Rate, Accumulation]):

        # if float, assume compound annual effective
        if isinstance(gr, float):
            acc = CompoundAcc(gr=gr)

        elif isinstance(gr, Rate):
            acc = CompoundAcc(gr=gr)

        elif isinstance(gr, (Accumulation, CompoundAcc)):
            acc = gr
        else:
            raise Exception("Invalid growth rate object provided.")

        self.acc = acc

    def npv(self):
        if self.acc is None:
            raise Exception("Growth rate object not set.")

        pv = sum([self.acc.discount_func(t=t, fv=fv) for t, fv in zip(self.times, self.amounts)])

        return pv

    def irr(self):
        times = self.times
        amounts = self.amounts
        payments = [[x, y] for x, y in zip(times, amounts)]
        payments.sort()
        payments_grouped = []
        for i, g in groupby(payments, key=lambda x: x[0]):
            payments_grouped.append([i, sum(v[1] for v in g)])

        payments_dict = {x[0]: x[1] for x in payments_grouped}

        degree = max(payments_dict, key=int)

        coefficients = [(payments_dict[i] if i in payments_dict else 0) for i in range(degree +1)]

        roots = np.roots(coefficients)

        reals = roots[np.isreal(roots)]

        if len(reals) == 0:
            warnings.warn("Unable to find real roots.")

        i_s = [np.real(x) - 1 for x in reals]

        return i_s

    def equated_time(self, c: float) -> float:

        acc = self.acc

        num = np.log(self.npv() / c)

        denom = np.log(1 / (1 + acc.interest_rate.rate))

        t = num / denom

        return t

    def eq_val(self, t: float) -> float:

        b = sum([c * self.acc.val(t) / self.acc.val(tk) for c, tk in zip(self.amounts, self.times)])

        return b

    def dollar_weighted_yield(
        self,
        a: float = None,
        b: float = None,
        w_t: float = None,
        k_approx: bool = False,
        annual: bool = False
    ) -> Rate:
        if [a, b, w_t].count(None) not in [0, 3]:
            raise Exception("a, b, w_t must all be provided or left none.")

        times = self.times.copy()
        amounts = self.amounts.copy()

        if a is None:
            w_t = times.pop()
            b = amounts.pop()
            a = amounts.pop(0)
            times.pop(0)

        c = sum(amounts)
        i = b - a - c

        if k_approx:

            j = (2 * i) / (a + b - i)

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


def payment_solver(payments: list, t: float, ca: CompoundAcc) -> float:

    all_other_pv = - npv(payments=payments, discount_func=ca.discount_func)

    p = compound_solver(pv=all_other_pv, t=t, gr=ca.interest_rate)

    return p


def interest_solver(payments: list, fv: float, tfv: float) -> float:

    coefficients = [payment.amount for payment in payments]

    # latest payment time in payments
    max_t = max([payment.time for payment in payments])

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


def has_all_discounts(payments: list) -> bool:

    res = all(payment.discount_factor is not None for payment in payments)

    return res


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

    acc = CompoundAcc(gr=gr)

    num = np.log(npv(payments=payments, discount_func=acc.discount_func) / c)

    denom = np.log(1/(1+acc.interest_rate.rate))

    t = num / denom

    return t
