from math import floor
from typing import Union

from tmval.annuity import Annuity, olb_r, olb_p
from tmval.growth import TieredTime
from tmval.rate import Rate


class Loan:
    def __init__(
        self,
        pmt,
        period,
        gr: Union[Rate, float, TieredTime],
        term: float = None,
        amt: float = None,
    ):
        self.pmt = pmt
        self.period = period
        self.term = term
        self.gr = gr

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

    def olb_r(self, t):

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

    def principal_paid(self, t):
        return self.amt - self.olb_r(t)

    def total_payments(self, t):
        return floor(t / self.period) * self.pmt

    def interest_paid(self, t):
        return self.total_payments(t) - self.principal_paid(t)
