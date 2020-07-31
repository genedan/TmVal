========================
Discount
========================

**Note:** This definition of :term:`discount` may differ from what you are used to in finance. If you typically use the terms **interest rate** and **discount rate** interchangeably, then stick with the interest rate operations in TmVal. If you encounter the term 'discount rate' in TmVal, please be aware that it refers to actuarial discount, discount interest, or interest up front.

For loans, sometimes, interest is paid up front. For example, if you were to take out a loan for $1000 to be repaid in 1 year, the lender may ask you to pay $100 immediately for use of the remaining $900. This value of $100 is known as the :term:`discount` on the loan.

Mathematically, discount be expressed as:

.. math::
   K - KD = (1-D)K,

Where :math:`K` is the amount of the loan, :math:`D` is the amount of discount, and :math:`(1-D)K` is the amount available to the borrower at time 0.

We can also think of discount as a rate. The effective discount rate over an interval :math:`[t_1, t_2]` is defined as:

.. math::
   d_{[t_1, t_2]} = \frac{a(t_2) - a(t_1)}{a(t_2)}.

When :math:`A_K(t) = Ka(t)`,

.. math::
   d_{[t_1, t_2]} = \frac{A_K(t_2) - A_K(t_1)}{A_K(t_2)}.

The discount rate for the :math:`n`-th time period is defined as:

.. math::
   d_n=\frac{a(n) - a(n-1)}{a(n)}

Examples
==========

Suppose we borrow $1000 to be paid back in 1 year, and we need to pay $100 of discount up front. What is the effective discount on the loan?


To solve this problem, we can use the ``discount_interval()`` method of the ``Amount`` class. TmVal also has a class called ``SimpleLoan`` which is a special case of money growth in which a lump sum is borrowed and paid back with a single payment at a later point in time. These loans are common between people outside the context of banking.

The ``SimpleLoan`` is callable, and can be passed to the ``Amount`` class just like a growth function.

To create a simple loan, supply the principal, term, and discount amount to ``SimpleLoan``. Then we can use ``discount_interval()`` to get the discount rate over the interval :math:`[0, 1]`:

.. ipython:: python

   from tmval import Amount, SimpleLoan

   my_loan = SimpleLoan(principal=1000, term=1, discount_amt=100)

   my_amt = Amount(f=my_loan, k=1000)

   print(my_amt.discount_interval(t1=0, t2=1))

Note that since the term is just one period, we can also simply this calculation by using the method ``effective_discount()``:

.. ipython:: python

   print(my_amt.effective_discount(n=1))

The ``SimpleLoan`` class also has some attributes that can be called to obtain information about the loan:

.. ipython:: python

   print(my_loan.principal)
   print(my_loan.discount_amt)
   print(my_loan.discount_rate)
   print(my_loan.amount_available)
