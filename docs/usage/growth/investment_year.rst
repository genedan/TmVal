===============================
The Investment Year Method
===============================

.. meta::
   :description: TmVal documentation on the investment year method.
   :keywords: investment year method, actuarial, python, package

The investment year method is a growth pattern in which the rate of interest applicable to an investment varies by year and depends on the time at which that investment was made. The rates are taken from a table, which might look something like this:

.. rst-class:: right-align
.. table::
   :align: center

   +-------------------+----------------+----------------+----------------+----------------+---------------------+
   |Year of            | Rate in        | Rate in        | Rate in        | Rate in        | First Ultimate      |
   |Investment         | Year 1         | Year 2         | Year 3         | Year 4         | Rate                |
   +===================+================+================+================+================+=====================+
   |2000               |.06             |.065            |.0575           |.06             |.065                 |
   +-------------------+----------------+----------------+----------------+----------------+---------------------+
   |2001               |.07             |.0625           |.06             |.07             |.0675                |
   +-------------------+----------------+----------------+----------------+----------------+---------------------+
   |2002               |.06             |.06             |.0725           |.07             |.0725                |
   +-------------------+----------------+----------------+----------------+----------------+---------------------+
   |2003               |.0775           |.08             |.08             |.0775           |.0715                |
   +-------------------+----------------+----------------+----------------+----------------+---------------------+


To get the rates for an investment, you first identify the row using the leftmost column based on the year in which the investment was made, for each subsequent year, you move one column to the right until reaching the rightmost column. Each subsequent year after that, you move one column down.

For example, an investment made in the year 2000 and held for 7 years will have applicable rates of 6% in the first year, 6.5% in the second, 5.75% in the third, 6% in the fourth, 6.5% in the fifth, 6.75% in the sixth, and 7.25% in the seventh.


Examples
=========

Suppose we invest 1,000 in the year 2000. If the rates in the above table represent annually compounded rates, how much does the investment grow to after 7 years?

Note that this method exhibits the same growth pattern as TmVal's :class:`.TieredTime` class. We can use the function :func:`.tt_iym` to read the above table if is in the form of a Python dictionary. The function parses the table based on the year of investment ``t0=2000``, and then returns a :class:`.TieredTime` object. This object can then be passed to the :class:`.Amount` class along with the 1,000, which we can then use to calculate the answer.

.. ipython:: python

   from tmval import Amount, tt_iym

   iym_table = {
    2000: [.06, .065, .0575, .06, .065],
    2001: [.07, .0625, .06, .07, .0675],
    2002: [.06, .06, .0725, .07, .0725],
    2003: [.0775, .08, .08, .0775, .0715]
    }

    tt = tt_iym(table=iym_table, t0=2000)

    amt = Amount(gr=tt, k=1000)

    print(amt.val(7))