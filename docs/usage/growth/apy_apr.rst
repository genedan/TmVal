========================
APY vs APR
========================

So far, what we have called the annual effective interest rate is also called the APY, or :term:`annual percentage yield<annual percentage yield (APY)>`. However, in practice, banks often quote what is called the :term:`annual percentage rate (APR)`, which is not the same thing as the APY.

For example, the bank might quote something like an APR of 6% compounded twice a year. In reality, this means that after 6 months of opening an account, each dollar is compounded at %6 / 2 = 3%, and then compounded again at the same rate after another 6 months:

.. math::

   \left(1 + \frac{.06}{2}\right)^2 = 1.0609

Which is equivalent to an APY of 6.09%.

This concept is generalized in interest theory with a term called the :term:`nominal interest rate`. We denote this rate as :math:`i^{(m)}` compounded :math:`m` times per year. For example, an APR of 6% compounded twice per year is the same as a nominal interest rate of :math:`i^{(2)} = 6\%` compounded :math:`m=2` times per year. In each period, money grows at a factor of:

.. math::

   \left(1 + \frac{i^{(m)}}{m}\right)^m

The nominal and effective interest rates are related by the following equations:

.. math::

   i^{(m)} &= m[(1+i)^{\frac{1}{m}} - 1] \\

   i &= \left(1+\frac{i^{(m)}}{m}\right)^m - 1

Examples
==========

TmVal offers a way to convert between nominal and effective interest rates with the :func:`.eff_int_from_nom_int` and :func:`.nom_int_from_eff_int`.


Suppose we have a nominal interest rate of 6% compounded twice per year. What is the annual effective interest rate?

To start, we need to declare a nominal interest rate using TmVal's :class:`.NominalInt` class. This class takes the nominal interest rate and compounding frequency as arguments:

.. ipython:: python

   from tmval import NominalInt, eff_int_from_nom_int

   nom = NominalInt(im=.06, m=2)

   i = eff_int_from_nom_int(nom=nom)

   print(i)

Let's do the reverse to confirm that it's working. :class:`.NominalInt` has two attributes, the rate, which can be extracted with `NominalInt.val` and the compounding frequency, which can be extracted with `NominalInd.m`:

.. ipython:: python

   from tmval import nom_int_from_eff_int

   im = nom_int_from_eff_int(i=i, new_m=2)

   print(im.val)

If these function names seemed cumbersome, there's indeed a better way to do the conversions. TmVal has a general interest rate conversion function called convert_rate, to handle conversions between any two types of rates, including both interest and discount rates, which we'll expand upon in the next section:

.. ipython:: python

   from tmval import convert_rate

   i = convert_rate(
       nom_i=nom,
       intdisc='interest',
       effnom='effective'
   )

   print(i)