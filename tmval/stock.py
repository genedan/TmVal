from copy import deepcopy

from tmval.rate import Rate, standardize_rate
from tmval.value import Payments


class Stock:
    def __init__(
        self,
        compref='common',
        div=None,
        dfreq=None,
        gr: Rate = None,
        shares=1,
        price: float = None,
        margin_req: float = .5,
        maint_req: float = None
    ):

        self.compref = compref
        self.div = div
        self.dfreq = dfreq
        self.shares = shares
        self.gr = gr
        self.margin_req = margin_req
        self.maint_req = maint_req

        if price is None:
            self.price = self.get_price()
        else:
            self.price = price

    @property
    def value(self):
        return self.price * self.shares

    def get_price(self):
        if self.compref == 'preferred':
            divr = self.gr.convert_rate(
                pattern="Effective Interest",
                interval=1/self.dfreq
            )

            return self.shares * self.div / divr


class Brokerage:

    def __init__(
        self,
        deposit,
        sma=False,
        ndb_rate=0,
        margin_rate=0
    ):

        self.cash = deposit
        self.portfolio = []
        self.sma = sma
        self.ndb_rate = ndb_rate
        self.margin_rate = margin_rate
        self.age = 0
        if sma:
            self.sma_val = 0
        else:
            self.sma_val = None

    @property
    def market_value(self):

        if len(self.portfolio) == 0:
            return 0
        else:
            return sum([x['stock'].value for x in self.portfolio])

    @property
    def ndb(self):

        if len(self.portfolio) == 0:
            return 0
        else:
            return sum([x['ndb'] for x in self.portfolio])

    @property
    def equity(self):
        if not self.sma:
            return self.market_value - self.ndb
        else:
            return self.market_value - self.sma_val - self.ndb

    @property
    def margin(self):

        if self.market_value == 0:
            return None
        else:
            return self.equity / self.market_value

    def purchase_stock(
        self,
        stock: Stock = None,
        deposit=None,
        t=0,
        idx=None
    ):
        if stock is not None:
            if deposit is None:
                if self.cash >= stock.value:
                    self.cash -= stock.value
                    borrow = 0
                    ndb = 0
                else:
                    borrow = stock.value - self.cash
                    self.cash -= self.cash
                    ndb = borrow
            else:
                if self.cash + deposit >= stock.value:
                    self.cash += deposit - stock.value
                    borrow = 0
                    ndb = 0
                else:
                    borrow = stock.value - deposit - self.get_extra()
                    ndb = borrow

            pmts = Payments(
                amounts=[-stock.value + borrow],
                times=[t]
            )

            res = {
                'stock': stock,
                'ndb': ndb,
                'payments': pmts,
                'position': 'long'
            }

            self.portfolio += [res]
        else:
            if self.portfolio[idx]['position'] == 'short':
                self.portfolio[idx]['margin_deposit'] *= (1 + self.margin_rate) ** (t - self.age)
                print(self.portfolio[idx]['margin_deposit'])
                repurchase = self.portfolio[idx]['stock'].value

                avail = self.cash + self.portfolio[idx]['margin_deposit']

                div_sv = self.portfolio[idx]['dividends'].eq_val(t)

                due = avail - repurchase - div_sv

                self.portfolio[idx]['margin_deposit'] = 0
                self.portfolio[idx]['stock'].shares = 0
                self.cash = due

                self.portfolio[idx]['payments'].append(
                    amounts=[due],
                    times=[t]
                )

        self.age = t

    def margin_threshold(self, idx=None, per=False):
        """
        Calculates the price at which a margin call will be made.

        :param idx:
        :type idx:
        :param per:
        :type per:
        :return:
        :rtype:
        """

        if idx is not None:
            st = self.portfolio[idx]

            p = st['ndb'] / ((1 - st['stock'].maint_req) * (st['stock'].shares if per else 1))
        else:
            p = 0
            for st in self.portfolio:
                p += st['ndb'] / (1 - st['stock'].maint_req)

        return p

    def prospect_deposit(self, st: Stock):
        """
        Find the deposit needed to purchase more stock.
        """

        extra = self.get_extra()

        margin_req = st.value * st.margin_req

        deposit = margin_req - extra

        return deposit

    def get_extra(self):

        extra = self.equity
        for x in self.portfolio:
            extra -= x['stock'].value * x['stock'].margin_req

        return extra

    def meet_maint(self):
        """
        Calculates the amount required to meet the maintenance margin.
        :return:
        :rtype:
        """
        amt = 0
        for x in self.portfolio:
            amt += x['stock'].value * x['stock'].maint_req

        return amt - self.equity

    def prospect_ps_margin(self, idx, chg):

        portfolio = deepcopy(self.portfolio)

        mreq = self.margin_threshold()

        val_other = 0
        for c in chg:
            c_idx = c[0]
            print(portfolio[c_idx])
            portfolio[c_idx]['stock'].price = c[1]
            val_other += portfolio[c_idx]['stock'].value

        sreq = mreq - val_other

        res = sreq / portfolio[idx]['stock'].shares

        return res

    def prospect_s_deposit(self, maint_req):
        """
        Calculates the price of a security needed, if it is to be added to meet a margin call.

        :return:
        :rtype:
        """

        req_base = 0
        for x in self.portfolio:
            req_base += x['stock'].value * x['stock'].maint_req

        print(req_base)

        s = (req_base - self.equity) / (1 - maint_req)

        return s

    def prospect_s_sale(self, idx):

        p = self.portfolio[idx]['stock'].price
        margin_req = self.portfolio[idx]['stock'].margin_req

        return p - self.equity / margin_req

    def set_sma(self):
        self.sma_val += self.get_extra()

    def dividend(self, idx, amt, t):
        t -= self.age
        div = self.portfolio[idx]['stock'].shares * amt
        self.portfolio[idx]['ndb'] *= (1 + self.ndb_rate) ** t
        if self.portfolio[idx]['ndb'] == 0:

            if self.portfolio[idx]['position'] == 'short':
                # self.cash += div
                self.portfolio[idx]['margin_deposit'] *= (1 + self.margin_rate) ** t
                self.portfolio[idx]['dividends'].append(
                    amounts=[div],
                    times=[t + self.age]
                )
            else:
                self.portfolio[idx]['payments'].append(
                    amounts=[div],
                    times=[t]
                )


        elif div > self.ndb:
            self.portfolio[idx]['ndb'] = 0
            extra = div - self.ndb
            self.portfolio[idx]['payments'].append(
                amounts=[extra],
                times=[t]
            )
        else:
            self.portfolio[idx]['ndb'] -= div
        self.age += t

    def sell_stock(self, idx, shares, t):
        self.portfolio[idx]['ndb'] *= (1 + self.ndb_rate) ** (t - self.age)
        proceeds = self.portfolio[idx]['stock'].price * shares - self.portfolio[idx]['ndb']
        self.portfolio[idx]['stock'].shares -= shares
        self.cash += proceeds
        self.portfolio[idx]['payments'].append(
            amounts=[proceeds],
            times=[t]
        )

    def yield_s(self, idx):
        irr = self.portfolio[idx]['payments'].irr()
        return irr

    def prospect_yield_s(self, idx, shares, t, price):
        s_c = deepcopy(self.portfolio[idx])
        s_c['stock'].price = price
        s_c['ndb'] *= (1 + self.ndb_rate) ** (t - self.age)
        print(s_c['ndb'])
        proceeds = s_c['stock'].price * shares - s_c['ndb']
        print(proceeds)
        s_c['payments'].append(
            amounts=[proceeds],
            times=[t]
        )
        print(s_c['payments'].amounts)
        print(s_c['payments'].times)
        irr = s_c['payments'].irr()
        return irr

    def short(self, st: Stock, deposit=None, t=0):

        sale_amt = st.value
        if deposit is None:
            self.cash += sale_amt
            md = st.value * st.margin_req
            self.cash -= md
        else:
            self.cash += sale_amt + deposit
            md = st.value * st.margin_req
            self.cash -= md
  
        pmts = Payments(
            amounts=[-md],
            times=[t]
        )

        divs = Payments(
            amounts=[],
            times=[],
            gr=self.margin_rate
        )

        res = {
            'stock': st,
            'ndb': 0,
            'margin_deposit': md,
            'position': 'short',
            'payments': pmts,
            'dividends': divs
        }
        
        self.portfolio += [res]

    def margin_call(self, idx, deposit, t):
        if self.portfolio[idx]['position'] == 'short':
            self.portfolio[idx]['margin_deposit'] *= (1 + self.margin_rate) ** (t - self.age)
            self.portfolio[idx]['margin_deposit'] += deposit
            self.portfolio[idx]['payments'].append(
                amounts=[-deposit],
                times=[t]
            )
        self.age = t