================================================
Outstanding Loan Balance - Retrospective Method
================================================

A common problem involving loans is calculating the outstanding loan balance at a point in time. One way to do this is called the :term:`retrospective method`, which first calculates the accumulated value of the principal, and then subtracts the accumulated value of the payments. The formula for the outstanding loan balance after the :math:`k\text{-th}` payment is thus:

.. math::

   \text{OLB}_k = La(k) - Q\sx{\angl{k}}

The main advantage of the retrospective method is that we do not need to know the term or the total number of payments required to settle the loan.

Examples
==========

Suppose we have borrowed 50,000 to be paid off with annual end-of-year payments of 5,000. If the interest rate is 5% compounded annually, what is the outstanding loan balance immediately after the 5th payment?

We can solve this problem with TmVal's :class:`.Loan` class, which is its main class for performing loan calculations. First, we need to define the loan by setting the arguments for the loan amount, ``amt=5000``, the payment amount, ``pmt=5000``, the payment period, ``period=1``, and the interest rate.

We can call the method :func:`.Loan.olb_r` to apply the retrospective method to find the balance at time ``t=5``:

.. ipython:: python

   from tmval import Loan, Rate

   my_loan = Loan(
      amt=50000,
      pmt=5000,
      period=1,
      gr=Rate(.05),
   )

   print(my_loan.olb_r(t=5))