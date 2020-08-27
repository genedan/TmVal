=======================================
Perpetuities - Arithmetic Progression
=======================================

TmVal's :class:`.Annuity` class can also handle perpetuities with payments of increasing arithmetic progression:

.. math::

   (I_{P,Q}\ax{}){\angl{\infty} i} = P\ax{\angl{\infty} i} + \frac{Q}{i}{\angl{\infty} i} = \frac{P}{i} + \frac{Q}{i^2}

.. math::

   (I_{P,Q}\ax**{}){\angl{\infty} i} = P\ax**{\angl{\infty} i} + \frac{Q}{i}{\angl{\infty} i} = \frac{P}{d} + \frac{Q}{id}

Examples
=========

Suppose we have a perpetuity-immediate with an initial end-of-year payment of 100. Subsequent end-of-year payments increase 100 each year forever. If the interest rate is 5% compounded annually, what's the present value?

To solve this problem, we need the special value ``np.Inf`` from NumPy to specify an infinite term, passing ``term=np.Inf`` to TmVal's :class:`.Annuity` class.

.. ipython:: python

   import numpy as np

   from tmval import Annuity

   ann = Annuity(
      amount=100,
      gr=.05,
      term=np.Inf,
      aprog=100
   )

   print(ann.pv())

What if we have a perpetuity-due instead?

.. ipython:: python

   ann2 = Annuity(
      amount=100,
      gr=.05,
      term=np.Inf,
      aprog=100,
      imd='due'
   )

   print(ann2.pv())