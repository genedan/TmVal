from collections import namedtuple
import decimal
import numpy as np
from typing import Callable, Union

from tmval.value import Payments, Rate
from tmval.growth import Accumulation, TieredTime, standardize_acc
from math import ceil, floor


class Annuity(Payments):

    def __init__(
        self,
        gr: Union[float, Rate, Accumulation, Callable],
        period: float = None,
        term: float = None,
        n: float = None,
        gprog: float = 0.0,
        aprog: float = 0.0,
        amount: Union[float, int, list] = 1.0,
        times: list = None,
        reinv: Union[float, Rate, Accumulation, Callable] = None,
        deferral: float = None,
        imd: str = 'immediate',
        loan: float = None,
        drb: str = None
    ):
        self.term = term
        self.amount = amount
        self.period = period
        self.imd = imd
        self.gprog = gprog
        self.aprog = aprog
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
            else:
                r = self.get_r_pmt(gr)
                r = ceil(r) if drb == 'drop' else floor(r)
                self.term = r * self.period

        # perpetuity
        if self.term == np.inf:

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
            elif self.get_r_pmt(gr) > self.term:
                f = self.get_r_pmt(gr) - self.term
                self.n_payments -= 1
            else:
                f = 0

            if isinstance(amount, (int, float)) or (isinstance(amount, list) and len(amount)) == 1:
                amounts = [self.amount * (1 + self.gprog) ** x + self.aprog * x for x in range(self.n_payments)]
                times = [period * (x + imd_ind) for x in range(self.n_payments)]
            else:
                amounts = amount
                times = times
                times.sort()
                intervals = list(np.diff(times))
                intervals = [round(x, 7) for x in intervals]
                if intervals[1:] != intervals[:-1]:
                    raise Exception("Non-level intervals detected, use Payments class instead.")
                else:
                    self.period = intervals[0]

                if min(times) == 0:
                    self.imd = 'due'
                    self.term = max(times) + self.period
                else:
                    self.imd = 'immediate'
                    self.term = max(times)

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

    def pv(self):

        # if interest rate is level, can use formulas to save time
        if isinstance(self.gr, Accumulation) and self.gr.is_level and (self.is_level_pmt or self.gprog != 0):
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

                else:
                    pv = self.n_payments * self.amount * (1 + i) ** (-1)

        # annuity with arithmetically increasing payments
        elif self.aprog != 0:
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

        if self.deferral is not None:
            pv = pv * self.gr.discount_func(self.deferral)

        return pv

    def sv(self):

        if isinstance(self.gr, Accumulation) and self.gr.is_level and self.is_level_pmt and self.reinv is None:
            sv = self.amount * \
                 ((1 + self.gr.interest_rate) ** self.term - 1) / \
                 (self.gr.val(self.period) - 1)

        elif self.aprog != 0:

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

            sv = self.eq_val(t=self.term)
            skip_due = True

        if self.imd == 'due' and 'skip_due' not in locals():
            sv = sv * self.gr.val(self.period)

        return sv

    def fv(self, t):
        sv = self.sv()
        pv = self.gr.discount_func(fv=sv, t=self.term)
        fv = pv * self.gr.val(t)

        return fv

    def get_r_pmt(self, gr):
        i = standardize_acc(gr).val(self.period) - 1
        r = - np.log(1 - i * self.loan / self.amount) / np.log(1 + i)
        return r

    def get_drop(self, gr):
        r = self.get_r_pmt(gr)
        n = floor(r)
        f = r - n
        i = standardize_acc(gr).val(self.period) - 1
        drop = (self.amount * ((1 + i) ** f - 1) / i) * (1 + i) ** (1 - f)
        return drop

    def get_balloon(self, gr):
        r = self.get_r_pmt(gr)
        n = floor(r)
        f = r - n
        q = self.amount
        i = standardize_acc(gr).val(self.period) - 1

        balloon = q + q * (((1 + i) ** f - 1) / i) * (1 + i) ** (-f)
        return balloon


def get_loan_amt(
        down_pmt: float,
        loan_pmt: float,
        period: float,
        term: float,
        gr: Rate
) -> float:

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
        gr: Rate,
        imd: str = 'immediate',
        cents=False
):

    ann = Annuity(
        period=period,
        term=term,
        gr=gr,
        imd=imd
    )

    pmt = loan_amt / ann.pv()

    if cents:

        acc = Accumulation(gr=gr)

        pmt_round = round(pmt, 2)

        pv = Annuity(
            amount=pmt_round,
            period=period,
            term=term,
            gr=gr,
            imd=imd
        ).pv()

        if loan_amt == round(pv, 2):

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
                gr=gr,
                imd=imd
            ).pv() - loan_amt

            last_pmt = pmt_round2 - round(diff * acc.val(t=term), 2)

            Installments = namedtuple(
                'installments',
                'amount last'
            )

            return Installments(pmt_round2, last_pmt)
    else:
        return pmt


def get_savings_pmt(
        fv: float,
        period: float,
        term: float,
        gr: Rate,
        cents=False
):

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
):
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
    gr: Union[float, Rate, Accumulation],
    t: float,
    r: float = None,
    missed: list = None
) -> float:
    """
    Outstanding loan balance - prospective method.

    :param q:
    :type q:
    :param period:
    :type period:
    :param term:
    :type term:
    :param gr:
    :type gr:
    :param t:
    :type t:
    :param r:
    :type r:
    :param missed:
    :type missed:
    :return:
    :rtype:
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
