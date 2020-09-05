========================
Nominal Interest
========================

.. meta::
   :description: Nominal vs effective interest.
   :keywords: nominal interest, effective interest, compounding frequency, python, package, interest, financial mathematics

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

Now that we've introduced the concept of nominal interest, we can demonstrate how to define a nominal interest rate by using TmVal's :class:`.Rate` class by setting the ``pattern`` argument. Nominal interest is one of the valid patterns that you can provide to :class:`.Rate`.

Let's define a nominal interest rate of 6%, compounded twice per year.

.. ipython:: python

   from tmval import Rate

   nom = Rate(
       rate=.06,
       pattern="Nominal Interest",
       freq=2
   )

   print(nom)

We can also demonstrate some more interesting rate conversions than we had previously. What annual effective interest rate is equivalent to a nominal interest rate of 6%, compounded twice per year?

.. ipython:: python

   i = nom.convert_rate(
       pattern="Effective Interest",
       interval=1
       )

   print(i)

Let's do the reverse to confirm that it's working:

.. ipython:: python

   nom2 = i.convert_rate(
       pattern="Nominal Interest",
       freq=2
   )

   print(nom2)

There are some shortcut aliases that you can provide to the ``pattern`` argument to shorten the amount of typing you need to do. One of them is 'apr,' if you are more comfortable using calling a nominal interest rate the annual percentage rate:

.. ipython:: python

   nom3 = Rate(
       rate=.06,
       pattern='apr',
       freq=2
   )

   print(nom3)
