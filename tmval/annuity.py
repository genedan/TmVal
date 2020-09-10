"""
Contains the Annuity class, TmVal's main class for all kinds of annuities. The user can choose what type of
annuities to represent by specifying the arguments at initialization.
"""
from collections import namedtuple
import decimal
import numpy as np
from scipy.integrate import quad

from typing import (
    Callable,
    Union
)

from tmval.value import (
    Payments,
    Rate
)

from tmval.growth import (
    Accumulation,
    standardize_acc,
    TieredTime
)

from math import (
    ceil,
    floor
)


class Annuity(Payments):
    """
    Annuity is TmVal's general class for representing all kinds of annuities. Among the supported types are:

    #. Annuity-immediate
    #. Annuity-due
    #. Perpetuity-immediate
    #. Perpetuity-due
    #. Deferred annuity
    #. Annuity with arithmetic progression
    #. Annuity with geometric progression
    #. Perpetuity with arithmetic progression
    #. Perpetuity with geometric progression
    #. Annuity with reinvested proceeds at a different growth rate

    By tweaking the arguments, you can represent more types of annuities that you might find in actuarial literature.

    The Annuity class comes with methods to solve for the present value, accumulated value, and equation of value at
    periods other than 0 or end-of-term. You do not have to provide overlapping time-related arguments. For example,
    if you provide the period and number of payments, the term can be inferred. Likewise, if you provide the term
    and period, the number of payments can be inferred.

    :param gr: A growth rate object.
    :type gr: Accumulation, Callable, float, Rate.
    :param amount: A payment amount, defaults to 1. Can also provide a list for non-level payments.
    :type amount: float, int, list
    :param period: The payment period, defaults to 1.
    :type period: float
    :param term: The annuity term.
    :type term: float
    :param n: The number of payments.
    :type n: float
    :param aprog: Arithmetic progression of payments defaults to 0.
    :type aprog: float
    :param gprog: Geometric progression of payments, defaults to 0.
    :type gprog: float
    :param times: Payment times, usually left blank but can be provided for nontraditional annuities, defaults to None
    :type times: list
    :param reinv: A reinvestment rate, if proceeds are reinvested at a rate other than provided to gr.
    :type reinv: Accumulation, Callable, float, Rate
    :param deferral: A time period in years to indicate a deferred annuity.
    :type deferral: float
    :param imd: Whether the annuity is 'immediate' or 'due', defaults to 'immediate'.
    :type imd: str
    :param loan: An amount that allows you to represent an annuity as a loan from which the payments can be inferred, \
    defaults to None.
    :type loan: float, optional
    :param drb: Whether the final loan payment is a 'drop' or 'balloon' payment.
    :type drb: str, optional
    """

    def __init__(
        self,
        gr: Union[
            Accumulation,
            Callable,
            float,
            Rate
        ],

        amount: Union[
            float,
            int,
            list,
            Callable
        ] = 1.0,

        period: float = 1,
        term: float = None,
        n: float = None,
        gprog: float = 0.0,
        aprog: Union[float, int, tuple] = 0.0,
        times: list = None,

        reinv: [
            Accumulation,
            Callable,
            float,
            Rate
        ] = None,

        deferral: float = 0.0,
        imd: str = 'immediate',
        loan: float = None,
        drb: str = None
    ):
        self.term = term
        self.amount = amount
        self.period = period
        self.imd = imd
        self.gprog = gprog

        if isinstance(aprog, (float, int)):
            self.aprog = aprog
            self.mprog = 1
        elif isinstance(aprog, tuple):
            self.aprog = aprog[0]
            self.mprog = aprog[1] * period
        else:
            raise ValueError("Invalid value provided to aprog.")

        imd_ind = 1 if imd == 'immediate' else 0
        self.is_level_pmt = None
        self.reinv = reinv
        self.deferral = deferral
        self.loan = loan
        self.n_payments = n
        self.drb_pmt = None

        if term is None:
            if self.n_payments:
                self.term = self.n_payments * self.period
                if loan is None:
                    r = self.n_payments
                else:
                    r = max(self.get_r_pmt(gr), self.n_payments)
            elif times:
                self.term = max(times)
                r = len(times)
                self.n_payments = len(times)
            elif period == 0:
                dt = standardize_acc(gr).interest_rate.convert_rate(pattern="Force of Interest")
                r = np.Inf
                self.term = np.log(1 - loan / amount * dt) / (- dt)
            else:
                r = self.get_r_pmt(gr)
                r = ceil(r) if drb == 'drop' else floor(r)
                self.term = r * self.period
        else:
            if self.period == 0:
                r = np.Inf
            else:
                r = self.term / self.period
        # perpetuity
        if self.term == np.inf or self.n_payments == np.Inf:

            def perp_series(t):
                start = amount
                factor = 1 + gprog
                curr = 0
                while curr < t:
                    yield start * factor ** curr
                    curr += 1

            def perp_times(t):
                curr = 0 + 1 if imd == 'immediate' else 0
                while curr < t:
                    yield curr + 1

            amounts = perp_series
            times = perp_times
            self._ann_perp = 'perpetuity'
            self.n_payments = np.inf

            if gprog == 0:
                self.is_level_pmt = True
            else:
                self.is_level_pmt = False
        # continuously paying
        elif self.period == 0:
            amounts = []
            times = []
            self.n_payments = np.inf
            self._ann_perp = 'annuity'

            if isinstance(amount, Callable):
                if round(amount(0) * self.term, 3) == round(quad(amount, 0, self.term)[0], 3):
                    Warning("Level continuously paying annuity detected. It's better to supply a constant to the "
                            "amount argument to speed up computation.")
                    self.is_level_pmt = True
                else:
                    self.is_level_pmt = False
            else:
                self.is_level_pmt = True
        else:
            if self.n_payments is None and term is not None:
                r_payments = self.term / period
                n_payments = floor(r_payments)
                self.n_payments = n_payments
                f = 0
            elif self.n_payments is None and term is None:
                r_payments = self.get_r_pmt(gr)
                n_payments = floor(r_payments)
                f = r_payments - n_payments
                self.n_payments = n_payments

            elif r > self.n_payments:
                self.n_payments -= 1
                f = r - self.n_payments
            else:
                f = 0

            if isinstance(amount, (int, float)) or (isinstance(amount, list) and len(amount)) == 1:
                amounts = [self.amount * (1 + self.gprog) ** x +
                           self.aprog * floor(x * self.mprog) for x in range(self.n_payments)]
                times = [period * (x + imd_ind) for x in range(self.n_payments)]
            else:
                amounts = amount
                times = times
                times.sort()
                intervals = list(np.diff(times))
                intervals = [round(x, 7) for x in intervals]
                if intervals[1:] != intervals[:-1]:
                    raise Exception("Non-level intervals detected, use payments class instead.")
                else:
                    self.period = intervals[0]

                if min(times) == 0:
                    self.imd = 'due'
                    self.term = max(times) + self.period
                else:
                    self.imd = 'immediate'
                    self.term = max(times)

            if deferral > 0:
                times = [x + deferral for x in times]

            if 0 < f < 1:

                if drb == "balloon":
                    self.drb_pmt = self.get_balloon(gr)
                    amounts[-1] = self.drb_pmt
                elif drb == "drop":
                    self.drb_pmt = self.get_drop(gr)
                    amounts.append(self.drb_pmt)
                    times.append(self.term)
                    self.n_payments += 1

                self.is_level_pmt = False

            elif 1 <= f:
                self.drb_pmt = self.amount + olb_r(
                    loan=self.loan,
                    q=self.amount,
                    period=self.period,
                    gr=gr,
                    t=self.term
                )

                amounts.append(self.drb_pmt)
                times.append(self.term)
                self.is_level_pmt = False

            else:
                pass

            if (isinstance(amount, (int, float)) or (isinstance(amount, list) and
                len(amount))) == 1 and \
                    gprog == 0 and \
                    aprog == 0 and self.drb_pmt is None:

                self.is_level_pmt = True

            elif gprog != 0 or aprog != 0:

                self.is_level_pmt = False

            elif amounts[1:] == amounts[:-1]:

                self.is_level_pmt = True

            else:

                self.is_level_pmt = False

            self._ann_perp = 'annuity'

        Payments.__init__(
            self,
            amounts=amounts,
            times=times,
            gr=gr
        )

        self.pattern = self._ann_perp + '-' + imd

        if imd not in ['immediate', 'due']:
            raise ValueError('imd can either be immediate or due.')

    def pv(self) -> float:
        """
        Calculates the present value of the annuity. The formula used to calculate the present value will \
        depend on the type of annuity that gets inferred from the arguments provided to the parent class. Several \
        classes of annuities come with shortcut formulas which will be used in favor of just the standard npv or \
        equation of value formulas to improve computation speed:

        #. Annuity-immediate: :math:`\\ax{\\angln i}`
        #. Annuity-due: :math:`\\ax**{\\angln i}`
        #. Perpetuity-immediate: :math:`\\ax{\\angl{\\infty} i}`
        #. Perpetuity-due: :math:`\\ax**{\\angl{\\infty} i}`
        #. Arithmetically increasing annuity-immediate: :math:`(I_{P, Q} a)_{\\angln i}`
        #. Arithmetically increasing annuity-due: :math:`(I_{P, Q} \\ax**{})_{\\angln i}`
        #. Arithmetically increasing perpetuity-immediate: :math:`(I_{P, Q} a)_{\\angl{\\infty} i}`
        #. Arithmetically increasing perpetuity-due: :math:`(I_{P, Q} a)_{\\angl{\\infty} i}`
        #. Geometrically increasing annuity-immediate
        #. Geometrically increasing annuity-due
        #. Geometrically increasing perpetuity-immediate
        #. Geometrically increasing perpetuity-due

        :return: The present value of the annuity.
        :rtype: float
        """

        if isinstance(self.amount, Callable):
            def f(x):
                return self.amount(x) * self.gr.discount_func(x)
            pv = quad(f, 0, self.term)[0]

        # if interest rate is level, can use formulas to save time
        elif isinstance(self.gr, Accumulation) and self.gr.is_level and (self.is_level_pmt or self.gprog != 0):
            i = self.gr.val(self.period) - 1
            g = self.gprog

            if self._ann_perp == 'perpetuity':
                # perpetuity with arithmetically increasing payments
                if self.aprog != 0:
                    pv = self.amount / i + self.aprog / (i ** 2)

                else:

                    pv = self.amount / (self.gr.val(self.period) - 1)

            else:

                if round(i - g, 5) != 0:

                    pv = self.amount * ((1 - ((1 + g) / (1 + i)) ** self.n_payments) / (i - g))

                # Continuously paying annuity
                elif self.period == 0:
                    pv = self.abar_angln()

                else:
                    pv = self.n_payments * self.amount * (1 + i) ** (-1)

        # annuity with arithmetically increasing payments
        elif self.aprog != 0 and self.mprog == 0:

            if self.period == 0:
                pv = self.ibar_abar_angln()
            else:
                i = self.gr.val(self.period) - 1
                n = self.n_payments
                q = self.aprog
                a_n = (1 - (1 + i) ** - n) / i
                p = self.amount

                pv = p * a_n + q / i * (a_n - n * (1 + i) ** - n)

        # perpetuity with geometric payments and tiered growth
        elif self._ann_perp == 'perpetuity' and isinstance(self.gr.gr, TieredTime):

            intervals = list(np.diff(self.gr.gr.tiers))
            rates_b = self.gr.gr.rates[:-1]
            r_f = self.gr.gr.rates[-1]
            t_f = self.gr.gr.tiers[-1]

            pv = 0
            disc = 1
            for t, r in zip(intervals, rates_b):
                n = t / self.period
                i = (1 + r) ** self.period - 1
                ratio = (1 + self.gprog) / (1 + i)
                pv_t = self.amount * ((1 + i) ** -1) * ((1 - ratio ** n) / (1 - ratio))
                pv += pv_t
                disc *= (1 + r) ** (-t)

            pv_f = disc * (self.amount * (1 + self.gprog) ** t_f) * ((1 + r_f) ** -1) * (
                        1 / (1 - ((1 + self.gprog) / (1 + r_f))))

            pv += pv_f

        else:
            # otherwise, use npv function
            pv = self.npv()
            skip_due = True

        if self.imd == 'due' and 'skip_due' not in locals():
            i = self.gr.val(self.period) - 1
            pv = pv * (1 + i)

        if self.deferral > 0:
            pv = pv * self.gr.discount_func(self.deferral)

        return pv

    def sv(self):
        """
        Calculates the accumulated value of the annuity. The formula used to calculate the accumulated value will \
        depend on the type of annuity that gets inferred from the arguments provided to the parent class. Several \
        classes of annuities come with shortcut formulas which will be used in favor of the equation of value formula \
        to improve computation speed:

        #. Annuity-immediate: :math:`\\sx{\\angln i}`
        #. Annuity-due: :math:`\\sx**{\\angln i}`
        #. Perpetuity-immediate: :math:`\\sx{\\angl{\\infty} i}`
        #. Perpetuity-due: :math:`\\sx**{\\angl{\\infty} i}`
        #. Arithmetically increasing annuity-immediate: :math:`(I_{P, Q} s)_{\\angln i}`
        #. Arithmetically increasing annuity-due: :math:`(I_{P, Q} \\sx**{})_{\\angln i}`
        #. Arithmetically increasing perpetuity-immediate: :math:`(I_{P, Q} s)_{\\angl{\\infty} i}`
        #. Arithmetically increasing perpetuity-due: :math:`(I_{P, Q} s)_{\\angl{\\infty} i}`
        #. Geometrically increasing annuity-immediate
        #. Geometrically increasing annuity-due
        #. Geometrically increasing perpetuity-immediate
        #. Geometrically increasing perpetuity-due

        :return: The accumulated value of the annuity.
        :rtype: float
        """

        # continuously paying annuity
        if isinstance(self.amount, Callable):
            sv = self.pv() * self.gr.val(self.term)

        elif isinstance(self.gr, Accumulation) and self.gr.is_level and self.is_level_pmt and self.reinv is None:

            if self.period == 0:
                sv = self.sbar_angln()

            else:
                sv = self.amount * \
                     ((1 + self.gr.interest_rate) ** self.term - 1) / \
                     (self.gr.val(self.period) - 1)

        elif self.aprog != 0 and self.mprog == 0:

            if self.period == 0:
                sv = self.ibar_sbar_angln()
            else:
                i = self.gr.val(self.period) - 1
                n = self.n_payments
                q = self.aprog
                p = self.amount
                s_n = ((1 + i) ** n - 1) / i

                sv = p * s_n + q / i * (s_n - n)

        # reinvestment
        elif self.reinv is not None:

            i = self.gr.val(self.period) - 1
            n = self.n_payments
            rn = n - 1

            r = standardize_acc(self.reinv)
            r = r.val(self.period) - 1
            dr = r / (1 + r)
            aprog = self.amount * i

            i_s = aprog * (((((1 + r) ** rn - 1) / dr) - rn) / r)

            k = self.amount * n

            sv = i_s + k

        else:

            sv = self.eq_val(t=self.term + self.deferral)

            return sv

        if self.deferral != 0:

            sv = sv * self.gr.val(self.deferral)

        if self.imd == 'due':
            sv = sv * self.gr.val(self.period)

        return sv

    def sbar_angln(self):
        delta = self.get_delta()
        return (np.exp(delta * self.term) - 1) / delta

    def abar_angln(self):
        delta = self.get_delta()
        return self.amount * (1 - np.exp(-delta * self.term)) / delta

    def ibar_abar_angln(self):
        delta = self.get_delta()
        abar = self.abar_angln()
        return (abar - self.term * np.exp(-delta * self.term)) / delta

    def ibar_sbar_angln(self):
        delta = self.get_delta()
        sbar = self.sbar_angln()
        return (sbar - self.term) / delta

    def get_r_pmt(
        self,
        gr: Union[
            Accumulation,
            Callable,
            float,
            Rate
        ]
    ) -> float:

        """
        When inferring the number of payment periods, returns the number of payment periods as if fractional periods
        were allowed. This fractional value helps calculate the drop or balloon payments, if needed.

        :param gr: A growth rate object.
        :type gr: Accumulation, Callable, float, or Rate
        :return: The number of payment periods.
        :rtype: float
        """

        i = standardize_acc(gr).val(self.period) - 1
        r = - np.log(1 - i * self.loan / self.amount) / np.log(1 + i)
        return r

    def get_drop(
        self,
        gr
    ) -> float:
        """
        If the number of payment periods does not settle to an integral number, calculates the drop payment.

        :param gr: A growth rate object.
        :type gr: Accumulation, Callable, float, or Rate
        :return: The drop payment.
        :rtype: float
        """
        r = self.get_r_pmt(gr)
        n = floor(r)
        f = r - n
        i = standardize_acc(gr).val(self.period) - 1
        drop = (self.amount * ((1 + i) ** f - 1) / i) * (1 + i) ** (1 - f)
        return drop

    def get_balloon(
        self,
        gr
    ) -> float:
        """
        If the number of payment periods does not settle to an integral number, calculates the balloon payment.

        :param gr: A growth rate object.
        :type gr: Accumulation, Callable, float, or Rate
        :return: The balloon payment.
        :rtype: float
        """
        r = self.get_r_pmt(gr)
        n = floor(r)
        f = r - n
        q = self.amount
        i = standardize_acc(gr).val(self.period) - 1

        balloon = q + q * (((1 + i) ** f - 1) / i) * (1 + i) ** (-f)
        return balloon

    def get_delta(self):
        return self.gr.interest_rate.convert_rate(pattern="Force of Interest")


