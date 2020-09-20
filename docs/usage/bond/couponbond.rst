==================
Coupon Bonds
==================

Coupon bonds are bonds in which the bond issuer makes payments to the bondholder in addition to the redemption amount throughout the life of the bond.

Coupons are calculated specifying a face value :math:`F`, a coupon rate :math:`\alpha`, and the coupon frequency :math:`m`. The relationship between these values can be described by the following equation:

.. math::

   Fr = \frac{F\alpha}{m}.

When the face value equals the redemption amount, :math:`F = C`, we refer to the bond as being a :term:`par-value bond`.

Sometimes we'd like to specify the coupon rate as a :term:`modified coupon rate` :math:`g` in terms of the bond redemption amount :math:`C`:

.. math::

   g = \frac{Fr}{C}.

We can calculate the number of coupons :math:`n` by multiplying the bond term :math:`N` in years by the coupon frequency in number of coupons per year :math:`m`:

.. math::

   n = Nm.

We are often interested in the bond's yield to the investor, or bondholder, as a rate compounded yearly :math:`i`, or as a rate :math:`j`, specified in terms of the coupon period:

.. math::

   j = \frac{I}{m}

where

.. math::

   i = \left(1 + \frac{I}{m}\right)^m - 1.

The price :math:`P` of a bond is the present value of the coupons and the redemption amount. Using this information, we arrive at the basic price formula for a bond:

.. math::

   P = (Fr)\ax{\angln j} + Cv_j^n

Another property of a bond is called the base amount :math:`G`, which is the present value of a perpetuity of the coupon payments:

.. math::

   G = \frac{Fr}{j}

We can express the coupon amount using the face amount, redemption value, or base amount:

.. math::

   Fr = Cg = Gj

Examples
==========

Suppose we have a 5-year 1,000 5% bond with semiannual coupons, redeemable at par. What is the price of the bond if the yield is 10% compounded annually?

We can use TmVal to solve for the price just like we can with a zero coupon bond, but this time we need to supply the coupon information because this bond pays coupons. We can set the arguments ``alpha=.05`` and ``cfreq=4`` to represent the coupon rate and frequency, respectively. We also need to set the face value, ``face=1000``:

.. ipython:: python

   from tmval import Bond

   bd = Bond(
       face=1000,
       red=1000,
       alpha=.05,
       cfreq=4,
       term=5,
       gr=.10
   )

   print(bd.price)

Alternatively, we can specify the coupon rate and frequency to the argument ``cgr``. Since this information is equivalent to a nominal interest rate, you can supply it to ``cgr`` instead of using ``alpha`` and ``cfreq``:

.. ipython:: python

   from tmval import Bond, Rate

   cgr = Rate(
      rate=.05,
      pattern="Nominal Interest",
      freq=4
   )

   bd = Bond(
       face=1000,
       red=1000,
       cgr=cgr,
       term=5,
       gr=.10
   )

   print(bd.price)

Now, let's examine various properties of this bond:

.. ipython:: python

   # coupon amount
   print(bd.fr)

   # number of coupons
   print(bd.n_coupons)

   # base amount
   print(bd.g)

   # coupon payments
   print(type(bd.coupons))
   print(bd.coupons.amounts)
   print(bd.coupons.times)

   # yield per coupon period
   print(bd.j)

Let's use this information to verify :math:`Fr = Cg = Gj`:

.. ipython:: python

   # Fr
   fr = bd.fr
   print(bd.fr)

   # Cg
   cg = bd.g * bd.red
   print(cg)

   # Gj
   gj = bd.base * bd.j
   print(gj)

   print(fr == cg == gj)