========================
Simple Interest
========================
:term:`Simple interest<simple interest>` is a pattern of money growth in which the value of money increases at a linear rate:

.. math::

   a(t) = 1 + st

where :math:`a(t)` refers to the value of 1 dollar (or other unit of currency) after time :math:`t`, at interest rate `s`. For example, $1 that grows at 5% simple interest is expected to grow to $1.05 after 1 year:

.. math::

   a(1) = 1 + (.05)(1) = 1.05.

For quantities of money larger than dollar, we can express growth as:

.. math::

   A_K(t) = K(1 + st)

Where :math:`K` refers to the initial amount, or :term:`principal`. For example, if we start with $5 and an interest rate of 5%, it should grow to $5.25 after one year:

.. math::

   A_K(1) = 5(1 + (.05)(1)) = 5.25

Examples
========================

Let's repeat the above examples using the TmVal package. Let's start by importing ``SimpleAmt``, which is a class that can be used for simple interest calculations:

.. ipython:: python

   from tmval import SimpleAmt

Let's see how much $1 grows to after 1 year, at an interest rate of 5%:

.. ipython:: python

   my_amt = SimpleAmt(k=1, s=.05)
   print(my_amt.val(1))


Now, let's change the principal to $5:

.. ipython:: python

   my_amt = SimpleAmt(k=5, s=.05)
   print(my_amt.val(1))

The output is 5.25, the same as above.

TmVal also comes with a simple interest solver, ``get_simple_amt()`` that can be used to solve for missing inputs. For example, what rate of interest would give us $5.25, if we held $5 for a year?

.. ipython:: python

   from tmval import get_simple_amt
   my_amt = get_simple_amt(fv=5.25, pv=5, n=1)
   print(my_amt.interest_rate)