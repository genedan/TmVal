"""
Contains interest rate conversion formulas. While these may be called manually by the user, I don't encourage it. \
These are intended to facilitate the convert_rate method in the Rate class, which should be more \
convenient for the user.
"""
import numpy as np


class RateTemplate:
    """
    Stores the results of conversions.
    """
    def __init__(
            self,
            rate: float = None,
            formal_pattern: str = None,
            freq: float = None,
            interval: float = None
    ):
        self.rate = rate
        self.formal_pattern = formal_pattern
        self.freq = freq
        self.interval = interval


def eff_int_from_eff_int(
        i: float,
        old_t: float,
        new_t: float
) -> RateTemplate:
    """

    :param i: the effective interest rate.
    :type i: float
    :param old_t: the old unit of time.
    :type old_t: float
    :param new_t: the new unit of time.
    :type new_t: float
    :return: a converted interest rate, based off the new unit of time.
    :rtype: RateTemplate
    """
    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = (1 + i) ** (1 / old_t) - 1

    if new_t is not None:
        i = (1 + i) ** new_t - 1

    res = RateTemplate(
        rate=i,
        formal_pattern='Effective Interest',
        interval=new_t
    )

    return res


def nom_int_from_eff_int(
        i: float,
        new_m: float,
        old_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given an effective interest rate and desired compounding \
    frequency, returns the nominal interest rate.

    :param i: the effective interest rate.
    :type i: float
    :param new_m: the desired compounding frequency.
    :type new_m: float,
    :param old_t: the interval of the effective interest rate. Assumed to be 1 if not provided.
    :type old_t: float, optional
    :return: the nominal interest rate.
    :rtype: RateTemplate
    """
    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=old_t, new_t=1).rate

    im = new_m * ((1 + i) ** (1 / new_m) - 1)

    res = RateTemplate(
        rate=im,
        formal_pattern="Nominal Interest",
        freq=new_m
    )

    return res


def eff_disc_from_eff_int(
        i: float,
        old_t: float = None,
        new_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given an effective interest rate and applicable unit \
    of time, along with a desired unit of time for the new rate, returns an effective discount rate at the new unit \
    of time. If old_t or new_t are not provided, they are each assumed to be 1, i.e., a 1-year period.

    :param i: the effective interest rate
    :type i: float
    :param old_t: the old unit of time, defaults to None.
    :type old_t: float, optional
    :param new_t: the new unit of time, defaults to None.
    :type new_t: float, optional
    :return: an effective discount rate at the new unit of time.
    :rtype: RateTemplate
    """

    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=old_t, new_t=1)

    d = discount_from_interest(i=i.rate)

    # assume new interval is 1 if not specified
    if new_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=1, new_t=new_t)

    res = RateTemplate(
        rate=d.rate,
        formal_pattern="Effective Discount",
        interval=new_t
    )

    return res


def nom_disc_from_eff_int(
        i: float,
        new_m: float,
        old_t: float = None

) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given an effective interest rate and unit of time, along \
    with a desired compounding frequency, returns a nominal discount rate at the desired compounding frequency. If \
    no unit of time (applicable to the effective interest rate) is provided, it is assumed to be 1, i.e., a 1-year \
    period.

    :param i: the effective interest rate.
    :type i: float
    :param new_m: the desired compounding frequency.
    :type new_m: float
    :param old_t: the unit of time applicable to the effective interest rate, defaults to None.
    :type old_t: float, optional
    :return: a nominal discount rate, compounded new_m times per year.
    :rtype: RateTemplate
    """
    # convert i to yearly effective if it is not already
    if old_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=old_t, new_t=1).rate

    d = discount_from_interest(i)

    res = nom_disc_from_eff_disc(d=d, new_m=new_m)

    return res


def eff_int_from_eff_disc(
        d: float,
        old_t: float = None,
        new_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given an effective discount rate and unit of time, along \
    with a desired new unit of time, returns an effective interest rate at the new unit of time. If \
    no unit of time (either old or new) is provided, it is assumed to be 1, i.e., a 1-year \
    period.

    :param d: the effective discount rate.
    :type d: float
    :param old_t: the old unit of time, defaults to None.
    :type old_t: float, optional
    :param new_t: the new unit of time, defaults to None.
    :type new_t: float, optional
    :return: an effective interest rate, at the new unit of time.
    :rtype: RateTemplate
    """
    # convert d to yearly effective if it is not already
    if old_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=old_t, new_t=1).rate

    i = interest_from_discount(d)

    # convert to new interval if given
    if new_t is not None:
        i = eff_int_from_eff_int(i=i, old_t=1, new_t=new_t).rate

    res = RateTemplate(
        rate=i,
        formal_pattern='Effective Interest',
        interval=new_t
    )

    return res


