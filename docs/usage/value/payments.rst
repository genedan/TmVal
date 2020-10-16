===================
The Payments Class
===================

.. meta::
   :description: TmVal documentation on payments class.
   :keywords: payment, payments, net present value, npv, present value, python net present value formula, python npv formula, actuarial, python, package

TmVal offers a :class:`.Payments` class, which is exactly what you think it is, a collection of transfers of money from one entity to another. Since we don't really care who is getting what at the moment, a :class:`.Payments` object in TmVal is simply a collection of payment amounts, payment times, and a growth rate object.

The growth rate object can be a float, in which case we assume compound effective interest. You can also provide a :class:`.Rate` object for other interest patterns, including compound effective interest. It can also be an Accumulation object, which gives you an option if the growth pattern you want to model is more complex.

While simple, :class:`.Payments` constitutes a core data type in TmVal. It is used, along with the fundamentals of interest theory that we have developed so far, to construct more complex financial instruments and transactions, such as :class:`annuities<.Annuity>` and :class:`loans<.Loan>`.

Examples
========

Suppose we have payments of 1,000, 2,000, and 3,000 that occur at times 1, 2, and 3, respectively. If we have 5% compound interest, construct a :class:`.Payments` object and explore its contents.

To declare a :class:`.Payments` class, pass the payment amounts, times, and interest rate to the arguments ``amounts``, ``times``, and ``gr``, respectively. Let's use ``dir`` to see what attributes and methods we can explore.

.. ipython:: python

   from tmval import Payments

   pmts = Payments(amounts=[1000, 2000, 3000], times=[1, 2, 3], gr=.05)

   dir(pmts)

First, we notice the amounts and times we provided to the object. We also see some methods such as :meth:`.npv()`, :meth:`.eq_val`, :meth:`.irr()`, :meth:`.dollar_weighted_yield`, and :meth:`.time_weighted_yield`, which we'll explore in the subsequent sections.

Note that we can also supply an :class:`.Accumulation` or :class:`.Rate` object to the argument ``gr``. The following declarations are equivalent to the previous one:

.. ipython:: python

   from tmval import Accumulation, Rate

   pmts = Payments(amounts=[1000, 2000, 3000], times=[1, 2, 3], gr=Accumulation(.05))

   pmts = Payments(amounts=[1000, 2000, 3000], times=[1, 2, 3], gr=Rate(.05))

This might seem superficial at first glance, but its usefulness becomes apparent if we have something more complicated than compound interest, such as :math:`a(t) = x^5 + 3x^4 + 2x + 4`

.. ipython:: python

   def f(t):
       return t ** 5 + 3 * t ** 4 + 2 * t + 4

   pmts = Payments(amounts=[1000, 2000, 3000], times=[1, 2, 3], gr=Accumulation(gr=f))