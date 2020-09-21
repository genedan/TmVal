"""
This file contains the Bond class, which is TmVal's class for representing bonds
"""
import numpy as np

from math import floor
from typing import Iterable, List, Union

from tmval.annuity import Annuity
from tmval.growth import Amount, standardize_acc, TieredTime
from tmval.rate import Rate
from tmval.value import Payments


class Bond(Payments):
    """
    Bond is TmVal's class for representing bonds. Bonds can be initialized if the arguments contain enough information
    to calculate:

    #. Bond price (price)
    #. Coupons (alpha and cfreq or cgr)
    #. Yield rate (gr)
    #. Redemption amount (red)
    #. Face value (face)
    #. Term (term)

    When one of these values is absent, the initialization will be able to solve for the missing quantity. When two
    values are missing, you can still initialize the bond under certain cases:

    #. Missing price and redemption amount - can be solved if premium/discount is supplied.
    #. Missing price and term - can be solved if Makeham's k is supplied.
    #. Missing price and coupon rate - can be solved if coupon amount is supplied.

    Coupon information is usually supplied by specifying an alpha amount for the nominal coupon rate and cfreq for the \
    coupon frequency. Alternatively, you may supply a nominal interest rate with a compounding frequency to the \
    argument cgr. It's possible to specify a coupon amount via fr and the coupon frequency of cfreq if you do not know \
    alpha but know the coupon amount.

    :param face: The face value.
    :type face: float
    :param red: The redemption amount.
    :type red: float
    :param gr: The yield rate used to price the bond.
    :type gr: float, Rate
    :param cgr: A nominal rate representing the coupon rate and frequency.
    :type cgr: Rate
    :param alpha: When supplied as a float, a nominal coupon rate. When supplied as a list of tuples of the form [(x1, \
    y_1), (x2, y2), ...], represents a series of coupon rates x supplied during periods beginning at time y. For \
    example alpha=[(.05, 0), (.04, 2)] means a 5% coupon rate the first two years and a 4% rate after that.
    :type alpha: float, list
    :param cfreq: The coupon frequency, or a list of coupon frequencies. When supplied as a list, alpha must also \
    be supplied as a list and each element in cfreq needs to correspond to a tuple in alpha.
    :type cfreq: float, list
    :param price: The bond price.
    :type price: float
    :param pd: The bond premium or discount.
    :type pd: float
    :param k: The present value of the redemption amount, used if instantiating from Makeham's formula.
    :type k: float
    :param fr: The coupon amount per period. Can be supplied with cfreq instead of alpha.
    :type fr: float
    """

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
        self.k = k

        if [cgr, alpha].count(None) == 2:
            c_args = None
            self.alpha = None
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

        if [red, k].count(None) == 2:
            red_args = None
        else:
            red_args = len([red, k])

        if term is not None:
            self.is_term_floor = self.term_floor()
        else:
            pass

        if [alpha, cfreq, fr, cgr].count(None) == 4:
            self.is_zero = True
        else:
            self.is_zero = False

        if self.is_zero:
            args = [gr, red_args, price, term]
        else:
            args = [gr, red_args, price, term, c_args]

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

                if self.is_zero:
                    amounts = [-price, red]
                elif self.fr_is_level:
                    amounts = [-price] + [self.fr] * self.n_coupons + [red]
                else:
                    amounts = [-price]
                    cis = self.get_coupon_intervals()

                    for afr, cf, ci in zip(self.fr, self.cfreq, cis):
                        n = cf * ci
                        amounts += [afr[0]] * n
                    amounts += [red]

                print(amounts)
                times = [0.0] + self.get_coupon_times() + [term]

                pmts = Payments(
                    amounts=amounts,
                    times=times
                )

                irr = [x for x in pmts.irr() if x > 0]
                self.gr = standardize_acc(min(irr))

                self.coupons = self.get_coupons()

            elif term is None:
                if self.is_zero:
                    self.red = red
                    self.gr = standardize_acc(gr)
                    self.price = price
                    self.term = Amount(gr=gr, k=price).solve_t(fv=red)

            else:
                self.n_coupons = self.get_n_coupons()
                self.red = red
                self.gr = standardize_acc(gr)
                self.price = price
                self.coupons = self.get_coupons()
                self.red = self.get_redemption()

        elif n_missing == 2:
            if price is None and red_args is None:
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

                    self.price = self.makeham()
                    self.term = self.gr.solve_t(pv=k, fv=self.red)
                    self.n_coupons = self.get_n_coupons()
                    self.coupons = self.get_coupons()
                    self.is_term_floor = self.term_floor()
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
                    self.alpha = None
                else:
                    raise Exception("Unable to evaluate bond. Too many missing arguments.")

            else:
                raise Exception("Unable to evaluate bond. Too many missing arguments.")

        else:
            raise Exception("Unable to evaluate bond. Too many missing arguments.")

        if self.is_zero:
            amounts = [self.red]
            times = [self.term]
        else:
            amounts = self.coupons.amounts + [self.red]
            times = self.coupons.times + [self.term]

        Payments.__init__(
            self,
            amounts=amounts,
            times=times,
            gr=self.gr
        )

        if price is None:
            if self.is_term_floor:
                self.price = self.npv()
            else:
                if self.n_coupons == 1:

                    j = self.gr.val(1 / self.cfreq) - 1
                    f = 1 - self.term / (1 / self.cfreq)
                    print((1 + (1 - f) * j))
                    self.price = (self.red + self.fr) / (1 + (1 - f) * j) - f * self.fr
                else:
                    self.price = self.clean(t=0)
        else:
            pass

        self.append(amounts=[-self.price], times=[0])

        if self.is_zero:
            pass
        elif self.fr_is_level:
            self.j = self.gr.val(1 / self.cfreq) - 1
            self.base = self.fr / self.j
            self.g = self.fr / self.red

        self.premium = self.price - self.red
        self.discount = self.red - self.price

        self.k = self.gr.discount_func(t=self.term, fv=self.red)

    def get_coupon_times(self) -> list:
        """
        Calculates the times at which the coupon payments occur.

        :return: A list of coupon payment times.
        :rtype: list
        """

        if self.is_zero:
            times = []
        elif self.fr_is_level:
            times = [(x + 1) * 1 / self.cfreq for x in range(self.n_coupons)]
        else:
            times = []
            coupon_intervals = self.get_coupon_intervals()
            for t, cf, a in zip(coupon_intervals, self.cfreq, self.alpha):
                at = a[1]
                n = t * cf
                times += [(x + 1) * 1 / cf + at for x in range(n)]

        return times

    def get_coupon_amt(self) -> Union[float, list]:
        """
        Calculates the coupon amount, or a list of coupon amounts and time periods in which they are applicable \
        if they are not level. In the case of non-level coupons, the list takes the form of [(x1, y1), (x2, y2), ...]
        Where the x values represent the coupon amounts and the y values represent the lower bound of the interval \
        in which the coupon amount is applicable. For example, [(50, 0), (60, 2)] means that coupon payments of 50
        happen in the first two periods and coupon payments of 60 happen afterwards.

        :return: A coupon amount, or list of coupon amounts.
        :rtype: float or list
        """

        if self.fr_is_level:
            coupon_amt = self.face * self.alpha / self.cfreq
        else:
            coupon_amt = []
            for a, c in zip(self.alpha, self.cfreq):
                amt = self.face * a[0] / c
                coupon_amt += [(amt, a[1])]

        return coupon_amt

    def get_redemption(self) -> float:
        """
        Calculates the redemption amount.

        :return: The redemption amount.
        :rtype: float
        """

        if self.is_zero:
            c = self.price * self.gr.val(self.term)
        else:
            c = (self.price - self.coupons.pv()) * self.gr.val(self.term)
        return c

    def get_n_coupons(
            self
    ) -> int:

        """
        Calculates the number of coupons.

        :return: The number of coupons.
        :rtype: int
        """

        if self.is_zero:
            n_coupons = 0
        elif self.fr_is_level:
            # if term is evenly divisible by period, assume bond purchased at beginning of period
            if round(self.term % (1 / self.cfreq), 5) == 0:
                n_coupons = self.term * self.cfreq

            # else, assume
            else:
                n_coupons = 1 + floor(self.term * self.cfreq)
        else:
            n_coupons = 0
            for t, c in zip(self.coupon_intervals, self.cfreq):
                n_coupons += t * c

        return n_coupons

    def get_coupons(self) -> Annuity:
        """
        Calculates the coupons and returns them as an Annuity object.

        :return: The bond coupons.
        :rtype: Annuity
        """
        if self.is_zero:
            coupons = None
        elif self.fr_is_level:

            if round(self.term % (1 / self.cfreq), 5) == 0:

                coupons = Annuity(
                    gr=self.gr,
                    amount=self.fr,
                    period=1 / self.cfreq,
                    term=self.term
                )

            else:
                period = 1 / self.cfreq
                f = self.term - ((self.n_coupons - 1) * period)
                coupons = Annuity(
                    gr=self.gr,
                    amount=self.fr,
                    n=self.n_coupons,
                    imd='due',
                    deferral=f
                )

        else:
            times = []
            amounts = []
            base = 0

            if isinstance(self.fr, Iterable)\
                    and isinstance(self.cfreq, Iterable)\
                    and isinstance(self.coupon_intervals, Iterable):

                for a, c, t in zip(self.fr, self.cfreq, self.coupon_intervals):
                    n_pmt = t * c
                    amounts += [a[0]] * n_pmt
                    times += [(x + base + 1) / c for x in range(n_pmt)]
                    base += n_pmt

            else:
                raise TypeError("fr, cfreq, and coupon_intervals must be iterable when coupons are nonlevel")

            coupons = Annuity(
                gr=self.gr,
                amount=amounts,
                times=times,
                term=self.term
            )

        return coupons

    def get_coupon_intervals(self) -> list:
        """
        Calculates the time intervals between coupon payments.

        :return: The time intervals between coupon payments.
        :rtype: list
        """
        if self.fr_is_level:
            times = []
        else:
            times = [a[1] for a in self.alpha]
            times += [self.term]
            times = np.diff(times)

        return times

    def makeham(self) -> float:
        """
        Calculates the bond price using Makeham's formula.

        :return: The bond price.
        :rtype: float
        """
        k = self.k
        j = self.gr.val(1/self.cfreq) - 1

        p = self.g / j * (self.red - k) + k
        return p

    def base_amount(self) -> float:
        """
        Calculates the base amount of the bond. The base amount is the investment needed to produce a perpetuity \
        of the coupon payments.

        :return: The base amount.
        :rtype: float
        """
        j = self.gr.val(1 / self.cfreq)
        g = self.fr / j
        p = (self.red - g) * self.gr.discount_func(self.term) + g
        return p

    def balance(
        self,
        t: float,
        n: int = None
    ) -> float:

        """
        Calculates the bond balance at time t, where t must coincide with a payment time. Alternatively, if you'd like \
        to know the balance just prior to the n-th coupon payment, you may supply the value to the argument n.

        :param t: The balance time.
        :type t: float
        :param n: The n-th coupon payment.
        :type n: int
        :return: The bond balance.
        :rtype: float
        """

        if t not in self.times:
            raise ValueError("Bond balance only available when t occurs on a payment date. For valuations "
                             "between payment dates, use the clean or dirty value formulas.")

        if n is not None and t is not None:
            raise ValueError("Can supply t or n, but not both.")

        if t is None:
            if n is not None:
                t = self.coupons.times[n - 1]
            else:
                raise ValueError("You need to supply a time or n-th coupon.")

        nc = self.n_coupons
        t0 = floor(t * self.cfreq)
        g = self.g
        c = self.red
        j = self.j

        if t < self.term:
            ann = Annuity(
                gr=j,
                n=nc - t0,
            )

            bt = c * (g - j) * ann.pv() + c
        elif t == self.term:
            bt = self.red
        else:
            bt = 0

        return bt

    def am_prem(
        self,
        t: float
    ) -> float:

        """
        Calculates the amortized premium in the last coupon payment prior to time t.

        :param t: The valuation time.
        :type t: float
        :return: The amortized premium.
        :rtype: float
        """
        j = self.j
        c = self.red
        g = self.g

        last_coupon = max([x for x in self.coupons.times if x <= t])

        ti = self.coupons.times.index(last_coupon)

        t0 = self.coupons.times[ti - 1] if ti > 0 else 0

        pt = c * (g - j) * self.gr.discount_func(self.term - t0)
        return pt

    def acc_disc(
        self,
        t: float
    ) -> float:

        """
        Calculates the accumulation of discount in the last coupon prior to time t.

        :param t: The valuation time.
        :type t: float
        :return: The accumulation of discount.
        :rtype: float
        """
        pt = self.am_prem(t)
        ad = - pt
        return ad

    def am_interest(
        self,
        t: float
    ) -> float:

        """
        Calculates the amortized interest in the last coupon prior to time t.

        :param t: The valuation time.
        :type t: float
        :return: The amortized interest.
        :rtype: float
        """
        pt = self.am_prem(t)
        it = self.fr - pt
        return it

    def amortization(self) -> dict:
        """
        Calculates the amortization table for the bond. This method returns a dictionary that can be supplied to \
        a pandas DataFrame.

        :return: The amortization table.
        :rtype: dict
        """
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

    def dirty(
        self,
        t: float,
        tprac: str = 'theoretical',
        gr: Union[float, Rate] = None
    ) -> float:

        """
        Calculates the dirty value of a bond. It can be toggled to switch between theoretical and practical dirty \
        values.

        :param t: The valuation time.
        :type t: float
        :param tprac: Whether you want the practical or theoretical dirty value. Defaults to 'theoretical'.
        :type tprac: str
        :param gr: The valuation yield, if pricing a bond at a different yield. Defaults to the current bond yield.
        :type gr: float, Rate
        :return: The dirty value.
        :rtype: float
        """
        if t == 0:
            t0 = 0

            ti = -1

            t1 = self.coupons.times[0]

        else:

            t0 = max([x for x in self.coupons.times if x <= t])

            # get next coupon time
            ti = self.coupons.times.index(t0)

            t1 = self.coupons.times[ti + 1]

            # get next coupon amount

        f = (t - t0) / (t1 - t0)

        if gr is None:
            j_factor = (1 + self.gr.effective_interval(t1=t0, t2=t))
            balance = self.balance(t0)
        else:
            jgr = standardize_acc(gr)
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

        if tprac == 'theoretical':

            dt = balance * j_factor

        elif tprac == 'practical':

            dt = self.balance(t0) * (1 + self.j * f)

        else:
            raise ValueError("tprac must be 'theoretical' or 'practical'.")

        return dt

    def clean(
        self,
        t: float,
        gr: Union[float, Rate] = None,
        tprac: str = 'theoretical'
    ) -> float:
        """
        Calculates the clean value. The argument tprac can be toggled to switch between the theoretical, \
        semipractical, or practical clean value.

        :param t: The valuation time.
        :type t: float
        :param gr: The valuation yield, if pricing a bond at a different yield. Defaults to the current bond yield.
        :type gr: float, Rate
        :param tprac: Whether you want the 'theoretical', 'semipractical', or 'practical' clean value.
        :type tprac: str
        :return: The clean value.
        :rtype: float
        """

        if t == 0:
            t0 = 0

            t1 = self.coupons.times[0]

            cg = self.coupons.amounts[0]

        else:

            t0 = max([x for x in self.coupons.times if x <= t])

            # get next coupon time
            ti = self.coupons.times.index(t0)

            t1 = self.coupons.times[ti + 1]

            # get next coupon amount

            cg = self.coupons.amounts[ti + 1]

        f = (t - t0) / (t1 - t0)

        if gr is None:
            gr = self.gr

        else:
            pass

        jgr = standardize_acc(gr)
        j0 = jgr.effective_interval(t1=t0, t2=t1)

        if tprac == 'theoretical':
            dt = self.dirty(t=t, gr=gr)
            ct = dt - cg * ((1 + j0) ** f - 1) / j0
        else:
            dt = self.dirty(t=t, tprac='practical')
            ct = dt - f * cg

        return ct

    def accrued_interest(
        self,
        t: float,
        gr: Union[float, Rate] = None,
        tprac: str = 'theoretical'

    ) -> float:
        """
        Calculates the accrued interest in a coupon payment. Can be toggled between the clean or practical values.

        :param t: The valuation time.
        :type t: float
        :param gr: The valuation yield, if pricing a bond at a different yield. Defaults to the current bond yield.
        :type gr: float, Rate
        :param tprac: Whether you want the 'theoretical' or 'practical' value.
        :type tprac: str
        :return: The accrued interest.
        :rtype: float
        """

        # get the next coupon

        t0 = max([x for x in self.coupons.times if x <= t])
        ti = self.coupons.times.index(t0)
        t1 = self.coupons.times[ti + 1]

        cg = self.coupons.amounts[ti + 1]

        f = (t - t0) / (t1 - t0)

        if tprac == "practical":
            at = f * cg

        elif tprac == "theoretical":
            if gr is None:
                gr = self.gr
            gr = standardize_acc(gr)
            j = gr.effective_interval(t1=t0, t2=t1)
            at = cg * (((1 + j) ** f) - 1) / j

        else:
            raise ValueError("tprac must be 'theoretical' or 'practical'")

        return at

    def yield_s(
        self,
        t: float,
        sale: float
    ) -> list:

        """
        Calculates the yield from the perspective of the person to whom you are selling the bond.

        :param t: The valuation time.
        :type t: float
        :param sale: The sale price.
        :type sale: float
        :return: The yield to the person to whom you are selling the bond.
        :rtype: list
        """

        t0 = max([x for x in self.coupons.times if x <= t])
        ti = self.coupons.times.index(t0)

        amounts = self.coupons.amounts[:(ti + 1)]
        times = self.coupons.times[:(ti + 1)]

        amounts += [-self.price] + [sale]
        times += [0.0] + [t]

        pmts = Payments(amounts=amounts, times=times)

        return pmts.irr()

    def yield_j(
        self,
        t: float,
        sale: float
    ) -> list:

        """
        Calculates the yield to the bondholder should they sell the bond at time t.

        :param t: The valuation time.
        :type t: float
        :param sale: The sale price.
        :type sale: float
        :return: The yield to the bondholder.
        :rtype: list
        """

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

    def sale_prem(
        self,
        t: float,
        gr: Union[float, Rate]
    ) -> float:

        """
        Calculates the sale premium.

        :param t: The valuation time.
        :type t: float
        :param gr: The valuation yield.
        :type gr: float, Rate
        :return: The sale premium.
        :rtype: float
        """
        prem = self.clean(t=t, gr=gr) - self.red
        return prem

    def last_coupon_amt(
        self,
        t: float
    ) -> float:

        """
        Calculates the amount of the last coupon paid out prior to time t.

        :param t: The valuation time.
        :type t: float
        :return: The last coupon amount
        :rtype: float
        """
        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        coupon = self.coupons.amounts[ti]
        return coupon

    def next_coupon_amt(
        self,
        t: float
    ) -> float:
        """
        Returns the amount of the next coupon payment after time t.

        :param t: The valuation time.
        :type t: float
        :return: The next coupon amount.
        :rtype: float
        """

        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        coupon = self.coupons.amounts[ti + 1]
        return coupon

    def last_coupon_t(
        self,
        t: float
    ) -> float:
        """
        Returns the time of the last coupon payment prior to time t.

        :param t: The valuation time.
        :type t: float
        :return: The time of the last coupon.
        :rtype: float
        """
        return max([x for x in self.coupons.times if x <= t])

    def next_coupon_t(
        self,
        t: float
    ) -> float:

        """
        Returns the time of the next coupon payment following time t.

        :param t: The valuation time.
        :type t: float
        :return: The time of the next coupon.
        :rtype: float
        """
        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        t1 = self.coupons.times[ti + 1]

        return t1

    def coupon_bound_t(
        self,
        t: float
    ) -> tuple:
        """
        Returns the time boundaries of the last and next coupons around time t.

        :param t: The valuation time.
        :type t: float
        :return: The coupon time boundaries.
        :rtype: tuple
        """
        t0 = self.last_coupon_t(t=t)
        t1 = self.next_coupon_t(t=t)

        return t0, t1

    def coupon_f(
        self,
        t: float
    ) -> float:

        """
        Calculates the fraction of a coupon period between time t and the time of the last coupon payment prior to \
        time t.

        :param t: The valuation time.
        :type t: float
        :return: The fraction of a coupon period.
        :rtype: float
        """

        t0, t1 = self.coupon_bound_t(t=t)

        f = (t - t0) / (t1 - t0)

        return f

    def adj_principal(
        self,
        t: float,
        gr: Union[float, Rate] = None,
        tprac: str = 'theoretical'
    ) -> float:

        """
        Calculates the adjustment to principal in the accrued interest for a coupon.

        :param t: The valuation time.
        :type t: float
        :param gr: The valuation rate, if different from the yield.
        :type gr: float, Rate
        :param tprac: Whether you want to use 'theoretical' or 'practical' values.
        :type tprac: str
        :return: The adjustment to principal in the accrued interest.
        :rtype: float
        """
        t1 = self.next_coupon_t(t=t)
        f = self.coupon_f(t=t)

        if tprac == 'practical':
            pt = self.am_prem(t=t1)
            adj_p = f * pt
        elif tprac == 'theoretical':
            t0 = self.last_coupon_t(t=t)

            if gr is None:
                j = self.j
            else:
                jgr = standardize_acc(gr)
                j = jgr.effective_interval(t1=t0, t2=t1)

            sv = ((1 + j) ** f - 1) / j

            c = self.red
            g = self.g
            n = self.term

            adj_p = sv * c * (g - j) * (1 + j) ** (- (n - t0))

        else:
            raise ValueError("tprac must be 'theoretical' or 'practical'.")

        return adj_p

    def interest_on_accrued(
        self,
        t: float,
        gr: Union[float, Rate] = None,
        tprac: str = 'theoretical'
    ) -> float:

        """
        Calculates the interest on accrued interest for a coupon.

        :param t: The valuation time.
        :type t: float
        :param gr: The valuation rate, if different from the yield.
        :type gr: float, Rate
        :param tprac: Whether you want to use 'theoretical' or 'practical' values.
        :type tprac: str
        :return: The interest on accrued interest.
        :rtype: float
        """

        if tprac == 'practical':
            adj_p = self.adj_principal(t=t, tprac='practical')
            at = self.accrued_interest(t=t, tprac='practical')

        elif tprac == 'theoretical':
            adj_p = self.adj_principal(t=t, gr=gr)
            at = self.accrued_interest(t=t, gr=gr)
        else:
            raise ValueError("tprac must be 'theoretical' or 'practical'.")

        it = at - adj_p

        return it

    def yield_c(
        self,
        times: list = None,
        premiums: list = None
    ) -> list:

        """
        Calculates the yields given a list of call times.

        :param times: A list of call times.
        :type times: list
        :param premiums: A list of call premiums.
        :type premiums: list
        :return: Yield rates for the corresponding call times.
        :rtype: list
        """

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

    def prior_coupons(
            self,
            t: float
    ) -> Payments:

        """
        Gets the coupons prior to the time t.

        :param t: The valuation time.
        :type t: float
        :return: The coupons prior to the time t.
        :rtype: Payments
        """

        t0 = self.last_coupon_t(t=t)
        ti = self.coupons.times.index(t0)
        amounts = self.coupons.amounts[:ti + 1]
        times = self.coupons.times[:ti + 1]

        pmts = Payments(amounts=amounts, times=times)

        return pmts

    def term_floor(self) -> bool:
        """
        Calculates whether the term provided coincides with bond issuance or a coupon payment.

        :return: Whether the term provided coincides with bond issuance or a coupon payment.
        :rtype: bool
        """

        if self.alpha is None and self.cfreq is None and self.fr is None:
            return True
        elif isinstance(self.alpha, (int, float)) or self.alpha is None and self.cfreq is not None:
            if round(self.term % (1 / self.cfreq), 5) == 0:
                return True
            else:
                return False
        else:
            last_alpha_t = self.alpha[-1][1]
            last_cfreq = self.cfreq[-1]
            interval = self.term - last_alpha_t
            if round(interval % (1 / last_cfreq), 5) == 0:
                return True
            else:
                return False


