import numpy as np

from tmval.growth import CompoundAcc, npv, compound_solver
from tmval.rates import Rate


def payment_solver(payments: list, t: float, ca: CompoundAcc) -> float:

    all_other_pv = - npv(payments=payments, discount_func=ca.discount_func)

    p = compound_solver(pv=all_other_pv, t=t, gr=ca.interest_rate)

    return p


def irr(payments: list) -> float:

    coefficients = [payment.amount for payment in payments]

    # latest payment time in payments


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
