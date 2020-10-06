========================
Time Value of Money
========================

.. meta::
   :description: TmVal documentation article on how to use Accumulation class discount function method to solve for present value.
   :keywords: time vale of money, present value, discount, interest rate, actuarial, python, package, principal

The time value of money is a phenomenon whereby the value of money changes with time. One reason why interest is required to facilitate lending is because people attach different values of money at different times. For example, if I needed to borrow money from my neighbor today, they would no longer have immediate use of the money. But money in the future may be worth less to the neighbor than money that they can use now.

Therefore, paying interest can be used to convince my neighbor to part with his money today, if he is confident that he will get the money back in the future along with the interest.

The value of money today of money to be received at some point in the future is called the :term:`present value`. The present value of :math:`L` to be received at time :math:`t` can be calculated by multiplying it by what we call the :term:`discount function`. We define the discount function as:

.. math::

   v(t) = \frac{1}{a(t)}

Where :math:`a(t)` is the accumulation function. This makes sense because if we were to invest :math:`Lv(t)` today, we would expect it to grow to :math:`Lv(t)a(t) = L` at time :math:`t`.

Example
=========

Suppose we will receive 5,000 at time 5. If the effective interest rate is 5%, how much is it worth today?

Since TmVal's :class:`.Accumulation` class comes with an :term:`accumulation function`, it also comes with a discount function. We can find the present value of 5,000 by passing it to the :meth:`.discount_func` method, along with the time indicating how far back we would like to discount the value.

.. ipython:: python

   from tmval import Accumulation

   my_acc = Accumulation(.05)

   pv = my_acc.discount_func(t=5, fv=5000)

   print(pv)

One neat thing TmVal can do is that it can find out how much you need to invest in the future to get a desired amount at an even later point in time. For example, if you wanted to make sure you had 10,000 at :math:`t_2 = 10`, how much do you need to invest at :math:`t_1 = 5` when the effective interest rate is 5%?

.. ipython:: python

   from tmval import Accumulation

   my_acc = Accumulation(.05)

   future_principal = my_acc.future_principal(t1=5, t2=10, fv=10000)

   print(future_principal)

You need to invest 7,835.26 5 years from now, to get 10,000 10 years from now.