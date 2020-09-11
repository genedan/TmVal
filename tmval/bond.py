"""
This file contains the Bond class, which is TmVal's class for representing bonds
"""
import numpy as np

from math import floor
from typing import Union

from tmval.annuity import Annuity
from tmval.growth import standardize_acc, TieredTime
from tmval.rate import Rate
from tmval.value import Payments


class Bond(Payments):

    def __init__(
        self,
        face: float = None,
        term: float = None,
        red: float = None,
        gr: Union[float, Rate] = None,
        cgr: Rate = None,
        alpha: Union[float, list] = None,
        cfreq: Union[float, list] = None,
        price: float = None,
        pd: float = None,
        k: float = None,
        fr: float = None
    ):

        self.face = face
        self.term = term

        if [cgr, alpha].count(None) == 2:
            c_args = None
        else:
            c_args = len([cgr, alpha])

        if c_args:

            cgr_dict = parse_cgr(alpha=alpha, cfreq=cfreq, cgr=cgr)
            self.cgr = cgr_dict['cgr']
            self.alpha = cgr_dict['alpha']
            self.cfreq = cgr_dict['cfreq']

            self.fr_is_level = isinstance(self.alpha, (float, int))

            self.fr = self.get_coupon_amt()

            if not self.fr_is_level:
                self.coupon_intervals = self.get_coupon_intervals()
        else:
            self.fr = fr
            self.cfreq = cfreq

        args = [gr, red, price, term, c_args]

        n_missing = args.count(None)

        if n_missing == 1:

            if price is None:
                self.n_coupons = self.get_n_coupons()
                self.red = red
                self.gr = standardize_acc(gr)
                self.coupons = self.get_coupons()

            elif gr is None:
                self.n_coupons = self.get_n_coupons()
                self.red = red
                self.price = price

                amounts = [-price] + [self.fr] * self.n_coupons + [red]
                times = [0.0] + self.get_coupon_times() + [term]

                pmts = Payments(
                    amounts=amounts,
                    times=times
                )

                irr = [x for x in pmts.irr() if x > 0]
                self.gr = standardize_acc(min(irr))

                self.coupons = self.get_coupons()

            else:
                self.n_coupons = self.get_n_coupons()
                self.red = red
                self.gr = standardize_acc(gr)
                self.price = price
                self.coupons = self.get_coupons()
                self.red = self.get_redemption()

        elif n_missing == 2:
            if price is None and red is None:
                if pd is not None:
                    self.n_coupons = self.get_n_coupons()
                    self.gr = standardize_acc(gr)
                    self.coupons = self.get_coupons()

                    self.red = (self.coupons.pv() - pd) / (1 - self.gr.discount_func(t=self.term))

                    self.price = self.red + pd

                else:
                    raise Exception("Unable to evaluate bond. Too many missing arguments.")

            elif price is None and term is None:
                if k is not None:
                    self.gr = standardize_acc(gr)
                    self.red = red
                    self.g = self.fr / self.red

                    self.price = self.makeham(k=k)
                    self.term = self.gr.solve_t(pv=k, fv=self.red)
                    self.coupons = self.get_coupons()
                else:
                    raise Exception("Unable to evaluate bond. Too many missing arguments.")

            elif price is None and c_args is None:
                if fr is not None:
                    self.gr = standardize_acc(gr)
                    self.red = red
                    self.price = self.base_amount()
                    self.fr_is_level = True
                    self.fr = fr
                    self.n_coupons = self.get_n_coupons()
                    self.coupons = self.get_coupons()
                else:
                    raise Exception("Unable to evaluate bond. Too many missing arguments.")

            else:
                raise Exception("Unable to evaluate bond. Too many missing arguments.")

        else:
            raise Exception("Unable to evaluate bond. Too many missing arguments.")

        amounts = self.coupons.amounts + [self.red]
        times = self.coupons.times + [self.term]

        Payments.__init__(
            self,
            amounts=amounts,
            times=times,
            gr=self.gr
        )

        if price is None:
            self.price = self.npv()
        else:
            pass

        self.append(amounts=[-self.price], times=[0])

        if self.fr_is_level:
            self.j = self.gr.val(1/self.cfreq) - 1
            self.base = self.fr / self.j
            self.g = self.fr / self.red

        self.premium = self.price - self.red
        self.discount = self.red - self.price

    def get_coupon_times(self) -> list:
        times = [(x + 1) * 1 / self.cfreq for x in range(self.n_coupons)]

        return times

    def get_coupon_amt(self):

        if self.fr_is_level:
            coupon_amt = self.face * self.alpha / self.cfreq
        else:
            coupon_amt = []
            for a, c in zip(self.alpha, self.cfreq):
                amt = self.face * a[0] / c
                coupon_amt += [(amt, a[1])]

        return coupon_amt

    def get_redemption(self):
        c = (self.price - self.coupons.pv()) * self.gr.val(self.term)
        return c

    def get_n_coupons(
            self
    ):
        if self.fr_is_level:
            n_coupons = self.term * self.cfreq
        else:
            n_coupons = 0
            for t, c in zip(self.coupon_intervals, self.cfreq):
                n_coupons += t * c

        return n_coupons

    def get_coupons(self):

        if self.fr_is_level:

            coupons = Annuity(
                gr=self.gr,
                amount=self.fr,
                period=1/self.cfreq,
                term=self.term
            )

        else:
            times = []
            amounts = []
            base = 0
            for a, c, t in zip(self.fr, self.cfreq, self.coupon_intervals):

                n_pmt = t * c
                amounts += [a[0]] * n_pmt
                times += [(x + base + 1) / c for x in range(n_pmt)]
                base += n_pmt

            coupons = Annuity(
                gr=self.gr,
                amount=amounts,
                times=times,
                term=self.term
            )

        return coupons

    def get_coupon_intervals(self) -> list:

        if self.fr_is_level:
            times = []
        else:
            times = [a[1] for a in self.alpha]
            times += [self.term]
            times = np.diff(times)

        return times

    def makeham(self, k):
        j = self.gr.val(1/self.cfreq)
        p = self.g / j * (self.red - k + k)
        return p

    def base_amount(self):
        j = self.gr.val(1 / self.cfreq)
        g = self.fr / j
        p = (self.red - g) * self.gr.discount_func(self.term) + g
        return p

    def balance(self, t):
        n = self.n_coupons
        t0 = floor(t * self.cfreq)
        g = self.g
        c = self.red
        j = self.j

        if t < self.term:
            ann = Annuity(
                gr=j,
                n=n - t0,
            )

            bt = c * (g - j) * ann.pv() + c
        elif t == self.term:
            bt = self.red
        else:
            bt = 0

        return bt

    def am_prem(self, t):
        j = self.j
        c = self.red
        g = self.g

        last_coupon = max([x for x in self.coupons.times if x <= t])

        ti = self.coupons.times.index(last_coupon)

        t0 = self.coupons.times[ti - 1] if ti > 0 else 0

        pt = c * (g - j) * self.gr.discount_func(self.term - t0)
        return pt

    def acc_disc(self, t):
        pt = self.am_prem(t)
        ad = - pt
        return ad

    def am_interest(self, t):
        pt = self.am_prem(t)
        it = self.fr - pt
        return it

    def amortization(self):
        res = {
            'time': [],
            'coupon_payment': [],
            'interest': [],
            'premium': [],
            'balance': []
        }

        res['time'] += [0]
        res['coupon_payment'] += [None]
        res['interest'] += [None]
        res['premium'] += [None]
        res['balance'] += [self.price]

        for t, c in zip(self.coupons.times, self.coupons.amounts):

            res['time'] += [t]
            res['coupon_payment'] += [c]
            res['interest'] += [self.am_interest(t)]
            res['premium'] += [self.am_prem(t)]
            res['balance'] += [self.balance(t)]

        return res

    def dirty(self, t, prac=False, j: Union[float, Rate] = None):

        t0 = max([x for x in self.coupons.times if x <= t])

        # get next coupon time
        ti = self.coupons.times.index(t0)

        t1 = self.coupons.times[ti + 1]

        f = (t - t0) / (t1 - t0)

        if j is None:
            j_factor = (1 + self.gr.effective_interval(t1=t0, t2=t))
            balance = self.balance(t)
        else:
            jgr = standardize_acc(j)
            j_factor = (1 + jgr.effective_interval(t1=t0, t2=t))

            amounts = self.coupons.amounts[(ti + 1):]
            times = self.coupons.times[(ti + 1):]
            times = [x - t0 for x in times]
            red_t = self.term - t0

            amounts += [self.red]
            times += [red_t]

            pmts = Payments(
                amounts=amounts,
                times=times,
                gr=jgr
            )

            balance = pmts.npv()

        if not prac:

            dt = balance * j_factor

        else:

            dt = self.balance(t) * (1 + self.j * f)

        return dt

    def clean(self, t, j=None, prac=False):
        t0 = max([x for x in self.coupons.times if x <= t])

        # get next coupon time
        ti = self.coupons.times.index(t0)

        t1 = self.coupons.times[ti + 1]

        # get next coupon amount

        cg = self.coupons.amounts[ti + 1]

        f = (t - t0) / (t1 - t0)

        if j is None:
            j = self.gr

        else:
            pass

        jgr = standardize_acc(j)
        j0 = jgr.effective_interval(t1=t0, t2=t1)

        if not prac:
            dt = self.dirty(t=t, j=j)
            ct = dt - cg * ((1 + j0) ** f - 1) / j0
        else:
            dt = self.dirty(t=t, prac=True)
            ct = dt - f * cg

        return ct

    def accrued_interest(self, t, j=None, prac=False):
        # get the next coupon

        t0 = max([x for x in self.coupons.times if x <= t])
        ti = self.coupons.times.index(t0)
        t1 = self.coupons.times[ti + 1]

        cg = self.coupons.amounts[ti + 1]

        f = (t - t0) / (t1 - t0)

        if prac:
            at = f * cg

        else:
            if j is None:
                j = self.gr
            j = standardize_acc(j)
            j = j.effective_interval(t1=t0, t2=t1)
            at = cg * (((1 + j) ** f) - 1) / j

        return at

    def yield_s(self, t, sale):
        t0 = max([x for x in self.coupons.times if x <= t])
        ti = self.coupons.times.index(t0)

        amounts = self.coupons.amounts[:(ti + 1)]
        times = self.coupons.times[:(ti + 1)]

        amounts += [-self.price] + [sale]
        times += [0] + [t]

        pmts = Payments(amounts=amounts, times=times)

        return pmts.irr()

    def yield_j(self, t, sale):
        t0 = max([x for x in self.coupons.times if x <= t])
        ti = self.coupons.times.index(t0)

        amounts = self.coupons.amounts[(ti + 1):]
        times = self.coupons.times[(ti + 1):]
        times = [x - t for x in times]
        red_t = self.term - t

        amounts += [-sale] + [self.red]
        times += [0] + [red_t]

        pmts = Payments(amounts=amounts, times=times)

        return pmts.irr()

    def sale_prem(self, t, j):
        prem = self.clean(t=t, j=j) - self.red
        return prem

    def last_coupon_amt(self, t):
        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        coupon = self.coupons.amounts[ti]
        return coupon

    def next_coupon_amt(self, t):
        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        coupon = self.coupons.amounts[ti + 1]
        return coupon

    def last_coupon_t(self, t):
        return max([x for x in self.coupons.times if x <= t])

    def next_coupon_t(self, t):
        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        t1 = self.coupons.times[ti + 1]

        return t1

    def coupon_bound_t(self, t) -> tuple:
        t0 = self.last_coupon_t(t=t)
        t1 = self.next_coupon_t(t=t)

        return t0, t1

    def coupon_f(self, t):
        t0, t1 = self.coupon_bound_t(t=t)

        f = (t - t0) / (t1 - t0)

        return f

    def adj_principal(self, t, j=None, prac=False):
        t1 = self.next_coupon_t(t=t)
        f = self.coupon_f(t=t)

        if prac:
            pt = self.am_prem(t=t1)
            adj_p = f * pt
        else:
            t0 = self.last_coupon_t(t=t)

            if j is None:
                j = self.j
            else:
                jgr = standardize_acc(j)
                j = jgr.effective_interval(t1=t0, t2=t1)

            sv = ((1 + j) ** f - 1) / j

            c = self.red
            g = self.g
            n = self.term

            adj_p = sv * c * (g - j) * (1 + j) ** (- (n - t0))

        return adj_p

    def interest_on_accrued(self, t, j=None, prac=False):

        if prac:
            adj_p = self.adj_principal(t=t, prac=True)
            at = self.accrued_interest(t=t, prac=True)

        else:
            adj_p = self.adj_principal(t=t, j=j)
            at = self.accrued_interest(t=t, j=j)

        it = at - adj_p

        return it

    def yield_c(self, times=None, premiums=None):

        if times is None:
            return self.irr()
        else:
            yields = []
            if isinstance(times, (float, int)):
                times = [times]
            else:
                pass

            if premiums is None:
                premiums = [0] * len(times)
            elif isinstance(premiums, (float, int)):
                premiums = [premiums]
            else:
                pass

            for t, p in zip(times, premiums):
                coupons = self.prior_coupons(t=t)
                amounts = coupons.amounts
                coupon_times = coupons.times

                amounts += [-self.price] + [self.red + p]
                coupon_times += [0] + [t]

                pmts = Payments(amounts=amounts, times=coupon_times)

                yields += pmts.irr()

            if len(times) == 1:

                res = yields

            else:

                res = {
                    'times': times,
                    'yields': yields
                }

            return res

    def prior_coupons(self, t) -> Payments:
        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        amounts = self.coupons.amounts[:ti + 1]
        times = self.coupons.times[:ti + 1]

        pmts = Payments(amounts=amounts, times=times)

        return pmts


