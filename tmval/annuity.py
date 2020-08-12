from collections import namedtuple
import decimal
import numpy as np
from tmval.value import Payments, Rate
from tmval.growth import CompoundAcc
from math import ceil


class Annuity(Payments):

    def __init__(
        self,
        interval,
        term,
        gr,
        amount=1.0,
    ):
        self.term = term
        self.amount = amount
        self.interval = interval

        n_payments = term / interval
        n_payments = int(ceil(n_payments))
        amounts = [amount] * n_payments
        times = [interval * (x + 1) for x in range(n_payments)]
        Payments.__init__(
            self,
            amounts=amounts,
            times=times,
            gr=gr
        )

    def pv(self):

        pv = self.amount * (1 - self.acc.discount_func(self.term)) / (self.acc.val(self.interval) - 1)

        return pv

    def sv(self):

        sv = self.amount * ((1 + self.acc.interest_rate) ** self.term - 1) / (self.acc.val(self.interval) - 1)

        return sv


def get_loan_amt(down_pmt: float, loan_pmt: float, interval: float, term: float, gr: Rate) -> float:

    ann = Annuity(interval=interval, term=term, amount=loan_pmt, gr=gr)

    loan_amt = ann.pv() + down_pmt

    return loan_amt


def get_loan_pmt(loan_amt: float, interval: float, term: float, gr: Rate, cents=False):

    ann = Annuity(interval=interval, term=term, gr=gr)

    pmt = loan_amt / ann.pv()

    if cents:
        acc = CompoundAcc(gr=gr)
        pmt_round = round(pmt, 2)
        pv = Annuity(amount=pmt_round, interval=interval, term=term, gr=gr).pv()
        if loan_amt == round(pv, 2):
            return pmt
        else:
            cent = decimal.Decimal('0.01')
            pmt_round2 = float(decimal.Decimal(pmt).quantize(cent, rounding=decimal.ROUND_UP))
            diff = Annuity(amount=pmt_round2, interval=interval, term=term, gr=gr).pv() - loan_amt
            last_pmt = pmt_round2 - round(diff * acc.val(t=term), 2)
            Installments = namedtuple('installments', 'amount last')
            return Installments(pmt_round2, last_pmt)
    else:
        return pmt


def get_savings_pmt(fv: float, interval: float, term: float, gr: Rate, cents=False):

    ann = Annuity(interval=interval, term=term, gr=gr)

    pmt = fv / ann.sv()

    if cents:
        pmt_round = round(pmt, 2)
        fv2 = Annuity(amount=pmt_round, interval=interval, term=term, gr=gr).sv()
        if fv == round(fv2, 2):
            return pmt
        else:
            cent = decimal.Decimal('0.01')
            pmt_round2 = float(decimal.Decimal(pmt).quantize(cent, rounding=decimal.ROUND_UP))
            diff = Annuity(amount=pmt_round2, interval=interval, term=term, gr=gr).sv() - fv
            last_pmt = round(pmt_round2 - round(diff, 2), 2)
            Installments = namedtuple('installments', 'amount last')
            return Installments(pmt_round2, last_pmt)
    else:
        return pmt


def get_number_of_pmts(pmt: float, fv: float, interval: float, gr: Rate):

    i = gr.convert_rate(
        'Effective Interest',
        interval=interval
    )

    n = np.log(fv / pmt * i + 1) / np.log(1 + i)

    n = ceil(n)

    return n
