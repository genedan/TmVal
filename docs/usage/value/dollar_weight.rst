======================
Dollar-Weighted Yield
======================

A common problem in finance is to calculate an interest rate that solves the time :math:`\tau` equation of value:

.. math::

   \sum_k C_{t_k} (1 + i)^{\tau-t_k} = B(1 + i)^{\tau - T}.

This interest rate is called the :term:`internal rate of return` (IRR), the :term:`yield rate` or the :term:`dollar-weighted yield rate`.

Not every equation of value has a yield rate, and when an equation of value has a yield rate, it is not guaranteed to be unique.

Examples
=========

Suppose we make an investment of 10,000. In return, we will receive 5,000 at the end of 1 year, and 6,000 at the end of two years. What is the internal rate of return?

We can solve this problem by declaring a :class:`.Payments` object and then calling the :meth:`irr()<tmval.value.Payments.irr>` method. If the equation of value happens to be a polynomial, TmVal will use a function from the `SciPy <https://www.scipy.org/>`_ package to calculate the roots. Otherwise, it will use `Newton's method <https://en.wikipedia.org/wiki/Newton%27s_method>`_.

.. ipython:: python

   from tmval import Payments

   pmts = Payments(
       amounts=[-10000, 5000, 6000],
       times=[0, 1, 2]
   )

   print(pmts.irr())

This equation of value happens to have two solutions. If we are to restrict ourselves to positive rates, the answer is 6.394%
