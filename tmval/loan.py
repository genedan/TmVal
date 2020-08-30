from math import ceil, floor
from typing import Union

from tmval.annuity import Annuity, olb_r, olb_p, get_loan_pmt
from tmval.growth import Amount, TieredTime, standardize_acc
from tmval.value import Payments
from tmval.rate import Rate


class Loan:
    def __init__(
        self,
        gr: Union[Rate, float, TieredTime],
        pmt: float = None,
        period: float = None,
        term: float = None,
        amt: float = None,
        cents: bool = False,
        sfr: Union[float, Rate, TieredTime] = None,
        sfd: float = None
    ):
        self.pmt = pmt
        self.period = period
        self.term = term
        self.gr = standardize_acc(gr)
        self.cents = cents
        self.sfr = sfr
        self.sfd = sfd

        if amt is None:

            ann = Annuity(
                period=self.period,
                term=self.term,
                gr=self.gr,
                amount=self.pmt
            )

            self.amt = ann.pv()
        else:
            self.amt = amt

        if pmt is None:
            self.pmt_sched = self.get_payments()
            self.pmt = self.pmt_sched.amounts[0]

    def get_payments(self):

        if self.sfr:
            n_payments = ceil(self.term / self.period)
            amt = self.gr.effective_rate(self.period) * self.amt
            pmts = Payments(amounts=[amt] * n_payments, times=[(x + 1) * self.period for x in range(n_payments)])

        else:

            pmts_dict = get_loan_pmt(
                loan_amt=self.amt,
                period=self.period,
                term=self.term,
                gr=self.gr.gr,
                cents=self.cents
            )

            pmts = Payments(
                amounts=pmts_dict['amounts'],
                times=pmts_dict['times']
            )

        return pmts

    def olb_r(self, t, payments: Payments = None) -> float:

        if payments:
            payments.set_accumulation(gr=self.gr)
            loan_value = self.principal_val(t)
            payments_value = payments.eq_val(t)
            olb = loan_value - payments_value

        else:
            olb = olb_r(
                loan=self.amt,
                q=self.pmt,
                period=self.period,
                gr=self.gr.gr,
                t=t
            )

        return olb

    def olb_p(
            self,
            t: float,
            r: float = None,
            missed: list = None
    ):

        olb = olb_p(
            q=self.pmt,
            period=self.period,
            term=self.term,
            gr=self.gr.gr,
            t=t,
            r=r,
            missed=missed
        )

        return olb

    def amortize_payments(self, payments: Payments) -> dict:
        amt = Amount(gr=self.gr.gr, k=self.amt)

        res = {
            'time': [],
            'payment_amt': [],
            'interest_paid': [],
            'principal_paid': [],
            'remaining_balance': []
        }

        # initial row
        res['time'] += [0]
        res['payment_amt'] += [None]
        res['interest_paid'] += [None]
        res['principal_paid'] += [None]
        res['remaining_balance'] += [self.amt]

        principal = self.amt
        t1 = 0
        for time, amount in zip(payments.times, payments.amounts):
            interest_due = principal * amt.effective_interval(t1=t1, t2=time)
            t1 = time
            interest_paid = min(interest_due, amount)

            if amount > interest_due:
                principal_paid = amount - interest_paid
            else:
                principal_paid = 0

            principal -= principal_paid
            res['time'] += [time]
            res['payment_amt'] += [amount]
            res['interest_paid'] += [interest_due]
            res['principal_paid'] += [principal_paid]
            res['remaining_balance'] += [principal]

        return res

    def principal_paid(self,  t2: float, t1: float = 0):

        if self.sfr:
            return 0
        else:
            return self.olb_r(t1) - self.olb_r(t2)

    def total_payments(self, t2: float, t1: float = 0):
        return round((t2 - t1) / self.period, 1) * self.pmt

    def interest_paid(self, t2: float, t1: float = 0, frac: bool = False):
        interest_paid = self.total_payments(t1=t1, t2=t2) - self.principal_paid(t1=t1, t2=t2)

        if frac:
            total_interest = self.interest_paid(t2=self.term)
            res = interest_paid / total_interest
            return res
        else:
            return interest_paid

    def principal_val(self, t):
        amt = Amount(gr=self.gr.gr, k=self.amt)
        return amt.val(t)

    def amortization(self):

        res = self.amortize_payments(payments=self.pmt_sched)

        if self.cents:
            for k, v in res.items():
                res[k] = [round(x, 2) if isinstance(x, float) else x for x in v]

        return res

    def sf_final(self):

        if self.sfr is None:
            raise Exception("sf_final only applicable to sinking fund loans.")

        sv = Annuity(
            amount=self.sfd,
            gr=self.sfr,
            period=self.period,
            term=self.term - self.period
        ).eq_val(self.term)

        final_pmt = self.amt - sv

        return final_pmt