def parse_cgr(
    alpha: Union[float, list] = None,
    cfreq: Union[float, list] = None,
    cgr: Union[Rate, TieredTime] = None,
    fr: float = None
) -> dict:

    if alpha is not None and cfreq is not None:

        if isinstance(alpha, (float, int)) \
                and isinstance(cfreq, (float, int)):

            gr = Rate(
                rate=alpha,
                pattern="Nominal Interest",
                freq=cfreq
            )

        elif isinstance(alpha, list) \
                and isinstance(cfreq, list):

            tiers = []
            rates = []
            for a, c in zip(alpha, cfreq):
                rates += [
                    Rate(
                        rate=a[0],
                        pattern="Nominal Interest",
                        freq=c
                    )
                ]

                tiers += [a[1]]

            gr = TieredTime(
                tiers=tiers,
                rates=rates
            )

        else:
            raise TypeError("Invalid type passed to alpha or cfreq")

    elif cgr is not None:

        gr = cgr

    elif (alpha is not None or cfreq is not None) and cgr is not None:
        raise ValueError("When using cgr to specify coupon rate, leave alpha and cfreq blank.")
    else:
        raise Exception("Cannot determine coupon rate.")

    if isinstance(gr, Rate):
        alphas = gr.rate
        cfreqs = gr.freq
    elif isinstance(gr, TieredTime):
        alphas = [(x.rate, y) for x, y in zip(gr.rates, gr.tiers)]
        cfreqs = [x.freq for x in gr.rates]
    else:
        raise Exception("cgr parsing failed.")

    res = {
        'cgr': gr,
        'alpha': alphas,
        'cfreq': cfreqs
    }

    return res


# def bsolve_g_from_am_prem(
#         am: float,
#         gr,
#         alpha,
#         cfreq,
#         term,
#         t
# ):
#     n = term * cfreq
#     cgr_dict = parse_cgr(alpha=alpha, cfreq=cfreq)
#     cgr = cgr_dict['cgr']
#     j = cgr.rate / cgr.freq
#
#     acc = Accumulation(gr=j)

