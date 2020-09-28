import numpy as np

from math import floor
from typing import Iterable, Tuple, Union

from tmval.growth import Accumulation, standardize_acc
from tmval.value import Payments
from tmval.stock import Stock
from tmval.loan import Loan


class Call:
    def __init__(
        self,
        n,
        k,
        t,
        s0=None,
        c0=None
    ):

        self.n = n
        self.k = k
        self.c0 = c0
        self.t = t
        self.s0 = s0

    def intrinsic_value(self, stp):
        return self.n * (stp - self.k)

    def time_premium(self, stp):
        return self.c0 - self.intrinsic_value(stp=stp)

    def yld(self, stp, t, x0=1.05):
        times = [0, t]
        amounts = [-self.c0, (stp - self.k) * self.n]

        pmts = Payments(
            times=times,
            amounts=amounts
        )

        return pmts.irr(x0=x0)

    def binomial_price(self, u, d, gr):
        rf_fac = Accumulation(gr=gr).val(self.t)
        vd = max(d - self.k, 0)
        vu = max(u - self.k, 0)
        c0 = (u * vd - d * vu) / ((u - d) * rf_fac) + (vu - vd) / (u - d) * self.s0
        return c0

    def binomial_d(self, u, gr):
        rf_fac = Accumulation(gr=gr).val(self.t)
        vu = max(u - self.k, 0)
        c0 = self.c0
        s0 = self.s0

        return (c0 * u - vu * s0) / (c0 - vu / rf_fac)

    def binomial_delta(self, u, d, nu, nd, gr, period):

        return binomial_delta(
            s0=self.s0,
            k=self.k,
            n=self.n,
            t=self.t,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            gr=gr,
            period=period,
            option='call'
        )

    def binomial_f(self, u, d, nu, nd, gr, period):

        return binomial_f(
            n=self.n,
            s0=self.s0,
            t=self.t,
            k=self.k,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            gr=gr,
            period=period,
            option='call'
        )

    def binomial_st(self, u, d, nu, nd):
        return binomial_st(s0=self.s0, n=self.n, u=u, d=d, nu=nu, nd=nd)

    def binomial_node(self, u, d, nu, nd, gr, period):

        return binomial_node(
            s0=self.s0,
            n=self.n,
            t=self.t,
            k=self.k,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            gr=gr,
            period=period,
            option='call'
        )

    def risk_neutral_prob(self, gr, u, d, nu=0, nd=0, period=None):

        return risk_neutral_prob(
            t=self.t,
            s0=self.s0,
            gr=gr,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            period=period
        )

    def risk_neutral_price(self, gr, u, d, nu, nd, period: Union[float, list]):

        return risk_neutral_price(
            s0=self.s0,
            t=self.t,
            k=self.k,
            n=self.n,
            gr=gr,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            period=period,
            option='call'
        )

    def decomp(self, u, d, gr, nu, nd, period) -> Tuple[Loan, Stock]:
        """
        Decomposes an option into an equivalent loan and stock. May generalize the stock to be any kind of \
        underlier in the future.

        :param u:
        :type u:
        :param d:
        :type d:
        :param gr:
        :type gr:
        :param period:
        :type period:
        :return:
        :rtype:
        """
        delta = self.binomial_delta(u=u, d=d, nu=nu, nd=nd, gr=gr, period=period)

        st = self.binomial_st(u=u, d=d, nu=nu, nd=nd)
        st = Stock(gr=gr, shares=self.n * delta, price=st / self.n)
        price = self.binomial_node(u=u, d=d, nu=nu, nd=nd, gr=gr, period=period)
        loan_amt = st.value - price
        loan_res = Loan(gr=gr, term=self.t, amt=loan_amt, period=self.t)

        return loan_res, st


