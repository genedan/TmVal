from math import floor

from tmval.annuity import olb_r
from tmval.rates import Rate


class Loan:
    def __init__(
        self,
        amt,
        pmt,
        period,
        term,
        gr: Rate,
    ):
        self.amt = amt
        self.pmt = pmt
        self.period = period
        self.term = term
        self.gr = gr

    def olb_r(self, t):

        olb = olb_r(
            loan=self.amt,
            q=self.pmt,
            period=self.period,
            gr=self.gr,
            t=t
        )

        return olb

    def principal_paid(self, t):
        return self.amt - self.olb_r(t)

    def total_payments(self, t):
        return floor(t / self.period) * self.pmt

    def interest_paid(self, t):
        return self.total_payments(t) - self.principal_paid(t)
