from copy import deepcopy

from tmval.rate import Rate


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
        sma=False
    ):

        self.cash = deposit
        self.portfolio = []
        self.sma = sma
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
        stock: Stock,
        deposit=None
    ):
        if deposit is None:
            if self.cash >= stock.value:
                self.cash -= stock.value
                ndb = None
            else:
                borrow = stock.value - self.cash
                self.cash -= self.cash
                ndb = borrow
        else:
            if self.cash + deposit >= stock.value:
                self.cash += deposit - stock.value
                ndb = None
            else:
                borrow = stock.value - deposit - self.get_extra()
                ndb = borrow

        res = {
            'stock': stock,
            'ndb': ndb,
            'initial_margin_req': stock.value * stock.margin_req
        }

        self.portfolio += [res]

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