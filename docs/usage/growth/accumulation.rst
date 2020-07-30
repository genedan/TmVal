========================
Accumulation Functions
========================

The accumulation function is a special case of the amount function where :math:`K=1`:

.. math::
   a(t) = A_1(t)

It is often convenient to use this form to explore the growth of money without having to bother with the principal.

The amount and accumulation functions are often related by the following expression:

.. math::
   A_K(t) = Ka(t)


Examples
========================

TmVal's **Accumulation** class models accumulation functions.

Suppose money exhibits a quadratic growth pattern, specified by the amount function:

.. math::
   a(t) = .05t^2 + .05t + 1

How much does $1 invested at time 0 grow to at time 5? To solve this problem, we import the Accumulation class, supply the growth function in a similar manner as we had done with the Amount class, except we do not need to supply a value for :math:`K`.

.. ipython:: python

   from tmval import Accumulation

   def f(t):
       return .05 * (t **2) + .05 * t + 1

   my_acc = Accumulation(f=f)

    print(my_acc.val(5))

Note that we could have also solved this problem with the Amount class, by setting :math:`K=1`.

.. ipython:: python

   from tmval import Amount

   def f(t, k):
       return k * (.05 * (t **2) + .05 * t + 1)

   my_amt = Amount(f=f, k=1)

   print(my_amt.val(5))

If the amount and accumulation functions are proportionally related, we can extract the accumulation function from the Amount class by calling the **get_accumulation()** method, which returns an Accumulation class derived from the Amount class:

.. ipython:: python

   from tmval import Amount

   def f(t, k):
       return k * (.05 * (t **2) + .05 * t + 1)

   my_amt = Amount(f=f, k=1)

   my_acc = my_amt.get_accumulation()

   print(my_acc.val(5))


