========================
Compound Interest
========================

:term:`Compound interest<compound interest>` is a pattern of money growth in which the value of money increases at a geometric rate:

.. math::

   a(t) = (1 + i)^2

where :math:`a(t)` refers to the value of 1 dollar (or other unit of currency) after time :math:`t`, at interest rate `i`. For example, $1 that grows at 5% simple interest is expected to grow to $1.1025 after 2 years:

.. math::

   a(1) = (1.05)^2 = 1.1025.

For quantities of money larger than dollar, we can express growth as:

.. math::

   A_K(t) = K(1 + i)^t

Where :math:`K` refers to the initial amount, or :term:`principal`. For example, if we start with $5 and an interest rate of 5%, it should grow to $5.5125 after two years:

.. math::

   A_K(1) = 5(1.05^2) = 5.5125

Examples
========================

Let's repeat the above examples using the TmVal package. Let's start by importing ``CompoundAmt``, which is a class that can be used for compound interest calculations:

.. ipython:: python

   from tmval import CompoundAmt

Let's see how much $1 grows to after 2 years, at an interest rate of 5%:

.. ipython:: python

   my_amt = CompoundAmt(k=1, i=.05)
   print(my_amt.val(2))

Now, let's change the principal to $5:

.. ipython:: python

   my_amt = CompoundAmt(k=5, i=.05)
   print(my_amt.val(2))


The output is 5.5125, the same as above.

TmVal also comes with a compound interest solver, ``compound_solver()``, that can be used to solve for missing inputs. For example, what rate of interest would give us $5.5125, if we held $5 for two years?

.. ipython:: python

   from tmval import compound_solver
   i = compound_solver(fv=5.5125, pv=5, t=2)
   print(i)