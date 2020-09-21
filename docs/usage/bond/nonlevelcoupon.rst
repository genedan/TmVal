=====================
Nonlevel Coupons
=====================

TmVal can handle nonlevel coupons as well. This feature can be found in some bonds that offer increasing coupon payments to hedge against inflation.

Examples
=========

Suppose we have a five year 1,000 bond with a redemption amount of 1,250. Annual coupons start at 5% and then increase by 2% each year. If the bond is priced to yield 5% compounded annually, what is the price of the bond?

We can solve this problem with TmVal by providing a list of tuples to the ``alpha`` argument of the :class:`.Bond` class. Each tuple in the list is an ordered pair that represents a coupon rate and the beginning of the time period in which it is applicable.

In this case, we want [(.05, 0), (.051, 1), (.05202, 2), (.0530604,3), (.054121608, 4)].

We also need to supply a corresponding list to the ``cfreq`` argument of equal length to the list provided to ``alpha``. Since that list has 5 elements, and for each of those periods we have one coupon payment, we set ``cfreq=[1,1,1,1,1]``. While this particular example has all 1s, this feature allows us to model more complex bonds where the coupon frequency is not the same for each period.

.. ipython:: python

   from tmval import Bond

   t = 5
   alpha_r = [.05 * 1.02 ** x for x in range(t)]
   alpha_t = [x for x in range(t)]
   alphas = [(x, y) for x, y in zip(alpha_r, alpha_t)]

   bd = Bond(
       face=1000,
       red=1250,
       alpha=alphas,
       cfreq=[1] * 5,
       gr=.05,
       term=t
   )

   # coupon amounts
   print(bd.coupons.amounts)

   # coupon times
   print(bd.coupons.times)

   print(bd.price)