===================
Equations of Value
===================

An equation of value is the valuation of a collection of cash flows at a desired point in time. Mathematically, the time :math:`\tau` equation of value is defined as:

.. math::

   \sum_{k}C_{t_k}\frac{a(\tau)}{a(t_k)} = B\frac{a(\tau)}{a(T)},

Where the Cs are the contributions, and B represents the accumulated value of the cash flows at time T. This concept is similar to net present value (NPV), except now we can take the value of the cash flows at any point in time. The NPV is the time :math:`\tau=0` equation of value.

Examples
=========

Suppose we have payments of 1,000, 2,000, 3,000, 4,000, and 5,000 occurring at times 1, 2, 3, 4, and 5. What is the time 5 equation of value?

To calculate the equation of value, simply call the :meth:`.eq_val` method of the :class:`.Payments` class and supply the argument ``t=5``.

.. ipython:: python

   from tmval import Payments

   pmts = Payments(
       amounts=[1000, 2000, 3000, 4000, 5000],
       times=[1, 2, 3, 4, 5],
       gr=.05)

   print(pmts.eq_val(t=5))

We can use the equation of value to calculate the valuation far out in to the future. What is the time 20 equation of value?

.. ipython:: python

   print(pmts.eq_val(t=20))

We can verify that the time 0 equation of value is equal to the NPV:

.. ipython:: python

   print(pmts.eq_val(t=0))

   print(pmts.npv())