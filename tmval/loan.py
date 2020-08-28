from math import floor
from typing import Union

from tmval.annuity import Annuity, olb_r, olb_p, get_loan_pmt
from tmval.growth import Amount, standardize_acc, TieredTime
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
        cents: bool = False
    ):
        self.pmt = pmt
        self.period = period
        self.term = term
        self.gr = gr
        self.cents = cents

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

        pmts_dict = get_loan_pmt(
            loan_amt=self.amt,
            period=self.period,
            term=self.term,
            gr=self.gr,
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
                gr=self.gr,
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
            gr=self.gr,
            t=t,
            r=r,
            missed=missed
        )

        return olb

    def amortize_payments(self, payments: Payments) -> dict:
        amt = Amount(gr=self.gr, k=self.amt)

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

    def principal_paid(self, t):
        return self.amt - self.olb_r(t)

    def total_payments(self, t):
        return floor(t / self.period) * self.pmt

    def interest_paid(self, t):
        return self.total_payments(t) - self.principal_paid(t)

    def principal_val(self, t):
        amt = Amount(gr=self.gr, k=self.amt)
        return amt.val(t)

    def amortization(self):

        res = self.amortize_payments(payments=self.pmt_sched)

        if self.cents:
            for k, v in res.items():
                res[k] = [round(x, 2) if isinstance(x, float) else x for x in v]

        return res
