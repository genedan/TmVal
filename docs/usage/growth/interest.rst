========================
Interest
========================

Suppose we invest :math:`K` at time 0. We define the amount of :term:`interest earned` between times :math:`t_1` and :math:`t_2` as:

.. math::

   A_K(t_2) - A_K(t_1).

We define the :term:`effective rate of interest` for the interval as:

.. math::

   i_{[t_1, t_2]} = \frac{a(t_2) - a(t_1)}{a(t_1)}

and, if :math:`A_K(t) = Ka(t)`,

.. math::
   i_{[t_1, t_2]} = \frac{A_K(t_2) - A_K(t_1)}{A_K(t_1)}.

To examine the effective interest rate for a single time period, the :math:`n`-th time period, we can define:

.. math::

   i_n = i_{[n-1, n]} = \frac{a(n) - a(n - 1)}{a(n - 1)}

Examples
========================

We can use the ``Amount`` class to make various interest calculations. For example, assume the following amount function:

.. math::
   A_K(t) = K(.02t^2 + .02t + 1)

If we invest $5 at time 0, What is the interest earned during the 5th time period?

First lets set up our ``Amount`` instance:

.. ipython:: python

   from tmval import Amount

   def f(t, k):
       return k * (.02 * (t **2) + .02 * t + 1)

   my_amt = Amount(f=f, k=5)

We can use the ``Amount`` class's ``interest_earned()`` method to get the answer:

.. ipython:: python

   interest = my_amt.interest_earned(t1=4, t2=5)

   print(interest)

What is the effective interest rate during the 5th time period? We can use the ``Amount`` class's ``effective_rate()`` method to get the answer:

.. ipython:: python

   eff_interest_rate_amt = my_amt.effective_rate(n=5)

   print(eff_interest_rate_amt)

We can also use the ``effective_interval()`` method to find the effective rate over a longer interval, say from times 1 to 5:

.. ipython:: python

   eff_interval_rate_amt = my_amt.effective_interval(t1=1, t2=5)

   print(eff_interval_rate_amt)

TmVal's ``Accumulation`` class is a subclass of the ``Amount`` class. This means that many of the methods that can be used from the ``Amount`` class can also be used by the ``Accumulation`` class.

Assuming proportionality, we can define an amount function from an accumulation function and then get the effective interest rate for the 5th interval. It should be the same answer as that achieved from the amount function:

.. ipython:: python

   import math

   my_acc = my_amt.get_accumulation()

   eff_interest_rate_acc = my_acc.effective_rate(n=5)

   print(eff_interest_rate_acc)

   print(math.isclose(eff_interest_rate_acc, eff_interest_rate_amt, rel_tol=.0001))

Note that there is some loss of precision due to floating point operations, so we use ``isclose()`` from the ``math`` library for the comparison.