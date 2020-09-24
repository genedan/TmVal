from tmval.growth import Accumulation
from tmval.value import Payments


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
            return max(k * st - st, 0)
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
