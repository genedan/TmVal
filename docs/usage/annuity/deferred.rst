===================
Deferred Annuities
===================

A :term:`deferred annuity` is a type of annuity whose first payment begins more than one payment period later than its present valuation date. For example, we can purchase a deferred annuity-immediate today that makes annual payments beginning 5 years from now.

We denote a deferred annuity-immediate as :math:`\ax[w|n]{}`, where :math:`w` indicates that the first payment will occur :math:`w + 1` periods from the present valuation date. For example, the annuity in the preceding paragraph would be denoted :math:`\ax[4|n]{}` because the first payment occurs at time 5, which is equal to :math:`w + 1`, since in this case :math:`w = 4`.

Annuities-immediate, deferred annuities-due, and deferred annuities-immediate are related by the following expression:

.. math::

   \ax{\angln} = \ax**[1|n]{} = \ax[0|n]{}

Examples
===========

Suppose we purchase an annuity-immediate deferred for 4 years. This annuity makes a payment of 1,000 each year for a term of five years, with the first payment beginning 5 years from now. If the annual effective interest rate is 5%, how much does the annuity cost?

We can solve this problem by using TmVal's :class:`.Annuity` class, and specifying the deferral by setting the argument ``deferral=4``.

.. ipython:: python

   from tmval import Annuity, Rate

   ann = Annuity(
      amount=1000,
      n=5,
      gr=Rate(.05),
      deferral=4
   )

   print(ann.pv())

Now suppose we want to know, if we reinvest the payments at the 5% effective rate, how much will the investments grow to 20 years from now?

.. ipython:: python

   print(ann.eq_val(20))