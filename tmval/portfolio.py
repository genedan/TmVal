from typing import List

from tmval.bond import Bond
from tmval.growth import standardize_acc
from tmval.value import Payments


def macaulay_duration(portfolio: List[Payments]):

    price = sum([get_price_from_instrument(instrument=x) for x in portfolio])

    res = sum([x.macaulay_duration() * get_price_from_instrument(instrument=x) for x in portfolio]) / price

    return res


def macaulay_convexity(portfolio: List[Payments]):

    price = sum([get_price_from_instrument(instrument=x) for x in portfolio])

    res = sum([x.macaulay_convexity() * get_price_from_instrument(instrument=x) for x in portfolio]) / price

    return res


def get_price_from_instrument(instrument: Payments):

    if isinstance(instrument, Bond):
        return instrument.price
    else:
        return instrument.npv()


def reddingtonize(fv, t, gr, terms=None, portfolio=List[Payments]):
    pv = standardize_acc(gr=gr).discount_func(fv=fv, t=t)

    if terms is not None:
        a = (terms[1] - t) * pv / (terms[1] - terms[0])

        b = pv - a

        bd1 = Bond(
            price=a,
            term=terms[0],
            gr=gr
        )

        bd2 = Bond(
            price=b,
            term=terms[1],
            gr=gr
        )
    elif portfolio is not None:
        a = (portfolio[1].macaulay_duration() - t) * pv / (portfolio[1].macaulay_duration() - portfolio[0].macaulay_duration())

        a_fac = a / portfolio[0].price

        b = pv - a

        b_fac = b / portfolio[1].price

        bd1 = Bond(
            red=portfolio[0].red * a_fac,
            face=portfolio[0].face * a_fac if portfolio[0].face is not None else None,
            alpha=portfolio[0].alpha,
            cfreq=portfolio[0].cfreq,
            term=portfolio[0].term,
            gr=portfolio[0].gr

        )

        bd2 = Bond(
            red=portfolio[1].red * b_fac,
            face=portfolio[1].face * a_fac if portfolio[1].face is not None else None,
            alpha=portfolio[1].alpha,
            cfreq=portfolio[1].cfreq,
            term=portfolio[1].term,
            gr=portfolio[1].gr

        )

    else:
        raise Exception("Unable to calculate weights.")

    return [bd1, bd2]


def price_from_efd(p0, efd, chg):
    """
    Estimates the price from the effective duration
    :return:
    :rtype:
    """

    return p0 * (1 - chg * efd)