def get_loan_amt(
    down_pmt: float,
    loan_pmt: float,
    period: float,
    term: float,
    gr: Rate
) -> float:
    """
    Returns a loan amount, given a set of characteristics that defines an annuity.

    :param down_pmt: A down payment amount, reduces the loan amount.
    :type down_pmt: float
    :param loan_pmt: The periodic loan payment amount.
    :type loan_pmt: float
    :param period: The payment period, as a fraction of a year.
    :type period: float
    :param term: The term of the loan, in years.
    :type term: float
    :param gr: A growth rate object
    :type gr: Rate
    :return: A loan amount whose present value is equal to the annuity generated from the other arguments.
    :rtype: float
    """

    ann = Annuity(
        period=period,
        term=term,
        amount=loan_pmt,
        gr=gr
    )

    loan_amt = ann.pv() + down_pmt

    return loan_amt


def get_loan_pmt(
    loan_amt: float,
    period: float,
    term: float,
    gr: Union[float, Rate, TieredTime],
    imd: str = 'immediate',
    gprog: float = 0.0,
    aprog: float = 0.0,
    cents=False
) -> dict:
    """
    Returns the loan payment schedule, given a loan amount, payment period, term, growth rate, and geometric or
    arithmetic progression of payments. If cents is set to True, uses the Daniel and Vaaler rounding algorithm
    to round each payment to cents, modifying the final payment such that there is no over/under payment of the
    loan due to rounding issues.

    :param loan_amt: The loan amount to be repaid.
    :type loan_amt: float
    :param period: The payment frequency, per fraction of a year.
    :type period: float
    :param term: The term of the loan, in years.
    :type term: float
    :param gr: Some kind of growth rate object specifying the interest rate
    :type gr: Accumulation, Callable, float, Rate
    :param imd: 'immediate' or 'due'. Whether the payments occur at the end or beginning of each period, defaults to \
    'immediate'.
    :type imd: str
    :param gprog: geometric progression, payments grow at a % of the previous payment per period, defaults to 0.
    :type gprog: float
    :param aprog: arithmetic progression, payments grow by a constant amount each period, defaults to 0.
    :type aprog: float
    :param cents: Whether you want payments rounded to cents.
    :type cents: bool
    :return: a dictionary of payment amounts along with the times of the payments
    :rtype: dict
    """
    ann = Annuity(
        period=period,
        term=term,
        gr=gr,
        gprog=gprog,
        imd=imd
    )

    if aprog >= 0:
        i = ann.gr.effective_interval(t2=ann.period)
        n = ann.n_payments
        v = ann.gr.discount_func(period)
        pmt = (loan_amt - (aprog / i) * (ann.pv() - n * v ** n)) / (ann.pv())
        iann = Annuity(
            amount=pmt,
            period=period,
            term=term,
            gr=gr,
            aprog=aprog,
            imd=imd
        )
        pmts = iann.amounts
    else:
        pmt = loan_amt / ann.pv()
        pmts = [pmt * x for x in ann.amounts]

    times = ann.times

    pmts_dict = {
        'times': times,
        'amounts': pmts
    }

    if cents:

        acc = Accumulation(gr=gr)

        pmt_round = round(pmt, 2)

        pv = Annuity(
            amount=pmt_round,
            period=period,
            term=term,
            gr=gr,
            gprog=gprog,
            imd=imd
        ).pv()

        if loan_amt == round(pv, 2):

            return pmts_dict

        else:

            cent = decimal.Decimal('0.01')

            pmt_round2 = float(
                decimal.Decimal(pmt).quantize(
                    cent,
                    rounding=decimal.ROUND_UP
                )
            )

            d_ann = Annuity(
                amount=pmt_round2,
                period=period,
                term=term,
                gr=gr,
                gprog=gprog,
                aprog=aprog,
                imd=imd
            )

            diff = d_ann.pv() - loan_amt

            last_pmt = round(d_ann.amounts[-1] - round(diff * acc.val(t=term), 2), 2)

            pmts = [round(x, 2) for x in d_ann.amounts[:-1]]
            pmts.append(last_pmt)

            pmts_dict = {
                'times': times,
                'amounts': pmts
            }

    return pmts_dict


