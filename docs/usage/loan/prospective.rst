==============================================
Outstanding Loan Balance - Prospective Method
==============================================

Another way to calculate the outstanding loan balance at a point in time is the :term:`prospective method`, which sums up the value of the remaining loan payments, discounted to that time period. Assuming compound interest, if the last payment is adjusted to avoid over/under payment, the outstanding loan balance calculated via the prospective method is defined as:

.. math::

   \text{OLB}_k = Q\ax{\angl{n-k-1} i} + R(1 + i)^{-(n-k)}.

If all the payments are equal, it is defined as:

.. math::

   \text{OLB}_k = Q\ax{\angl{n-k} i}.

The advantage of the prospective method is that we do not need to know the original loan amount.

Examples
==========

Suppose we need to make 10 end-of-year payments of 5,000 to pay off a loan. Assuming the rate of interest is 5% compounded annually, what is the outstanding loan balance immediately after the 5th payment?

We can solve this by using TmVal's :class:`.Loan` class. First, we define the loan by providing the characteristics in the preceding paragraph. Then, we call the method :func:`.Loan.olb_p` to execute the prospective method:

.. ipython:: python

   from tmval import Loan, Rate

   my_loan = Loan(
      pmt=5000,
      gr=Rate(.05),
      period=1,
      term=10
   )

   print(my_loan.olb_p(t=5))

Now, suppose we miss the 4th and 5th payment. What is the outstanding loan balance at time 5?

We can solve this by again calling the :func:`.Loan.olb_p`, and supplying the 4th and 5th payments as a list to the missing argument, ``missing=[4, 5]``:

.. ipython:: python

   print(my_loan.olb_p(t=5, missed=[4, 5]))