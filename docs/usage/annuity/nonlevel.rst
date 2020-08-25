===================
Nonlevel Annuities
===================

Sometimes annuities involves nonlevel payments that do not correspond to a standard annuity symbol. In this case, TmVal's :class:`.Annuity` class defaults to using methods from its parent class, :class:`.Payments`.

Examples
==========

Suppose we have an annuity that makes end-of-year payments of 2000, 5000, 1000, 4000, and 8000. If interest is governed by a compound annual effective rate of 5%, how much does this annuity cost today?

To solve this problem, simply supply the payment stream to the ``amount`` argument, ``amount[2000, 5000, 1000, 4000, 8000], and payment times to the ``times`` argument, much like we would with the :class:`.Payments` class:

.. ipython:: python

   from tmval import Annuity, Rate

   pmts = [2000, 5000, 1000, 4000, 8000]
   times = [x + 1 for x in range(5)]
   ann = Annuity(
      amount=pmts,
      times=times,
      gr=Rate(.05)
   )

   print(ann.pv())

How much is this annuity worth at time 3?

.. ipython:: python

   print(ann.eq_val(3))
