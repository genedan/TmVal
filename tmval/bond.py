"""
This file contains the Bond class, which is TmVal's class for representing bonds
"""
import numpy as np

from typing import Union

from tmval.annuity import Annuity
from tmval.growth import standardize_acc, TieredTime
from tmval.rate import Rate
from tmval.value import Payments


class Bond(Payments):

    def __init__(
        self,
        face,
        term,
        red: float = None,
        gr: Union[float, Rate] = None,
        cgr: Rate = None,
        alpha: Union[float, list] = None,
        cfreq: Union[float, list] = None,
        price: float = None
    ):

        cgr_dict = parse_cgr(alpha=alpha, cfreq=cfreq, cgr=cgr)
        self.cgr = cgr_dict['cgr']
        self.alpha = cgr_dict['alpha']
        self.cfreq = cgr_dict['cfreq']

        self.fr_is_level = isinstance(self.alpha, (float, int))

        self.face = face
        self.term = term
        self.fr = self.get_coupon_amt()
        print(self.fr)

        if not self.fr_is_level:
            self.coupon_intervals = self.get_coupon_intervals()

        self.n_coupons = self.get_n_coupons()

        args = [gr, red, price]
        n_missing = args.count(None)

        if n_missing == 1:
            if price is None:

                self.red = red
                self.gr = standardize_acc(gr)
                self.coupons = self.get_coupons()
                print(self.coupons.amounts)
                print(self.coupons.times)

                amounts = self.coupons.amounts + [self.red]
                times = self.coupons.times + [self.term]

                Payments.__init__(
                    self,
                    amounts=amounts,
                    times=times,
                    gr=self.gr
                )

                self.price = self.npv()

            elif gr is None:

                self.red = red
                self.price = price

                amounts = [-price] + [self.fr] * self.n_coupons + [red]
                times = [0] + self.get_coupon_times() + [term]

                pmts = Payments(
                    amounts=amounts,
                    times=times
                )

                irr = [x for x in pmts.irr() if x > 0]
                self.gr = standardize_acc(min(irr))

                self.coupons = self.get_coupons()

                amounts = self.coupons.amounts + [self.red]
                times = self.coupons.times + [self.term]

                Payments.__init__(
                    self,
                    amounts=amounts,
                    times=times,
                    gr=self.gr
                )

            else:

                self.red = red
                self.gr = standardize_acc(gr)
                self.price = price
                self.coupons = self.get_coupons()
                self.red = self.get_redemption()

                amounts = self.coupons.amounts + [self.red]
                times = self.coupons.times + [self.term]

                Payments.__init__(
                    self,
                    amounts=amounts,
                    times=times,
                    gr=self.gr
                )

        self.append(amounts=[-self.price], times=[0])

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
            print(self.coupon_intervals)
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


def parse_cgr(
    alpha: Union[float, list] = None,
    cfreq: Union[float, list] = None,
    cgr: Union[Rate, TieredTime] = None
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
    # elif isinstance(gr, list):
    #     alphas = [(x[0].rate, x[1]) for x in gr]
    #     cfreqs = [(x[0].freq, x[1]) for x in gr]
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
