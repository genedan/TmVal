========================
A Friendly Reminder
========================

If you have read the last couple sections on accumulation and amount functions, you may wonder why we have to define a growth function prior to defining an Amount or Accumulation class. After all, this seems cumbersome and it would be more convenient to simply create an Amount or Accumulation class by specifying an interest rate.

The good news is, we can actually do this! If you recall at the beginning of the tutorial, TmVal provided a pair of classes called :code:`CompoundAmt` and :code:`CompoundAcc`. These are subclasses of the Amount and Accumulation classes, respectively, and can be called without having to specify a separate growth function, and have access to the methods in their parent classes.

For example, if money grows at a compound rate of 5%, we can define an accumulation class with a single argument, and see what value it accumulates to after 5 years:

.. ipython:: python

   from tmval import CompoundAcc

   my_acc = CompoundAcc(i=.05)

   print(my_acc.val(5))

In the case of simple interest, TmVal offers the companion classes, :code:`SimpleAmt` and :code:`SimpleAcc`.

The :code:`Amount` and :code:`Accumulation` classes are for generalized cases that cannot be handled by the compound and simple classes. In these cases, you can define your own growth pattern.