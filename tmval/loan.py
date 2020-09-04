from math import ceil
from typing import Union

from tmval.annuity import Annuity, olb_r, olb_p, get_loan_pmt
from tmval.growth import Amount, TieredTime, standardize_acc
from tmval.value import Payments
from tmval.rate import Rate


class Loan:
    def __init__(
        self,
        gr: Union[Rate, float, TieredTime] = None,
        pmt: Union[float, int, Payments] = None,
        period: float = None,
        term: float = None,
        amt: float = None,
        cents: bool = False,
        sfr: Union[float, Rate, TieredTime] = None,
        sfd: float = None,
        sf_split: float = 1.0,
        sfh_gr: Union[float, Rate, TieredTime] = None,
        pp: float = None
    ):
        self.pmt = pmt
        self.period = period
        self.term = term
        if gr is not None:
            self.gr = standardize_acc(gr)
        else:
            self.gr = None
        self.cents = cents
        if sfr:
            self.sfr = standardize_acc(sfr)
        else:
            self.sfr = None
        self.sfd = sfd
        self.sf_split = sf_split
        self.pp = pp
        self.pmt_is_level = None

        if isinstance(pmt, Payments):
            self.pmt_sched = pmt
            if pmt.amounts[1:] == pmt.amounts[:-1]:
                self.pmt_is_level = True
            else:
                self.pmt_is_level = False

        if amt is None:
            if sfr is None:
                ann = Annuity(
                    period=self.period,
                    term=self.term,
                    gr=self.gr,
                    amount=self.pmt
                ).pv()
            elif sfr and sf_split == 1:
                ann_snk = Annuity(
                    period=self.period,
                    term=self.term,
                    gr=self.sfr,
                    amount=1
                ).pv()

                sf_i = self.gr.effective_interval(t2=self.period)
                sf_j = self.sfr.effective_interval(t2=self.period)
                ann = self.pmt * (ann_snk / (((sf_i - sf_j) * ann_snk) + 1))
            else:
                ann = self.hybrid_principal()

            self.amt = ann
        else:
            self.amt = amt

        if sfh_gr:
            self.sfh_gr = standardize_acc(sfh_gr)
        elif gr is not None and sfr is not None:
            self.sfh_gr = standardize_acc(self.sgr_equiv())
        else:
            self.sfh_gr = self.gr

        if pmt is None:
            if period and term:
                self.pmt_sched = self.get_payments()
                self.pmt = self.pmt_sched.amounts[0]
            elif pp:
                self.pmt_sched = self.get_payments()
                self.pmt = self.pmt_sched.amounts[0]

        if pmt and isinstance(pmt, (float, int)) and period and term:
            n_payments = ceil(term / period)
            self.pmt_sched = Payments(
                times=[(x + 1) * period for x in range(n_payments)],
                amounts=[pmt] * n_payments
            )
            self.pmt_is_level = True

        if sfr is not None and sfd is None and pmt is not None:
            sv = Annuity(
                gr=self.sfr,
                period=self.period,
                term=self.term
            ).sv()

            self.sfd = self.amt / sv

    def get_payments(self):

        if self.sfr:
            if self.sfd is not None:
                interest_due = self.gr.effective_interval(t2=self.period) * self.amt
                n_payments = ceil(self.term / self.period)

                final_pmt = self.sf_final()
                pmts = Payments(
                    amounts=[self.sfd + interest_due] * (n_payments - 1) + [final_pmt],
                    times=[(x + 1) * self.period for x in range(n_payments)]
                )

            else:
                interest_due = self.sfh_gr.effective_interval(t2=self.period) * self.amt
                n_payments = ceil(self.term / self.period)

                sv_ann = Annuity(
                    gr=self.sfr.effective_rate(self.period),
                    period=self.period,
                    term=self.term
                ).sv()

                sfd = self.amt / sv_ann
                amt = interest_due + sfd
                self.sfd = sfd
                pmts = Payments(
                    amounts=[amt] * n_payments,
                    times=[(x + 1) * self.period for x in range(n_payments)]
                )

        elif self.pp is not None:
            pmts = self.fixed_principal()

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

        if self.cents:
            for k, v in res.items():
                res[k] = [round(x, 2) if isinstance(x, float) else x for x in v]

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

        return res

    def sf_final(self, payments: Payments = None) -> float:

        if self.sfr is None:
            raise Exception("sf_final only applicable to sinking fund loans.")

        if payments:
            bal = self.amt
            t0 = 0
            sf_amounts = []
            sf_times = []
            for amount, time in zip(payments.amounts, payments.times):
                interest_due = bal * self.gr.effective_interval(t1=t0, t2=time)
                if amount >= interest_due:
                    sf_deposit = amount - interest_due
                else:
                    sf_deposit = 0
                    bal += interest_due - amount
                sf_amounts += [sf_deposit]
                sf_times += [time]
                t0 = time
            sf_payments = Payments(amounts=sf_amounts, times=sf_times, gr=self.sfr)

            sv = sf_payments.eq_val(self.term)

            final_pmt = bal * (1 + self.gr.effective_interval(t1=t0, t2=self.term)) - sv
        else:
            sv = Annuity(
                amount=self.sfd,
                gr=self.sfr,
                period=self.period,
                term=self.term - self.period
            ).eq_val(self.term)

            final_pmt = self.amt - sv

        return final_pmt

    def sink_payments(self, payments: Payments) -> dict:

        res = {
            'time': [],
            'interest_due': [],
            'sf_deposit': [],
            'sf_interest': [],
            'sf_bal': [],
            'loan_balance': []
        }

        # initial row
        res['time'] += [0]
        res['interest_due'] += [0]
        res['sf_deposit'] += [0]
        res['sf_interest'] += [0]
        res['sf_bal'] += [0]
        res['loan_balance'] += [self.amt]

        bal = self.amt
        sf_bal = 0
        t0 = 0
        for amount, time in zip(payments.amounts, payments.times):
            interest_due = bal * self.sfh_gr.effective_interval(t1=t0, t2=time)
            if amount >= interest_due:
                sf_deposit = amount - interest_due
            else:
                sf_deposit = 0
                bal += interest_due - amount

            sf_interest = sf_bal * self.sfr.effective_interval(t1=t0, t2=time)
            sf_bal += (sf_deposit + sf_interest)
            net_bal = bal - sf_bal
            res['time'] += [time]
            res['interest_due'] += [interest_due]
            res['sf_deposit'] += [sf_deposit]
            res['sf_interest'] += [sf_interest]
            res['sf_bal'] += [sf_bal]
            res['loan_balance'] += [net_bal]
            t0 = time

        if self.cents:
            for k, v in res.items():
                res[k] = [round(x, 2) if isinstance(x, float) else x for x in v]

        return res

    def sinking(self):
        res = self.sink_payments(payments=self.pmt_sched)

        return res

    def rc_yield(self):
        n_payments = ceil(self.term / self.period)
        if self.pmt_is_level:
            extra = [self.pmt - self.sfd] * n_payments

            sv = Annuity(
                amount=self.sfd,
                gr=self.sfr,
                term=self.term,
                period=self.period
            ).sv()

            pmts = Payments(
                amounts=[-self.amt] + extra + [sv],
                times=[0.0] + [(x + 1) * self.period for x in range(n_payments)] + [self.term],
                gr=self.sfr
            )

        else:
            sf_deps = self.sinking()['sf_deposit']

            extra = []
            for amount, sfd in zip(self.pmt_sched.amounts, sf_deps[1:]):
                extra_i = amount - sfd
                extra += [extra_i]

            sv = self.sinking()['sf_bal'][-1]

            pmts = Payments(
                amounts=[-self.amt] + extra + [sv],
                times=[0.0] + [(x + 1) * self.period for x in range(n_payments)] + [self.term],
                gr=self.sfr
            )

        return pmts.irr()

    def fixed_principal(self) -> Payments:
        # so far, last payment just gets adjusted
        n_payments = ceil(self.amt / self.pp)

        bal = self.amt
        times = [(x + 1) * self.period for x in range(n_payments)]
        amounts = []
        for x in range(n_payments):
            interest_due = bal * self.gr.effective_interval(t2=self.period)
            if bal >= self.pp:
                pmt = self.pp + interest_due
            else:
                pmt = bal + interest_due
            amounts += [pmt]
            bal -= self.pp

        pmts = Payments(
            times=times,
            amounts=amounts
        )

        return pmts

    def hybrid_principal(self):
        ann_am = Annuity(
            term=self.term,
            gr=self.gr,
            period=self.period
        )

        ann_sf = Annuity(
            term=self.term,
            gr=self.sfr,
            period=self.period
        )

        if self.sfh_gr:
            sfh = self.sfh_gr.effective_interval(t2=self.period)
        else:
            sfh = self.gr.effective_interval(t2=self.period)

        return self.pmt / (sfh * self.sf_split + self.sf_split / ann_sf.sv() + (1 - self.sf_split) / ann_am.pv())

    def sgr_equiv(self):

        if self.pmt_is_level:

            ann = Annuity(
                period=self.period,
                term=self.term,
                gr=self.gr
            ).pv()

            snn = Annuity(
                period=self.period,
                term=self.term,
                gr=self.sfr
            ).sv()

            gr = Rate(
                rate=1 / ann - 1 / snn,
                pattern="Effective Interest",
                interval=self.period
            )
        else:
            pmts = Payments(
                amounts=self.pmt_sched.amounts,
                times=self.pmt_sched.times,
                gr=self.sfr
            )

            snn = Annuity(
                period=self.period,
                term=self.term,
                gr=self.sfr
            )

            i = (pmts.eq_val(t=self.term) - self.amt) / (self.amt * snn.sv())

            gr = Rate(
                rate=i,
                pattern="Effective Interest",
                interval=self.period
            )

        return gr
