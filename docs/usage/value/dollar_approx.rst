=======================================
Approximate Dollar-Weighted Yield Rate
=======================================

.. meta::
   :description: TmVal documentation on approximate dollar-weighted yield rate.
   :keywords: approximate dollar-weighted yield rate, dollar-weighted yield, actuarial, python, package

Sometimes, we would like to approximate the dollar-weighted yield rate. One such approximation is to set the investment term to 1:

.. math::

   j \approx \frac{I}{A + \sum_{t \in (0,1)} C_t (1-t)}

Where :math:`I` is the total interest earned, :math:`A` is the beginning balance, the Cs are the contributions, and the ts are contribution times as fractions of the unit investment time. We can further simplify things by assuming that each contribution happens at a constant time :math:`k` within the unit interval:

.. math::

   j \approx \frac{I}{A + C(1-k)}

Furthermore, if we assume :math:`k=1/2`, this once more simplifies to:

.. math::

   j \approx \frac{2I}{A + B - I}

Examples
=========

Suppose we make an investment of 10,000 at time 0 and 5,000 at time 1. If we withdraw 16,000 at time 2, what is the approximate dollar-weighted yield?

We can solve this problem by calling the :meth:`dw_approx()<tmval.value.Payments.dw_approx>` method of the :class:`.Payments` class:

.. ipython:: python

   from tmval import Payments

   pmts = Payments(
       amounts=[10000, 5000, -16000],
       times=[0, 1, 2]
   )

   print(pmts.dw_approx())

What if we use k-approximation? If we set ``k_approx=True``, k defaults to 1/2:

.. ipython:: python

   from tmval import Payments

   pmts = Payments(
       amounts=[10000, 5000, -16000],
       times=[0, 1, 2]
   )

   print(pmts.dw_approx(k_approx=True))

What if we set k=3/4?

.. ipython:: python

   from tmval import Payments

   pmts = Payments(
       amounts=[10000, 5000, -16000],
       times=[0, 1, 2]
   )

   print(pmts.dw_approx(k_approx=True, k=3/4))