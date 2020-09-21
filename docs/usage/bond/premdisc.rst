==========================
Bond Premium and Discount
==========================

The bond notation can be used to rearrange the basic price formula to arrive at the premium-discount formula:

.. math::

   P = C(g-j)\ax{\angln j} + C

A bond is said to sell at a premium if the price :math:`P` exceeds the redemption amount :math:`C`. Equivalently this is also the case when the modified coupon rate exceeds the yield rate per coupon period, when :math:`g > j`:

.. math::

   \text{premium} = P - C = C(g - j)\ax{\angln j}.

A bond is said to sell at a discount if the price :math:`P` is less than the redemption amount :math:`C`. Equivalently, this is also the case when the yield rate per coupon period exceeds the modified coupon rate, when :math:`j > g`:

.. math::

   \text{discount} = C - P = C(j - g)\ax{\angln j}.

Examples
=========

Suppose we have a 5-year, 1,000 5% par value bond with annual coupons, priced to yield 8% compounded annually. Find out if the bond sells at a premium or discount, and compute the magnitude of premium or discount.

TmVal's :class:`.Bond` class has an attribute called ``premium`` that represents the magnitude of the premium or discount. It is positive if the bond sells at a premium and negative if it sells at a discount. Since :math:`j > g` for this example, we would expect it to sell at a discount:


.. ipython:: python

   from tmval import Bond

   bd = Bond(
      face=1000,
      red=1000,
      alpha=.05,
      cfreq=1,
      term=5,
      gr=.08
   )

   print(bd.price)

   print(bd.price < bd.red)

   print(bd.premium)

Now, to see that the bond sells at a premium when :math:`g > j`, let's switch the yield and coupon percentages:

.. ipython:: python

   from tmval import Bond

   bd = Bond(
      face=1000,
      red=1000,
      alpha=.08,
      cfreq=1,
      term=5,
      gr=.05
   )

   print(bd.price)

   print(bd.price > bd.red)

   print(bd.premium)