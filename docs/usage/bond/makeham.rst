=================
Makeham's Formula
=================

Makeham's formula can also be derived via bond notation and can be useful for obtaining the price of a bond when we do not know the number of coupons:

.. math::

   P = \frac{g}{j}(C-K) + K,

where :math:`K` is the present value of the redemption amount.


Examples
=========

Suppose we have a 1,000 bond that pays 5% annual coupons. The redemption amount is 1,250 and the present value of the redemption amount is 776.1516538. If it is priced to yield 10% compounded annually, what is the price of the bond? Also, find the term and number of coupons.

TmVal's :class:`.Bond` class has a method called :meth:`.makeham` which it calls internally when the term and price are missing, and when the present value of the redemption amount is provided via the ``k`` argument. Because it is called internally, we do not have to explicitly call this method to get the bond price.

.. ipython:: python

   from tmval import Bond

   bd = Bond(
      face=1000,
      red=1250,
      k=776.1516538,
      alpha=.05,
      cfreq=1,
      gr=.10
   )

   print(bd.term)

   print(bd.n_coupons)

   print(bd.price)

We could call :meth:`.makeham` anyway, just to verify:

.. ipython:: python

   print(bd.makeham())