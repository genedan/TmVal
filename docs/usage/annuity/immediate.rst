====================
Annuities-Immediate
====================

An :term:`annuity-immediate` is a type of annuity in which the payments occur at the end of each payment period. We define a :term:`basic annuity-immediate` as an annuity immediate in which every payment equals 1.

Basic annuities-immediate are convenient because the formulas specifying their present and accumulated values can be reduced to simple, compact algebraic expressions. For example, the present value of a basic annuity-immediate that pays 1 for :math:`n` periods at compound effective interest rate :math:`i` per period is:

.. math::

   \ax{\angln i} = v + v^2 + v^3 + \cdots + v^n = \frac{1 - v^n}{i}

The accumulated value at time :math:`n` is :

.. math::

   \sx{\angln i} = (1 + i)^{n-1} + (1+i)^{n-2} + \cdots + 1 = \frac{(1+i)^n - 1}{i}

Examples
=========

Suppose we have a basic annuity-immediate that pays 1 at the end of each year for 5 years at an annual effective interest rate of 5%. What is the present value?

We can solve this problem by importing the :class:`.Annuity` class, TmVal's general class that can be used to represent most types of annuities. We can specify the payment amount with the argument `amount=1`, the 5-year term as `term=5`, the 1-year payment interval as `period=1`, and the 5% interest rate as `gr=Rate(.05)`.

We then use the method :func:`.Annuity.pv` to get the present value:

.. ipython:: python

   from tmval import Annuity, Rate

   ann = Annuity(
      amount=1,
      term=5,
      period=1,
      gr=Rate(.05)
   )

   print(ann.pv())

Note that we can simplify the above answer and make it more consistent with actuarial notation by simply supplying the number of payments as `n=5`. Since the period defaults to 1 year, the amount defaults to 1, we only need to supply two arguments in the case of a basic annuity-immediate:

.. ipython:: python

   ann = Annuity(
      n=5,
      gr=Rate(.05)
   )

   print(ann.pv())

What is the accumulated value? We can use :func:`.Annuity.sv()` to find out:

.. ipython:: python

   print(ann.sv())