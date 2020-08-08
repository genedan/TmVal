import numpy as np

from tmval.growth import CompoundAcc, npv, compound_solver
from tmval.rates import Rate


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
