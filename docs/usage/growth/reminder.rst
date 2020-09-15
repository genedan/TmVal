========================
A Friendly Reminder
========================

.. meta::
   :description: Account and Accumulation functions can be initialized with a float object representing compound interest.
   :keywords: amount, accumulation, function, interest, interest theory, actuarial, python, package

If you have read the last couple sections on accumulation and amount functions, you may wonder why we have to define a growth function prior to defining an :class:`.Amount` or :class:`Accumulation` class. After all, this seems cumbersome and it would be more convenient to simply create an :class:`.Amount` or :class:`.Accumulation` class by specifying an interest rate.

The good news is, we can actually do this! All you have to do is supply a float object to either the :class:`.Amount` or :class:`.Accumulation` classes. Since compound annual interest is the most common scenario, these classes are defined to assume compound annual interest as the default case when supplied with a float. This reduces the amount of typing required by the user.

For example, if money grows at a compound rate of 5%, we can define an accumulation class with a single argument, and see what value it accumulates to after 5 years:

.. ipython:: python

   from tmval import Accumulation

   my_acc = Accumulation(gr=.05)

   print(my_acc.val(5))

If you want to be more explicit about the interest rate, both classes also accept a :class:`.Rate` object:

.. ipython:: python

   from tmval import Rate

   my_acc2 = Accumulation(gr=Rate(.05))

   print(my_acc2.val(5))

   gr=Rate(
      rate=.05,
      pattern="Effective Interest",
      interval=1
   )

   my_acc3 = Accumulation(gr=gr)

   print(my_acc3.val(5))

This also works with simple interest:

.. ipython:: python

   my_acc4 = Accumulation(gr=Rate(s=.05))

   print(my_acc4.val(5))

While it's possible to even define your own growth functions for simple and compound interest and supply them to the :class:`.Accumulation` and :class:`.Amount` classes, it's generally not recommended and it's more computationally efficient to use the :class:`.Rate` class unless you have a custom growth pattern, since more complex financial classes can use more efficient algorithms if they detect a :class:`.Rate` object instead of a function.