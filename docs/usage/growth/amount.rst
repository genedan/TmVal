========================
Amount Functions
========================

Although we have introduced the familiar cases of simple and compound interest, not all growth patterns are linear or geometric. Sometimes a growth pattern might be geometric, cubic, or some arbitrary user-defined pattern.

To accommodate these new patterns, we can define an :term:`amount function`, which specifies how money grows for an arbitrary growth pattern:

.. math::
   A_K(t)

Where :math:`K` specifies the amount of principal, :math:`t` specifies the amount of time, and :math:`A_K(t)` returns the value at time :math:`t` of :math:`K` invested at time 0.

Examples
========================

Suppose money exhibits a quadratic growth pattern, specified by the amount function:

.. math::
   A_K(t) = K(.05t^2 + .05t + 1)

If we invest :math:`K=5` at time 0, how much does it grow to at time 5?

TmVal's ``Amount`` class allows us to model this behavior. To solve the above problem, simply call the class and supply the growth function and principal. First, define the growth function as a Python function that takes the time and principal as arguments:

.. ipython:: python

   from tmval import Amount

   def f(t, k):
       return k * (.05 * (t **2) + .05 * t + 1)

Now supply the growth function to the ``Amount`` class, and call :code:`my_amt.val(5)` to get the answer:

.. ipython:: python

   my_amt = Amount(gr=f, k=5)

    print(my_amt.val(5))