def get_savings_pmt(
    fv: float,
    period: float,
    term: float,
    gr: Union[float, Rate],
    cents=False
) -> Union[float, tuple]:
    """
    Returns the savings payments, made at regular installments specified by period, that grow to the desired
    future value. When cents is set to True, rounds the payments to the next cent, except for the last payment
    which is adjusted so that the desired future value is reached without over/under payment.

    :param fv: The desired future value.
    :type fv: float
    :param period: The payment period, as a fraction of a year.
    :type period: float
    :param term: The amount of time required to reach the desired future value, in years.
    :type term: float
    :param gr: A growth rate object.
    :type gr: Rate
    :param cents: Whether you want the payments rounded up to the next cent, except the final one.
    :type cents: bool
    :return: A payment amount.
    :rtype: float, or tuple if cents is True
    """

    ann = Annuity(
        period=period,
        term=term,
        gr=gr
    )

    pmt = fv / ann.sv()

    if cents:
        pmt_round = round(pmt, 2)

        fv2 = Annuity(
            amount=pmt_round,
            period=period,
            term=term,
            gr=gr
        ).sv()

        if fv == round(fv2, 2):

            return pmt

        else:
            cent = decimal.Decimal('0.01')

            pmt_round2 = float(
                decimal.Decimal(pmt).quantize(
                    cent,
                    rounding=decimal.ROUND_UP
                )
            )

            diff = Annuity(
                amount=pmt_round2,
                period=period,
                term=term,
                gr=gr
            ).sv() - fv

            last_pmt = round(pmt_round2 - round(diff, 2), 2)

            Installments = namedtuple('installments', 'amount last')

            return Installments(pmt_round2, last_pmt)
    else:
        return pmt


