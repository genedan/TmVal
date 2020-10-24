===========================================
Nonlevel Annuities - Geometric Progression
===========================================

.. meta::
   :description: TmVal documentation on nonlevel annuities with payments of increasing geometric progression.
   :keywords: annuity, nonlevel, non-level, geometric, progression, payment, function, formula, actuarial, python, package

Annuities can have payments that increase geometrically. For example, an annuity might have payments that increase by 2% per year. If we have payments that increase by g% per year, we define the present value of an annuity-immediate with an initial payment :math:`P` as:

.. math::

   P\left(\frac{1-\left(\frac{1 + g}{1 + i}\right)^n}{i-g}\right),

where :math:`i-g \neq 0`, since this expression is undefined when the denominator is 0. If the payments increase at the rate of interest, we have:

.. math::

   nP(1 + i)^{-1}.

Examples
=========

Suppose we have an annuity-immediate with end-of-year payments that pays 1 at the end of the first period, and then whose payments increase by 2% for each year for the next 4 years. If the interest rate is 5% compounded annually, what is its present value?

We can solve this problem by using TmVal's :class:`.Annuity` class, and by providing the rate of payment increase to the argument ``gprog``, which in this case is ``gprog=.02``:

.. ipython:: python

   from tmval import Annuity, Rate

   ann = Annuity(
      gr=Rate(.05),
      n=5,
      gprog=(.02)
   )

   print(ann.pv())