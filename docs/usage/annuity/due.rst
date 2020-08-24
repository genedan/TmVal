==============
Annuities-Due
==============

An :term:`annuity-due` is a type of annuity in which the payments occur at the beginning of each payment period. We define a :term:`basic annuity-due` as an annuity-due in which every payment equals 1.

The formulas for basic annuities-due are similar to those for basic annuities-immediate, except the present value of the basic annuity-due is taken at the time of the first payment, and the accumulated value is taken at the next period following the final payment of the annuity. In the case of compound interest:

.. math::

   \ax**{\angln i} = 1 + v + v^2 + v^3 + \cdots + v^{n-1} = \frac{1 - v^n}{d}

.. math::

   \sx**{\angln i} = (1 + i)^n + (1 + i)^{n-1} + (1 + i)^{n-2} + \cdots + (1 + i)^1 = \frac{(1+i)^n -1}{d}

Examples
=========

Suppose we have a basic annuity-due that pays 1 at the beginning of each year for 5 years at an annual effective interest rate of 5%. What is the present value?

Again we can use TmVal's :class:`.Annuity` class to solve this problem. The change from the previous section's example is that this time, we just need to change specify that our annuity is an annuity-due by setting the argument `imd='due'`. This argument defaults to 'immediate,' which is why we didn't need to set it last time:

.. ipython:: python

   from tmval import Annuity, Rate

   ann = Annuity(
      amount=1,
      term=5,
      period=1,
      gr=Rate(.05),
      imd='due'
   )

   print(ann.pv())

As before, we can also reduce the number of arguments provided by simply providing the number of payments and interest rate, but this time also the `imd` argument:

.. ipython:: python

   from tmval import Annuity, Rate

   ann = Annuity(
      n=5,
      gr=Rate(.05)
   )

   print(ann.pv())

What is the accumulated value? We can use :func:`.Annuity.sv()` to find out:

.. ipython:: python

   print(ann.sv())