def parse_cgr(
    alpha: Union[float, list] = None,
    cfreq: Union[float, list] = None,
    cgr: Union[Rate, TieredTime] = None
) -> dict:
    """
    Parses the coupon-related arguments provided to the Bond class. It returns a dictionary containing items that
    are used to calculate other features of the bond - alpha, cfreq, and cgr. This is used to improve the flexibility
    of the arguments one may supply to specify coupons.

    This function can for example, extract the rate and frequency components out of the cgr argument and supply them
    to alpha and cfreq, respectively. Or, it can take the alpha and cfreq values to calculate cgr.

    It also handles the case where alpha and cfreq are not constant throughout the term of the bond, in which case
    cgr is calculated to be a TieredTime and vice versa.

    :param alpha: When supplied as a float, a nominal coupon rate. When supplied as a list of tuples of the form [(x1, \
    y_1), (x2, y2), ...], represents a series of coupon rates x supplied during periods beginning at time y. For \
    example alpha=[(.05, 0), (.04, 2)] means a 5% coupon rate the first two years and a 4% rate after that.
    :type alpha: float, list
    :param cfreq: The coupon frequency, or a list of coupon frequencies. When supplied as a list, alpha must also \
    be supplied as a list and each element in cfreq needs to correspond to a tuple in alpha.
    :type cfreq: float, list
    :param cgr: A nominal rate representing the coupon rate and frequency.
    :type cgr: Rate, TieredTime
    :return: A dictionary containing the alpha, cfreq, and cgr values.
    :rtype: dict
    """

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


