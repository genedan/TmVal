====================
Time-Weighted Yield
====================

.. meta::
   :description: TmVal documentation on time-weighted yield.
   :keywords: time weighted yield, time, weight, yield, actuarial, python, package

The time-weighted yield is a measure of how well a fund was managed. Mathematically, it is defined as:

.. math::

   j_tw = \left[\prod_{k=1}^{r+1} (1 + j_k) \right] - 1,

effective over the investment interval, where

.. math::

   1 + j_k = \begin{cases}
   \frac{B_{t_1}}{B_0} & k = 1\\
   \frac{B_{t_k}}{B_{t_{k-1}} + C_{t_{k-1}}} & k = 2, 3, \cdots, r+1
   \end{cases}.

The Bs represent the balances at points in time and the Cs represent the contributions. If we desire an annualized yield:

.. math::

   i_{tw} = (1 + j_{tw})^{\frac{1}{T}} -1 = \left[ \prod_{k=1}^{r+1} (1 + j_k)\right]^{\frac{1}{T}} - 1

Examples
=========

Suppose we deposit 100,000 in a bank account. It grows to 105,000 at time 1, and we immediately deposit an additional 5,000. It then grows to 115,000 at time 2. what is the time-weighted yield?

We can solve this problem by passing the balance amounts and times to the :meth:`time_weighted_yield<tmval.value.Payments.time_weighted_yield>` method of the :meth:`.Payments` class:

.. ipython:: python

   from tmval import Payments

   pmts = Payments(
      amounts=[100000, 5000],
      times=[0, 1]
   )

   i = pmts.time_weighted_yield(
      balance_times=[0, 1, 2],
      balance_amounts=[100000, 105000, 115000],
      annual=True
   )

   print(i)