========================
Tiered Accounts
========================

.. meta::
   :description: Modeling tiered investment accounts with TmVal
   :keywords: amount, accumulation, function, tiered investment account, interest rate, actuarial, python, package

Recall that the amount and accumulation functions are often related by the property:

.. math::
   A_K(t) = Ka(t)

This is not always the case. An example where this relationship does not hold is the tiered investment account. A tiered investment account is one that offers different interest rates at different balances. For example, the following interest rate schedule determines what interest rate is paid according to the account balance:

.. rst-class:: right-align
.. table::
   :align: center

   +-------------------------+---------------+
   |Required Minimum Balance | Interest Rate |
   +=========================+===============+
   |0                        | 1%            |
   +-------------------------+---------------+
   |10,000                   | 2%            |
   +-------------------------+---------------+
   |20,000                   | 3%            |
   +-------------------------+---------------+

This means that the account pays 1% interest when the balance is less than 10,000. Once that balance grows to 10,000, the account starts paying 2%. When it hits 20,000, the account starts paying 3%.

Examples
==========

TmVal's :class:`.TieredBal` class offers a way to model this type of account. You simply supply the tiers and rates. Let's do this using the above table:

.. ipython:: python

   from tmval import TieredBal

   my_tiered_bal = TieredBal(
       tiers=[0, 10000, 20000],
       rates=[.01, .02, .03]
   )

:class:`.TieredBal` is a growth pattern that can be supplied to the :class:`.Amount` class, which you can then use to access its methods. If we invest 18,000 today, to what value does it grow after 10 years?

.. ipython:: python

   from tmval import Amount

   my_amt = Amount(gr=my_tiered_bal, k=18000)
   print(my_amt.val(10))

You can also use :class:`.TieredBal` to find the times at which you would expect the interest rate to jump, given an initial investment. We do this by calling the method :meth:`.get_jump_times()`. Assuming no future contributions, how long will it take to hit 2% and 3% interest?

.. ipython:: python

   print(my_tiered_bal.get_jump_times(k=5000))

It will take almost 70 years to reach 2%, and about 105 years to reach 3%. That's a long time!

TmVal also offers the :class:`.TieredTime` class, where the interest rate paid varies by the length of time the account is held:

.. rst-class:: right-align
.. table::
   :align: center

   +-------------------------+---------------+
   |Required Minimum Time    | Interest Rate |
   +=========================+===============+
   |0 years                  | 1%            |
   +-------------------------+---------------+
   |1 year                   | 2%            |
   +-------------------------+---------------+
   |2 years                  | 3%            |
   +-------------------------+---------------+

This means, the account pays 1% during the first year, 2% during the second year, and 3% for subsequent years. Let's model this in TmVal, and find out how much 18,000 grows after 10 years:

.. ipython:: python

   from tmval import TieredTime

   my_tiered_time = TieredTime(
       tiers=[0, 1, 2],
       rates=[.01, .02, .03]
   )

   my_amt = Amount(gr=my_tiered_time, k=18000)

   print(my_amt.val(10))