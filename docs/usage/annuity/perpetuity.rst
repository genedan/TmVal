==============
Perpetuities
==============

.. meta::
   :description: TmVal documentation on perpetuities.
   :keywords: annuity, perpetuity, formula, actuarial, python, package

A :term:`perpetuity` is a type of annuity that has an infinite number of payments. Perpetuities come in both :term:`immediate<perpetuity-immediate>` and :term:`due<perpetuity-due>` forms. For the former, the payments occur at the beginning of each period, whereas for the latter, they occur at the end of each period. A basic perpetuity (either :term:`immediate<basic perpetuity-immediate>` or :term:`due<basic perpetuity-due>`), is one that pays 1 for each period.

Like annuities, perpetuities have present value formulas that can be simplified to concise algebraic expressions. This fact can be proved via properties of infinite series. For a perpetuity-immediate:

.. math::

   \ax{\angl{\infty} i} = \frac{1}{i}

For a perpetuity-due:

.. math::

   \ax**{\angl{\infty} i} = \frac{1}{d}.

Unlike annuities, perpetuities do not have an accumulated value because the payments never end.

Examples
=========

Suppose we have a perpetuity-immediate that pays 1 at the end of each year, and the annual effective interest rate is 5%. What is the present value of the annuity?

We can solve this problem by using TmVal's :class:`.Annuity` class. In order to specify an infinite number of payments, we can set either the ``term`` or ``n`` argument to be infinite. We do so by importing `Numpy <https://numpy.org/>`_ and setting ``term=np.Inf`` or ``n=np.Inf``:

.. ipython:: python

   import numpy as np
   from tmval import Annuity, Rate

   ann = Annuity(
      term=np.Inf,
      gr=Rate(.05)
   )

   ann2 = Annuity(
      n=np.Inf,
      gr=Rate(.05)
   )

   print(ann.pv())
   print(ann2.pv())

For those who are unfamiliar with NumPy, NumPy is a scientific computing package that serves as the backbone of many other popular Python tools, such as Pandas (and hopefully someday, TmVal).
