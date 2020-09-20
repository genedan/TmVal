==================
Zero-Coupon Bonds
==================

Zero-coupon bonds are bonds that do not pay any coupons. They are the simplest type of bond, in which a bond issuer sells the bond to a bondholder. The price paid for the bond is the amount of money loaned the bond issuer from the bondholder. At the end of a specified amount of time, the bond issuer pays a redemption amount to the bondholder to settle the debt.

Examples
=========

Suppose an entity issues a bond for 1,000 to be repaid in 5 years for 1,200. What is the yield rate on the bond?

Since we know the price, redemption amount, and term, we can supply these to the :class:`.Bond` class arguments ``price``, ``red``, and ``term`` respectively. The :class:`.Bond` class constructor will automatically detect which argument is missing and solve for it. We can then find the missing value (in this case the yield rate) by printing the attribute.

.. ipython:: python

   from tmval import Bond

   bd = Bond(
       price=1000,
       red=1200,
       term=5
   )

   print(bd.irr())

To further illustrate how :class:`.Bond` can solve for missing values, here are some more examples with various missing values.

If an entity issues a bond for 1,000 to be repaid in 5 years with a yield of 5% compounded annually, what should the redemption amount be?

.. ipython:: python

   bd = Bond(
       price=1000,
       gr=.05,
       term=5
   )

   print(bd.red)

If an entity issues a bond redeemable for 1,200 in 5 years at a yield rate of 5% compounded annually, what is the price of the bond?

.. ipython:: python

   bd = Bond(
       red=1200,
       gr=.05,
       term=5
   )

   print(bd.price)

If an entity issues a bond for a price of 1,000, to be redeemed for 1,200 at a yield rate of 5% compounded annually, what is the term of the bond?


.. ipython:: python

   bd = Bond(
      price=1000,
      red=1200,
      gr=.05
   )

   print(bd.term)