def get_number_of_pmts(
    pmt: float,
    fv: float,
    period: float,
    gr: Rate
) -> int:
    """
    Given payment information represented by an annuity, calculates the number of payments required to reach a
    desired future value.

    :param pmt: The payment amount.
    :type pmt: float
    :param fv: The desired future value.
    :type fv: float
    :param period: The payment period, as a fraction of a year.
    :type period: float
    :param gr: A growth rate object.
    :type gr: Rate
    :return: The number of payments.
    :rtype: int
    """
    i = gr.convert_rate(
        'Effective Interest',
        interval=period
    )

    n = np.log(fv / pmt * i + 1) / np.log(1 + i)

    n = ceil(n)

    return n


def olb_r(
    loan: float,
    q: float,
    period: float,
    gr: Union[Accumulation, float, Rate],
    t
) -> float:
    """
    Calculates the outstanding loan balance using the retrospective method.

    :param loan: The loan amount.
    :type loan: float
    :param q: The payment amount.
    :type q: float
    :param period: The payment period.
    :type period: float
    :param gr: A growth rate object.
    :type gr: Accumulation, float, or Rate
    :param t: The valuation time.
    :type t: float
    :return: The outstanding loan balance.
    :rtype: float
    """

    ann = Annuity(
        period=period,
        term=t,
        gr=gr,
        amount=q
    )

    acc = Accumulation(gr=gr)
    olb = loan * acc.val(t) - ann.sv()

    return max(olb, 0)


