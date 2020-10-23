===============================
General Accumulation Functions
===============================

.. meta::
   :description: TmVal documentation on using general accumulation functions with annuities
   :keywords: annuity, accumulation, general accumulation, accumulation function, function, formula, actuarial, python, package


The annuities supported by TmVal need not be limited to the main growth patterns supported by the :class:`.Rate` class. TmVal can also handle annuities governed by more complex growth patterns, such as polynomial growth.

Examples
==========

Suppose we have a basic, 5-year term annuity-immediate governed by the following growth pattern:

.. math::

   a(t) = .05t^2 + .02t + .03

What is the present value of the annuity?

We can solve this problem by defining a function for the quadratic growth pattern and then passing it to the :class:`.Accumulation` class, which in turn is passed to the :class:`.Annuity` class:

.. ipython:: python

   from tmval import Accumulation, Annuity

   def f(t):
       return .05 * t ** 2 + .02 * t + 1


   ann = Annuity(gr=Accumulation(gr=f), n=5)

   print(ann.pv())

What is the accumulated value?

.. ipython:: python

   print(ann.sv())