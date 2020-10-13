=============
Equated Time
=============

.. meta::
   :description: TmVal documentation on the method of equated time.
   :keywords: equated time, actuarial, python, package


Suppose we have a series of contributions :math:`C_{t_k}` for :math:`k=1, 2, \ldots, n`. The method that solves for :math:`T` such that a single payment of :math:`C=\sum_{k=1}^n C_{t_k}` at time :math:`T` has the same value at :math:`t=0` as the sequence of :math:`n` contributions is known as the method of equated time.

Examples
=========

Suppose we are are repaying a loan with payments of 5,000 after 5 years, 10,000 after 10 years, and 15,000 after 15 years. If we desire to replace these payments with a single payment of 30,000, such that its present value equals the present value of the original payment plan, at what time must we make this payment? Assume the interest rate is 5% compounded annually.

We can solve this problem using the :meth:`.equated_time` method of the :class:`.Payments` class. Declare a :class:`.Payments` object with the original stream of payments and then pass `c=30000` to the :meth:`.equated_time` method.

.. ipython:: python

   from tmval import Payments

   pmts = Payments(
       amounts=[5000, 10000, 15000],
       times=[5, 10, 15],
       gr=.05
   )

   t = pmts.equated_time(c=30000)

   print(t)