class Put:
    def __init__(
        self,
        n,
        k,
        t,
        s0=None,
        c0=None
    ):

        self.n = n
        self.k = k
        self.s0 = s0
        self.t = t
        self.c0 = c0

    def payoff(self, stp, cost):
        return self.n * max(stp, self.k) - self.s0 - cost

    def binomial_st(self, u, d, nu, nd):
        return binomial_st(s0=self.s0, n=self.n, u=u, d=d, nu=nu, nd=nd)

    def binomial_delta(self, u, d, nu, nd, gr, period):
        return binomial_delta(
            s0=self.s0,
            k=self.k,
            n=self.n,
            t=self.t,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            gr=gr,
            period=period,
            option='put'
        )

    def binomial_f(self, u, d, nu, nd, gr, period):

        return binomial_f(
            n=self.n,
            s0=self.s0,
            t=self.t,
            k=self.k,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            gr=gr,
            period=period,
            option='put'
        )

    def binomial_node(self, u, d, nu, nd, gr, period):

        return binomial_node(
            s0=self.s0,
            n=self.n,
            t=self.t,
            k=self.k,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            gr=gr,
            period=period,
            option='put'
        )

    def risk_neutral_prob(self, gr, u, d, nu=0, nd=0, period=None):

        return risk_neutral_prob(
            t=self.t,
            s0=self.s0,
            gr=gr,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            period=period
        )

    def risk_neutral_price(self, gr, u, d, nu, nd, period: Union[float, list]):

        return risk_neutral_price(
            s0=self.s0,
            t=self.t,
            k=self.k,
            n=self.n,
            gr=gr,
            u=u,
            d=d,
            nu=nu,
            nd=nd,
            period=period,
            option='put'
        )



def binomial_st(s0, n, u, d, nu, nd):
    return n * s0 * (1 + u) ** nu * (1 - d) ** nd


def binomial_node(s0, n, t, k, u, d, nu, nd, gr, period, option):

    n_periods = t / period

    if nu + nd == n_periods:

        st = binomial_st(
            s0=s0,
            n=n,
            u=u,
            d=d,
            nu=nu,
            nd=nd
        )

        if option == 'call':
            return max(st - k * n, 0)
        elif option == 'put':
            return max(k * n - st, 0)
        else:
            raise ValueError("Invalid option type specified")
    else:
        delta = binomial_delta(s0=s0, k=k, n=n, t=t, u=u, d=d, nu=nu, nd=nd, gr=gr, period=period, option=option)
        f = binomial_f(s0=s0, t=t, k=k, n=n, u=u, d=d, nu=nu, nd=nd, gr=gr, period=period, option=option)
        st = binomial_st(s0=s0, n=n, u=u, d=d, nu=nu, nd=nd)
    return f + delta * st


def binomial_delta(s0, k, n, t, u, d, nu, nd, gr, period, option):

    if nu + nd > t / period - 1:
        raise ValueError("Steps exceed option length.")

    vu = binomial_node(s0=s0, k=k, n=n, t=t, u=u, d=d, nu=nu+1, nd=nd, gr=gr, period=period, option=option)
    vd = binomial_node(s0=s0, k=k, n=n, t=t, u=u, d=d, nu=nu, nd=nd+1, gr=gr, period=period, option=option)

    su = binomial_st(s0=s0, n=n, u=u, d=d, nu=nu+1, nd=nd)
    sd = binomial_st(s0=s0, n=n, u=u, d=d, nu=nu, nd=nd+1)

    return (vu - vd) / (su - sd)


def binomial_f(n, s0, t, k, u, d, nu, nd, gr, period, option):

    if nu + nd > t / period - 1:
        raise ValueError("Steps exceed option length.")

    rf_factor = Accumulation(gr=gr).discount_func(t=period)

    vu = binomial_node(s0=s0, n=n, u=u, d=d, t=t, k=k, nu=nu + 1, nd=nd, gr=gr, period=period, option=option)
    vd = binomial_node(s0=s0, n=n, u=u, d=d, t=t, k=k, nu=nu, nd=nd + 1, gr=gr, period=period, option=option)

    su = binomial_st(n=n, s0=s0, u=u, d=d, nu=nu + 1, nd=nd)
    sd = binomial_st(n=n, s0=s0, u=u, d=d, nu=nu, nd=nd + 1)

    return rf_factor * (su * vd - sd * vu) / (su - sd)