def olb_p(
    q: float,
    period: float,
    term: float,
    gr: Union[Accumulation, float, Rate],
    t: float,
    r: float = None,
    missed: list = None
) -> float:
    """
    Calculates the outstanding loan balance using the retrospective method.

    :param q: The payment amount.
    :type q: float
    :param period: The payment period.
    :type period: float
    :param term: The loan term, in years.
    :type term: float
    :param gr: A growth rate object.
    :type gr: Accumulation, float, or Rate.
    :param t: The valuation time, in years.
    :type t: float
    :param r: The final payment amount, if different from the others, defaults to None.
    :type r: float, optional
    :param missed: A list of missed payments, for example, 4th and 5th payments would be [4, 5].
    :type missed: list
    :return: The outstanding loan balance.
    :rtype: float
    """
    acc = Accumulation(gr=gr)

    if r is not None:
        ann = Annuity(
            period=period,
            term=term - t - period,
            gr=gr,
            amount=q
        )

        r_pv = r * acc.discount_func(term - t)

        olb = ann.pv() + r_pv

    else:
        ann = Annuity(
            period=period,
            term=term - t,
            gr=gr,
            amount=q
        )

        olb = ann.pv()

    if missed:

        for p in missed:
            olb += q * acc.val(t - p)

    return olb


