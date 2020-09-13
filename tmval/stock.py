from tmval.rate import Rate

class Stock:
    def __init__(
        self,
        compref='common',
        div=None,
        dfreq=None,
        gr: Rate = None,
        shares=1
    ):

        self.compref = compref
        self.div = div
        self.dfreq = dfreq
        self.shares = shares
        self.gr = gr

    def price(self):
        if self.compref == 'preferred':
            divr = self.gr.convert_rate(
                pattern="Effective Interest",
                interval=1/self.dfreq
            )

            return self.shares * self.div / divr