def risk_neutral_prob(t, s0, gr, u, d, nu=0, nd=0, period=None):
    if period is None:
        period = t
    s0 = s0 * (1 + u) ** nu * (1 - d) ** nd

    rf_factor = Accumulation(gr=gr).discount_func(t=period)

    return (s0 - s0 * (1-d) * rf_factor) / ((s0 * (1 + u) - s0 * (1 - d)) * rf_factor)


def risk_neutral_price(s0, t, k, n, gr, u, d, nu, nd, period: Union[float, list], option):

    if isinstance(period, (int, float)):
        n_periods = t / period
        periods = [period] * floor(n_periods)
    else:
        n_periods = len(period)
        periods = period

    if nu + nd == n_periods:
        st = binomial_st(s0=s0, n=n, u=u, d=d, nu=nu, nd=nd)
        if option == 'call':
            return max(st - k * n, 0)
        elif option == 'put':
            return max(k * n - st, 0)
        else:
            raise ValueError("Invalid option type specified")
    else:
        t = periods[nu + nd]

        rf_factor = Accumulation(gr=gr).discount_func(t=t)

        p = risk_neutral_prob(s0=s0, t=t, gr=gr, u=u, d=d, period=t)

        vu = risk_neutral_price(s0=s0, n=n, k=k, t=t, gr=gr, u=u, d=d, nu=nu + 1, nd=nd, period=periods, option=option)
        vd = risk_neutral_price(s0=s0, n=n, k=k, t=t, gr=gr, u=u, d=d, nu=nu, nd=nd + 1, period=periods, option=option)
        return p * vu * rf_factor + (1 - p) * vd * rf_factor


class EquitySwap:
    def __init__(
        self,
        s0,
        gr,
    ):
        self.s0 = s0
        self.acc = standardize_acc(gr)

    def get_interest_payments(self, times):

        prev_times = times.copy()
        prev_times.pop()
        prev_times = [0.0] + prev_times
        i_s = [self.acc.effective_interval(t1=x, t2=y) for x, y in zip(prev_times, times)]
        pmts = [self.s0 * x for x in i_s]

        return pmts

    def get_gain_pmts(
        self,
        divs,
        sts
    ):
        sts = [self.s0] + sts
        gains = list(np.diff(sts))

        pmts = [x + y for x, y in zip(divs, gains)]

        return pmts

    def get_net_payments(
            self,
            times,
            divs,
            sts
    ):
        interest = self.get_interest_payments(times=times)
        gains = self.get_gain_pmts(divs=divs, sts=sts)

        pmts = [x - y for x, y in zip(interest, gains)]

        return pmts


class CurrencySwap:
    def __init__(
        self,
        n1,
        gr1,
        gr2,
        fx,
        period,
        term
     ):

        self.n1 = n1
        self.n2 = n1 * fx
        self.acc1 = standardize_acc(gr1)
        self.acc2 = standardize_acc(gr2)
        self.fx = fx
        self.period = period
        self.term = term

    def get_payments(self, perspective=1):
        n_payments = floor(self.term / self.period)
        times = [(x + 1) * self.period for x in range(n_payments)]
        times_p = times.copy()
        times_p = [0] + times_p
        if perspective == 1:

            interest_payments = [self.n2 * self.acc2.effective_interval(t1=x, t2=y)
                                 for x, y in zip(times_p, times)]
            pmts = interest_payments
            pmts[-1] += self.n2
        elif perspective == 2:
            print([self.acc1.effective_interval(t1=x, t2=y)
                   for x, y in zip(times_p, times)])
            interest_payments = [self.n1 * self.acc1.effective_interval(t1=x, t2=y)
                                 for x, y in zip(times_p, times)]

            pmts = interest_payments
            pmts[-1] += self.n1

        return pmts


class RateSwap:
    def __init__(
        self,
        principal,

    ):
        self.principal = principal