def get_perpetuity_gr(
    amount: float,
    pv: float,
    period: float,
    imd: str = 'immediate'
) -> Rate:

    """
    Given a payment amount, payment frequency, and present value, returns a compound annual effective interest rate.

    :param amount: The payment amount.
    :type amount: float
    :param pv: The present value.
    :type pv: float
    :param period: The payment period, as a fraction of a year.
    :type period: float
    :param imd: Whether the perpetuity is 'immediate' or 'due'.
    :type imd: str
    :return: The annual effective interest rate.
    :rtype: Rate
    """
    i = amount / pv

    if imd == 'immediate':
        gr = Rate(i, pattern="Effective Interest", interval=period)
    elif imd == 'due':
        gr = Rate(i, pattern="Effective Discount", interval=period)
    else:
        raise ValueError("Invalid value provided to imd argument, please use 'immediate' or 'due'.")

    gr = gr.convert_rate(pattern="Effective Interest", interval=1)
    return gr


def get_perpetuity_pmt(
    gr: Rate,
    pv: float,
    period: float,
    imd: str = 'immediate'
) -> float:
    """
    Given an interest rate, present value, and payment period, returns the payment amount of a perpetuity.

    :param gr: A growth rate object.
    :type gr: Rate
    :param pv: The present value.
    :type pv: float
    :param period: The payment period.
    :type period: float
    :param imd: Whether the perpetuity is 'immediate' or 'due'.
    :type imd: str
    :return: The payment amount.
    :rtype: float
    """

    if imd == 'immediate':
        i = gr.convert_rate(
            pattern="Effective Interest",
            interval=period
        )
    elif imd == 'due':
        i = gr.convert_rate(
            pattern="Effective Discount",
            interval=period
        )
    else:
        raise ValueError("Invalid value provided to imd argument, please use 'immediate' or 'due'.")

    amount = i * pv

    return amount


def n_solver(
        gr,
        amount,
        sv=None,
        period=None,
):
    if sv:
        acc = standardize_acc(gr)
        i = acc.effective_rate(period)

        n = np.log(1 + sv / amount * i) / np.log(1 + i)
    else:
        n = None

    return n