def nom_int_from_eff_disc(
        d: float,
        new_m: float,
        old_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given an effective discount rate and unit of time, along \
    with a desired compounding frequency, returns a nominal interest rate at the desired compounding frequency. If \
    no unit of time is provided (applicable to the effective discount rate), it is assumed to be 1, i.e., a 1-year \
    period.

    :param d: the effective discount rate.
    :type d: float
    :param new_m: the desired compounding frequency.
    :type new_m: float
    :param old_t: the old unit of time, defaults to None.
    :type old_t: float, optional
    :return: a nominal interest rate, compounded new_m times per year
    :rtype: RateTemplate
    """

    # convert d to yearly effective if it is not already
    if old_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=old_t, new_t=1)

    i = interest_from_discount(d=d)

    res = nom_int_from_eff_int(i=i, new_m=new_m)

    return res


def eff_disc_from_eff_disc(
        d: float,
        old_t: float,
        new_t: float
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given an effective discount rate and unit of time, along \
    with a desired new unit of time, returns an effective discount rate at the desired new unit of time.
    period.

    :param d: the effective discount rate.
    :type d: float
    :param old_t: the old unit of time.
    :type old_t: float
    :param new_t: the new unit of time.
    :type new_t: float
    :return: an effective discount rate at the new unit of time.
    :rtype: RateTemplate
    """
    # first convert to single-period rate
    d1 = 1 - (1 - d) ** (1 / old_t)
    # then, convert to new interval
    new_d = 1 - ((1 - d1) ** new_t)

    res = RateTemplate(
        rate=new_d,
        formal_pattern='Effective Discount',
        interval=new_t
    )

    return res


def nom_disc_from_eff_disc(
        d: float,
        new_m: float,
        old_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given an effective discount rate and unit of time, along \
    with a desired compounding frequency, returns a nominal discount rate at the desired compounding frequency. If \
    no unit of time is provided (applicable to the effective discount rate), it is assumed to be 1, i.e., a 1-year \
    period.

    :param d: the effective discount rate.
    :type d: float
    :param new_m: the desired compounding frequency.
    :type new_m: float
    :param old_t: the old unit of time, defaults to None.
    :type old_t: float, optional
    :return: a nominal discount rate, compounded new_m times per year.
    :rtype: RateTemplate
    """
    # convert d to yearly effective if it is not already

    if old_t is not None:
        d = eff_disc_from_eff_disc(d=d, old_t=old_t, new_t=1).rate

    dm = new_m * (1 - (1 - d) ** (1 / new_m))

    res = RateTemplate(
        rate=dm,
        formal_pattern='Nominal Discount',
        freq=new_m
    )

    return res


def eff_int_from_nom_int(
        im: float,
        m: float,
        new_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal interest rate, along \
    with a desired unit of time, returns an effective interest rate at the desired unit of time. If \
    no unit of time is provided, it is assumed to be 1, i.e., a 1-year \
    period.

    :param im: the nominal interest rate.
    :type im: float
    :param m: the compounding frequency.
    :type m: float
    :param new_t: the desired unit of time, defaults to None.
    :type new_t: float, optional
    :return: an effective interest rate.
    :rtype: RateTemplate
    """
    # get yearly rate first
    i = effective_from_nominal_int(im=im, m=m)

    if new_t is not None:
        res = eff_int_from_eff_int(i=i, old_t=1, new_t=new_t)
    else:
        res = RateTemplate(
            rate=i,
            formal_pattern='Effective Interest',
            interval=1
        )

    return res


def nom_int_from_nom_int(
        im: float,
        m: float,
        new_m: float
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal interest rate, along \
    with a desired compounding frequency, returns a nominal interest rate at the desired compounding frequency.

    :param im: the nominal interest rate.
    :type im: float
    :param m: the compounding frequency
    :type m: float
    :param new_m: the desired compounding frequency.
    :type new_m: float
    :return: a nominal interest rate, compounded new_m times per year.
    :rtype: RateTemplate
    """

    i = effective_from_nominal_int(im=im, m=m)

    res = nom_int_from_eff_int(i=i, new_m=new_m)

    return res


def eff_disc_from_nom_int(
    im: float,
    m: float,
    new_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal interest rate, along \
    with a desired unit of time, returns an effective discount rate at the desired unit of time. If \
    no unit of time is provided, it is assumed to be 1, i.e., a 1-year \
    period.

    :param im: the nominal interest rate.
    :type im: float
    :param m: the compounding frequency
    :type m: float
    :param new_t: the desired unit of time.
    :type new_t: float, optional
    :return: an effective discount rate.
    :rtype: RateTemplate
    """

    i = effective_from_nominal_int(im=im, m=m)
    d = discount_from_interest(i=i)

    if new_t is not None:
        res = eff_disc_from_eff_disc(d=d, old_t=1, new_t=new_t)
    else:
        res = RateTemplate(
            rate=d,
            formal_pattern='Effective Discount',
            interval=1
        )

    return res


def nom_disc_from_nom_int(
        im: float,
        m: float,
        new_m: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal interest rate, along \
    with a desired compounding frequency, returns an nominal discount rate at the desired compounding frequency.


    :param im: the nominal interest rate.
    :type im: float
    :param m: the compounding frequency
    :type m: float
    :param new_m: the desired compounding frequency.
    :type new_m: float
    :return: a nominal discount rate, compounded new_m times per year
    :rtype: RateTemplate
    """

    if new_m is None:
        new_m = m

    n = m
    i_n = im

    i = (1 + i_n / n) ** n - 1

    p = new_m

    dp = (1 - (1+i) ** (-1 / p)) * p

    res = RateTemplate(
        rate=dp,
        formal_pattern='Nominal Discount',
        freq=new_m
    )

    return res


def eff_int_from_nom_disc(
        dm: float,
        m: float,
        new_t: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal discount rate, along \
    with a desired unit of time, returns an effective interest rate at the desired unit of time. If \
    no unit of time is provided, it is assumed to be 1, i.e., a 1-year \
    period.

    :param dm: the nominal discount rate.
    :type dm: float
    :param m: the compounding frequency.
    :type m: float
    :param new_t: the desired unit of time, defaults to None.
    :type new_t: float
    :return: an effective interest rate.
    :rtype: RateTemplate
    """

    d = effective_from_nominal_disc(dm=dm, m=m)

    i = interest_from_discount(d)

    if new_t is not None:
        res = eff_int_from_eff_int(i=i, old_t=1, new_t=new_t)
    else:
        res = RateTemplate(
            rate=i,
            formal_pattern='Effective Interest',
            interval=1
        )

    return res


def nom_int_from_nom_disc(
        dm: float,
        m: float,
        new_m: float = None
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal discount rate, along \
    with a desired compounding frequency, returns a nominal interest rate at the desired compounding frequency.

    :param dm: the nominal discount rate.
    :type dm: float
    :param m: the compounding frequency.
    :type m: float
    :param new_m: the desired compounding frequency.
    :type new_m: float
    :return: a nominal interest rate, compounded new_m times per year
    :rtype: RateTemplate
    """
    if new_m is None:
        new_m = m

    p = m
    dp = dm

    i = ((1 - dp / p) ** (-p)) - 1

    res = nom_int_from_eff_int(i=i, new_m=new_m)

    return res


def eff_disc_from_nom_disc(
        dm: float,
        m: float,
        new_t: float,
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal discount rate, along \
    with a desired unit of time, returns an effective discount rate at the desired unit of time.


    :param dm: the nominal discount rate.
    :type dm: float
    :param m: the compounding frequency.
    :type m: float
    :param new_t: the desired unit of time.
    :type new_t: float
    :return: an effective discount rate, at the desired unit of time.
    :rtype: RateTemplate
    """

    d = effective_from_nominal_disc(dm=dm, m=m)

    if new_t is not None:
        res = eff_disc_from_eff_disc(d=d, old_t=1, new_t=new_t)
    else:
        res = RateTemplate(
            rate=d,
            formal_pattern='Effective Discount',
            interval=1
        )

    return res


def nom_disc_from_nom_disc(
        dm: float,
        m: float,
        new_m: float
) -> RateTemplate:
    """
    A nominal/effective interest/discount rate converter. Given a nominal discount rate, along \
    with a desired compounding frequency, returns an nominal discount rate at the desired compounding frequency.

    :param dm: the nominal discount rate.
    :type dm: float
    :param m: the compounding frequency.
    :type m: float
    :param new_m: the desired compounding frequency.
    :type new_m: float
    :return: a nominal discount rate, compounded new_m times per year.
    :rtype: RateTemplate
    """

    d = effective_from_nominal_disc(dm=dm, m=m)
    res = nom_disc_from_eff_disc(d=d, new_m=new_m)

    return res


def delta_from_eff_int(
        i: float,
        old_t: float = None
) -> RateTemplate:

    rate = eff_int_from_eff_int(
        i=i,
        old_t=old_t,
        new_t=1
    )

    i = rate.rate
    delta = np.log(1+i)

    res = RateTemplate(
        rate=delta,
        formal_pattern='Force of Interest'
    )

    return res


def delta_from_nom_int(
        im: float,
        m: float
) -> RateTemplate:

    rate = eff_int_from_nom_int(
        im=im,
        m=m,
        new_t=1
    )

    i = rate.rate
    delta = np.log(1 + i)

    res = RateTemplate(
        rate=delta,
        formal_pattern='Force of Interest'
    )

    return res


def delta_from_eff_disc(
        d: float,
        old_t: float
) -> RateTemplate:

    rate = eff_int_from_eff_disc(
        d=d,
        old_t=old_t,
        new_t=1
    )

    i = rate.rate
    delta = np.log(1 + i)

    res = RateTemplate(
        rate=delta,
        formal_pattern='Force of Interest'
    )
    return res


def delta_from_nom_disc(
        dm: float,
        m: float
) -> RateTemplate:

    rate = eff_int_from_nom_disc(
        dm=dm,
        m=m,
        new_t=1
    )

    i = rate.rate
    delta = np.log(1 + i)

    res = RateTemplate(
        rate=delta,
        formal_pattern='Force of Interest'
    )

    return res


def eff_int_from_delta(
        delta: float,
        new_t: float
) -> RateTemplate:

    i = np.exp(delta) - 1

    if new_t:
        res = eff_int_from_eff_int(
            i=i, old_t=1,
            new_t=new_t
        )

    else:
        res = RateTemplate(
            rate=i,
            formal_pattern='Effective Interest',
            interval=1
        )

    return res


def nom_int_from_delta(
        delta: float,
        new_m: float
) -> RateTemplate:

    rate = eff_int_from_delta(
        delta=delta,
        new_t=1
    )
    i = rate.rate

    res = nom_int_from_eff_int(
        i=i,
        new_m=new_m,
        old_t=1
    )

    return res


def eff_disc_from_delta(
        delta: float,
        new_t: float
) -> RateTemplate:

    rate = eff_int_from_delta(
        delta=delta,
        new_t=1
    )

    i = rate.rate

    res = eff_disc_from_eff_int(
        i=i,
        old_t=1,
        new_t=new_t
    )

    return res


def nom_disc_from_delta(
        delta: float,
        new_m: float
) -> RateTemplate:

    rate = eff_int_from_delta(
        delta=delta,
        new_t=1
    )

    i = rate.rate

    res = nom_disc_from_eff_int(
        i=i,
        new_m=new_m,
        old_t=1
    )

    return res


def any_from_eff_int(
        i: float,
        old_t: float,
        formal_pattern: str,
        freq: float = None,
        interval: float = None,
) -> RateTemplate:

    if formal_pattern == "Effective Interest":

        res = eff_int_from_eff_int(
            i=i,
            old_t=old_t,
            new_t=interval
        )

    elif formal_pattern == "Effective Discount":

        res = eff_disc_from_eff_int(
            i=i,
            old_t=old_t,
            new_t=interval
        )

    elif formal_pattern == "Nominal Interest":

        res = nom_int_from_eff_int(
            i=i,
            old_t=old_t,
            new_m=freq
        )

    elif formal_pattern == "Nominal Discount":

        res = nom_disc_from_eff_int(
            i=i,
            old_t=old_t,
            new_m=freq
        )

    elif formal_pattern == "Force of Interest":

        res = delta_from_eff_int(
            i=i,
            old_t=old_t
        )

    else:
        raise Exception("Invalid formal property specified")

    return res


def any_from_eff_disc(
        d: float,
        old_t: float,
        formal_pattern: str,
        freq: float = None,
        interval: float = None
) -> RateTemplate:

    if formal_pattern == "Effective Interest":

        res = eff_int_from_eff_disc(
            d=d,
            old_t=old_t,
            new_t=interval
        )

    elif formal_pattern == "Effective Discount":

        res = eff_disc_from_eff_disc(
            d=d, old_t=old_t,
            new_t=interval
        )

    elif formal_pattern == "Nominal Interest":

        res = nom_int_from_eff_disc(
            d=d,
            old_t=old_t,
            new_m=freq
        )

    elif formal_pattern == "Nominal Discount":

        res = nom_disc_from_eff_disc(
            d=d,
            old_t=old_t,
            new_m=freq
        )

    elif formal_pattern == "Force of Interest":

        res = delta_from_eff_disc(
            d=d,
            old_t=old_t
        )

    else:
        raise Exception("Invalid formal property specified")
    return res


def any_from_nom_int(
        im: float,
        m: float,
        formal_pattern: str,
        freq: float = None,
        interval: float = None
) -> RateTemplate:

    if formal_pattern == "Effective Interest":

        res = eff_int_from_nom_int(
            im=im,
            m=m,
            new_t=interval
        )

    elif formal_pattern == "Effective Discount":

        res = eff_disc_from_nom_int(
            im=im,
            m=m,
            new_t=interval
        )

    elif formal_pattern == "Nominal Interest":

        res = nom_int_from_nom_int(
            im=im,
            m=m,
            new_m=freq
        )

    elif formal_pattern == "Nominal Discount":

        res = nom_disc_from_nom_int(
            im=im,
            m=m,
            new_m=freq
        )

    elif formal_pattern == "Force of Interest":

        res = delta_from_nom_int(
            im=im,
            m=m
        )

    else:
        raise Exception("Invalid formal property specified")
    return res


def any_from_nom_disc(
        dm: float,
        m: float,
        formal_pattern: str,
        freq: float = None,
        interval: float = None
) -> RateTemplate:

    if formal_pattern == "Effective Interest":

        res = eff_int_from_nom_disc(
            dm=dm,
            m=m,
            new_t=interval
        )
    elif formal_pattern == "Effective Discount":

        res = eff_disc_from_nom_disc(
            dm=dm,
            m=m,
            new_t=interval
        )

    elif formal_pattern == "Nominal Interest":

        res = nom_int_from_nom_disc(
            dm=dm,
            m=m,
            new_m=freq
        )

    elif formal_pattern == "Nominal Discount":

        res = nom_disc_from_nom_disc(
            dm=dm,
            m=m,
            new_m=freq
        )

    elif formal_pattern == "Force of Interest":

        res = delta_from_nom_disc(
            dm=dm,
            m=m
        )

    else:
        raise Exception("Invalid formal property specified")
    return res


def any_from_delta(
        delta: float,
        formal_pattern: str,
        freq: float = None,
        interval: float = None
) -> RateTemplate:

    if formal_pattern == "Effective Interest":

        res = eff_int_from_delta(
            delta=delta,
            new_t=interval
        )

    elif formal_pattern == "Effective Discount":

        res = eff_disc_from_delta(
            delta=delta,
            new_t=interval
        )

    elif formal_pattern == "Nominal Interest":

        res = nom_int_from_delta(
            delta=delta,
            new_m=freq
        )
    elif formal_pattern == "Nominal Discount":

        res = nom_disc_from_delta(
            delta=delta,
            new_m=freq
        )

    elif formal_pattern == "Force of Interest":

        res = RateTemplate(
            rate=delta,
            formal_pattern='Force of Interest'
        )

    else:
        raise Exception("Invalid formal property specified")
    return res


def any_from_simp_int(
        s: float,
        old_t: float,
        formal_pattern: str,
        interval: float
) -> RateTemplate:

    s_std = s / old_t

    if formal_pattern == "Simple Interest":

        new_s = s_std * interval

        res = RateTemplate(
            rate=new_s,
            formal_pattern=formal_pattern,
            interval=interval
        )

    else:
        raise Exception("Invalid formal property specified")

    return res


def any_from_simp_disc(
        d: float,
        old_t: float,
        formal_pattern: str,
        interval: float
) -> RateTemplate:

    d_std = d / old_t

    if formal_pattern == "Simple Discount":

        new_d = d_std * interval

        res = RateTemplate(
            rate=new_d,
            formal_pattern=formal_pattern,
            interval=interval
        )

    else:
        raise Exception("Invalid formal property specified")

    return res


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


def effective_from_nominal_int(
        im: float,
        m: float
) -> float:
    """
    A nominal/effective interest rate converter. Given a :class:`.NominalInt` object, returns the
    effective interest rate. You may also supply the nominal interest rate and compounding frequency, but not when \
    a :class:`.NominalInt` is already supplied and vice-versa.

    :param im: the nominal interest rate.
    :type im: float
    :param m: the compounding frequency.
    :type m: float
    :return: the effective interest rate.
    :rtype: float
    """

    return (1 + im / m) ** m - 1


def effective_from_nominal_disc(
        dm: float,
        m: float
):
    """
    A nominal/effective discount rate converter. Given a :class:`.NominalDisc` object, returns the
    effective discount rate. You may also supply the nominal discount rate and compounding frequency, but not when \
    a :class:`.NominalDisc` is already supplied and vice-versa.

    :param dm: the nominal discount rate.
    :type dm: float
    :param m: the compounding frequency.
    :type m: float
    :return: the effective discount rate
    :rtype: float
    """

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


def apr(i: float, m: float) -> RateTemplate:
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
