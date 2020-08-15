=========
Payments
=========

TmVal offers a :class:`.Payment` class, which is exactly what you think it is, a transfer of money from one person to another. Since we don't really care who is getting what at the moment, a :class:`.Payment` in TmVal is simply a collection of a payment amount, a time of payment, and a discount rate, with the discount rate being optional to model undiscounted payments.

While simple, payments constitute a core data type in TmVal, they are used, along with the fundamentals of interest theory that we have developed so far, to construct more complex financial instruments and transactions.

Examples
========

To construct a payment, simply call the :class:`.Payment` class and supply a payment amount, a payment time, and optionally, a discount factor.

For example, we can declare a :class:.`Payment` that has a payment amount of 1000, occurs at time t=5, and has a discount factor of .8.


..
   from tmval import Payment

   my_payment = Payment(amount=1000, time=5, discount_factor=.8)

We can also retrieve the payment information by calling its members:


..
   print(my_payment.amount)
   print(my_payment.time)
   print(my_payment.discount_factor)

We can also construct payments more quickly by using the :func:`.create_payments` function. You can do so by supplying a list of payment amounts, a list of payment times, and a list of discount factors:



..
   from tmval import create_payments

   my_payments = create_payments(
     amounts = [1000, 2000, 3000],
     times = [1, 2, 3],
     discount_factors = [.8, .9, .95]
   )

There are many ways to supply discounting to :func:`.create_payments`. In addition to supplying a list of discount rates, you can also supply a discount function:


..
   from tmval import CompoundAcc

   my_acc = CompoundAcc(i=.05)

   my_func = my_acc.discount_func

   more_payments = create_payments(
     amounts = [1000, 2000, 3000],
     times = [1, 2, 3],
     discount_func=my_func
   )

Or, you can simply supply the :class:`.Accumulation` object directly:


..
   even_more_payments = create_payments(
     amounts = [1000, 2000, 3000],
     times = [1, 2, 3],
     discount_func=my_func
   )

Furthermore, if interest is compounded, then you can just supply the interest rate:


..
   yet_even_more_payments = create_payments(
     amounts = [1000, 2000, 3000],
     times = [1, 2, 3],
     interest_rate=.05
   )
