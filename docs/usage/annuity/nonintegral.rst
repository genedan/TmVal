==================
Nonintegral Terms
==================

.. meta::
   :description: TmVal documentation annuities with nonintegral terms.
   :keywords: annuity, nonintegral, integral, non-integral, term, formula, actuarial, python, package

Sometimes, certain payment structures will not yield an integral number of payments for a desired present value. For example, suppose we were to take out a loan for 10,000 at 5% interest compounded annually. If we were to pay 1,000 per year to settle the loan, solving the equation :math:`L=Q\ax{\angl{r} i}` for :math:`r` will not result in an integer. Specifically, the formula for solving r is:

.. math::

   r = -\frac{\ln\left(1-\frac{iL}{Q}\right)}{\ln(1 + i)},

and for our example, :math:`r \approx 14.207` years.

This is problematic if we want the final payment to coincide with the payment period. Two ways to adjust for this are to have the final payment occur on the next or previous integral period. For example, in our example, we can have the final payment occur at time 15 or time 14. We then adjust the final payment for the appropriate time value of money so that the present value of payments equals the present value of the loan.

If the payment is rolled forward to the next period, this payment is called the :term:`drop payment`. When rolled backwards and added to the previous payment, it is called the :term:`balloon payment`.

The drop payment is equal to:

.. math::

   Q\left(\frac{(1 + i)^f - 1}{i}\right)(1 + i)^{1-f},

and the balloon payment is equal to:

.. math::

   Q + Q\left(\frac{(1 +i)^f - 1}{i}\right)v^f.

Example
=========

Suppose we borrow 10,000 at 5% compound annual interest, and repay it by making end-of-year payments of 1,000. If we elect to have the final payment be a drop payment, how much is the payment, and what time does it occur on?

To solve this problem, we can set the ``loan`` and ``drb`` arguments of the :class:`.Annuity` class to their appropriate values. The ``drb`` argument specifies whether we want a drop or balloon payment. We can then check the drop payment using the ``drb_pmt`` attribute.

To check the time of the last payment, we can use the ``times`` attribute of the :class:`.Annuity` object and pass it to the ``max`` function to get the result.

.. ipython:: python

   from tmval import Annuity

   ann = Annuity(
       loan=10000,
       amount=1000,
       gr=.05,
       drb='drop'
   )

   # drop payment amount
   print(ann.drb_pmt)

   # drop payment time
   print(max(ann.times))

To get confidence, let's confirm that the present value is equal to 10,000:

.. ipython:: python

   print(ann.pv())

What if we elect the final payment to be a balloon payment? What is the amount, and when does it occur?

.. ipython:: python

   ann2 = Annuity(
       loan=10000,
       amount=1000,
       gr=.05,
       drb='balloon'
   )

   # drop payment amount
   print(ann2.drb_pmt)

   # drop payment time
   print(max(ann2.times))

   # again, check the pv
   print(ann2.pv())