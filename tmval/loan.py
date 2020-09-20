from math import ceil
from typing import List, Union

from tmval.annuity import (
    Annuity,
    get_loan_pmt,
    olb_r,
    olb_p
)

from tmval.growth import (
    Amount,
    standardize_acc,
    TieredTime
)

from tmval.value import Payments
from tmval.rate import Rate


class Loan(Payments):

    """
    Loan is TmVal's class for representing loans. TmVal currently supports amortized loans, sinking fund loans,
    amortized/sinking hybrid loans, and payment of fixed principal loans. You can specify the loan type by supplying
    the appropriate argument.

    The default case is an amortized loan, when gr, period, term, and payment amount are supplied without a
    corresponding sinking fund rate or fixed principal payment. You do not have to supply all of the arguments. If
    enough of them are supplied, the missing arguments are automatically calculated.

    For sinking fund loans, specify the amount of the sinking fund deposit and the sinking fund rate.

    For fixed principal loans, the payment is a fixed amount of principal which can be supplied with the argument pp.


    :param gr: The interest rate of the loan.
    :type gr: float, Rate, TieredTime
    :param period: The time interval between payments, if the loan has regular payments.
    :type period: float
    :param term: The term of the loan.
    :type term: float
    :param amt: The loan amount.
    :type amt: float
    :param cents: Whether you want the payments to be rounded to cents. Defaults to False.
    :type cents: bool
    :param sfr: The sinking fund rate, if different from the loan interest rate.
    :type sfr: float, Rate, TieredTime
    :param sfd: The sinking fund deposit amount.
    :type sfd: float
    :param sf_split: If using a hybrid amortized/sinking loan, the % of the loan that is a sinking fund loan.
    :type sf_split: float
    :param sfh_gr: In the case of a hybrid loan, the loan interest rate of the sinking fund portion, if it differs \
    from the amortization rate.
    :type sfh_gr: float, Rate, TieredTime
    :param pp: The principal payment, in the case of a fixed principal loan.
    :type pp: float

    """
    def __init__(
        self,
        gr: Union[float, Rate, TieredTime] = None,
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

        elif pmt and isinstance(pmt, (float, int)) and period and term:
            n_payments = ceil(term / period)
            self.pmt_sched = Payments(
                times=[(x + 1) * period for x in range(n_payments)],
                amounts=[pmt] * n_payments
            )
            self.pmt_is_level = True
        else:
            self.pmt_sched = Payments(
                times=[],
                amounts=[]
            )

        if sfr is not None and sfd is None and pmt is not None:
            sv = Annuity(
                gr=self.sfr,
                period=self.period,
                term=self.term
            ).sv()

            self.sfd = self.amt / sv

        Payments.__init__(
            self,
            amounts=[amt] + [-x for x in self.pmt_sched.amounts],
            times=[0] + self.pmt_sched.times,
            gr=self.gr
        )

    def get_payments(self) -> Payments:

        """
        Takes the arguments supplied and creates the payment schedule for the loan. The return type is a \
        :class:`.Payments` object, so it contains the payment times and amounts.

        :return: The payment schedule.
        :rtype: Payments
        """

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

    def olb_r(
        self,
        t: float,
        payments: Payments = None
    ) -> float:

        """
        Calculates the outstanding loan balance at time t, using the retrospective method. If the actual payments
        differ from the original payment schedule, they may be supplied to the payments argument.

        :param t: The valuation time.
        :type t: float
        :param payments: A list of payments, if they differed from the original payment schedule.
        :type payments: Payments
        :return: The outstanding loan balance.
        :rtype: float
        """

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
            missed: List[int] = None
    ) -> float:

        """
        Calculates the outstanding loan balance via the prospective method. If there were missed payments, they
        may be indicated by supplying them to the missed argument.

        :param t: The valuation time.
        :type t: float
        :param r: The final payment amount, if different from the others, defaults to None.
        :type r: float
        :param missed: A list of missed payments, for example, 4th and 5th payments would be [4, 5].
        :type missed: List[int]
        :return: The outstanding loan balance.
        :rtype: float
        """

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

    def amortize_payments(
        self,
        payments: Payments
    ) -> dict:

        """
        Amortizes a list of payments, this function is used when the actual payments differ from the original \
        amortization table. It returns a dict, which may be passed to something like a pandas DataFrame for further
        analysis and viewing.

        :param payments: A list of payments.
        :type payments: Payments
        :return: An amortization table of the payments.
        :rtype: dict
        """
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

    def principal_paid(
        self,
        t2: float,
        t1: float = 0
    ) -> float:

        """
        Calculates the principal paid between two points in time..

        :param t2: The second point in time.
        :type t2: float
        :param t1: The first point in time.
        :type t1: float
        :return: The principal paid.
        :rtype: float
        """

        if self.sfr:
            return 0
        else:
            return self.olb_r(t1) - self.olb_r(t2)

    def total_payments(
        self,
        t2: float,
        t1: float = 0
    ) -> float:

        """
        Calculates the total loan payments that occurred between two points in time.

        :param t2: The second point in time.
        :type t2: float
        :param t1: The first point in time.
        :type t1: float
        :return: The total loan payments.
        :rtype: float
        """
        return round((t2 - t1) / self.period, 1) * self.pmt

    def interest_paid(
        self,
        t2: float,
        t1: float = 0,
        frac: bool = False
    ) -> float:

        """
        Calculates the total interest paid between two points in time.

        :param t2: The second point in time.
        :type t2: float
        :param t1: The first point in time.
        :type t1: float
        :param frac: Whether you want the answer as a fraction of the total interest of the loan.
        :type frac: bool
        :return: The total interest paid.
        :rtype: float
        """
        interest_paid = self.total_payments(t1=t1, t2=t2) - self.principal_paid(t1=t1, t2=t2)

        if frac:
            total_interest = self.interest_paid(t2=self.term)
            res = interest_paid / total_interest
            return res
        else:
            return interest_paid

    def principal_val(
        self,
        t: float
    ) -> float:
        """
        Calculates the time-value adjusted principal at a desired point in time.

        :param t: The valuation time.
        :type t: float
        :return: The time-value adjusted principal.
        :rtype: float
        """

        amt = Amount(gr=self.gr.gr, k=self.amt)

        return amt.val(t)

    def amortization(self) -> dict:
        """
        Calculates the amortization table based off the original payment schedule. Returned as a dict which can be \
        supplied to a pandas DataFrame for further analysis and viewing.

        :return: The amortization table.
        :rtype: dict
        """

        res = self.amortize_payments(payments=self.pmt_sched)

        return res

    def sf_final(
        self,
        payments: Payments = None
    ) -> float:

        """
        Calculates the final payment required to settle a sinking fund loan. You may supply payments, if they differed \
        from the original payment schedule.

        :param payments: A list of payments, if different from the original payment schedule.
        :type payments: Payments, optional
        :return: The final sinking fund payment.
        :rtype: float
        """

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

    def sink_payments(
            self,
            payments: Payments
    ) -> dict:

        """
        Calculates a sinking fund schedule for a list of payments. Intended to be called externally only if the \
        payments differ from the original sinking fund schedule. Otherwise, use the :meth:`.sinking` method. The \
        return type is a dict which can be passed to a pandas DataFrame for further analysis and viewing.

        :param payments: A list of payments.
        :type payments: Payments
        :return: The sinking fund schedule for the payments.
        :rtype: dict
        """

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

    def sinking(self) -> dict:
        """
        Calculates the sinking fund schedule based off the original payment schedule. The \
        return type is a dict which can be passed to a pandas DataFrame for further analysis and viewing.

        :return: The sinking fund schedule.
        :rtype: dict
        """
        res = self.sink_payments(payments=self.pmt_sched)

        return res

    def rc_yield(self) -> list:
        """
        Calculates the yield rate based off replacement of capital.

        :return: The yield rate based off replacement of capital.
        :rtype: list
        """
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
        """
        Calculates the loan payment schedule if a fixed amount of principal is paid each period.

        :return: The payment schedule.
        :rtype: Payments
        """
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

    def hybrid_principal(self) -> float:
        """
        Calculates the loan amount based on a hybrid amortized/sinking fund loan.

        :return: The loan amount.
        :rtype: float
        """
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

    def sgr_equiv(self) -> Rate:

        """
        Calculates the sinking fund rate such that would produce a loan payment schedule equivalent to that of an
        amortized loan.

        :return: The sinking fund rate.
        :rtype: Rate
        """

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