def spot_rates(bonds: List[Bond] = None, yields=None, alpha=None):
    """
    Solves for the spot rates given a list of bonds.
    :param bonds:
    :type bonds:
    :param yields:
    :type yields:
    :param alpha:
    :type alpha:
    :return:
    :rtype:
    """

    if yields is not None and alpha is not None and bonds is None:
        bonds = [Bond(
            face=100,
            red=100,
            alpha=alpha,
            cfreq=1,
            term=t + 1,
            gr=y
        ) for t, y in zip(range(len(yields)), yields)]

    # find bond with shortest term
    bond_ts = [b.term for b in bonds]
    min_t = min(bond_ts)
    b0_i = bond_ts.index(min_t)
    b0 = bonds[b0_i]

    r_1 = b0.gr.interest_rate
    rates = [r_1]

    bonds.pop(0)

    t0 = 1

    res = {
        t0: r_1
    }

    for b in bonds:
        pmts = b.group_payments()
        del pmts[0]
        times = list(pmts.keys())
        times.sort()
        t_max = times.pop()
        base = b.price
        for r, t in zip(rates, times):
            pv = pmts[t] / ((1 + r) ** t)
            base -= pv
        r_t = (pmts[t_max] / base) ** (1 / t_max) - 1
        r_t = Rate(r_t)
        rates += [r_t]
        res.update({t_max: r_t})

    return res


def forward_rates(term, bonds=None, yields=None, alpha=None):
    """
    Given a list of bonds, or yields and coupon rates, returns the forward rates.

    :param term:
    :type term:
    :param bonds:
    :type bonds:
    :param yields:
    :type yields:
    :param alpha:
    :type alpha:
    :return:
    :rtype:
    """
    sr = spot_rates(bonds=bonds, yields=yields, alpha=alpha)

    res = {}
    for t in range(len(sr) + 1 - term):
        if t == 0:
            f = sr[term]
        else:
            f_factor = (1 + sr[t + term]) ** (t + term) / (1 + sr[t]) ** t
            f = Rate(f_factor ** (1 / term) - 1)
        res.update({(t, t + term): f})

    return res
