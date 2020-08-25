===============
The Rate Class
===============

TmVal's :class:`.Rate` class is the central class for representing interest rates. Although we have only introduced two types of rates so far, simple and compound interest, we will shortly show that there are many different types of interest rates and ways to convert one rate to another. This introduces several complexities into the theory of interest, which motivated the need to create a special class to make life easier for the user.

To define a rate, we need to keep a few things in mind. If you are new to interest theory, you may not have encountered all of these concepts yet, but we will revisit them later once we've gone over nominal rates and the force of interest.

**Rate**
The magnitude of the rate, for example, the 5% in "5% compounded annually."

**Pattern**
A name used to describe whether the rate pertains to simple or compound interest, and whether it is nominal, effective or interest. For now, the only two patterns you have been introduced to are:

1. Simple Interest
2. Effective Interest (compound)

**Interval**
The interval over which the rate is effective. For example, if the rate is "5% compounded annually," the interval is 1. If it were effective every other year, then the interval would be 2. If it were effective over half a year then the interval would be .5.

**Compounding Frequency**
This refers to how often the interest is compounded for nominal rates, to be explored later. We don't have to think about it yet as this is not applicable to simple or compound effective interest.

Examples
==========

The interest rate is 5% compounded annually. Define this using the rate class.

To do this, we import TmVal's :class:`.Rate` class, and then supply the arguments. We set ``rate=.05``, ``pattern="Effective Interest"``, and ``interval=1``

.. ipython:: python

   from tmval import Rate

   gr = Rate(
      rate=.05,
      pattern="Effective Interest",
      interval=1
   )

   print(gr)

That's a lot of arguments to supply. Since compound interest is so common, there's a more convenient way to initialize a compound interest rate. We can supply this by setting a single argument ``i=.05`` or even just supplying the value ``.05`` without specifying any arguments. What happens is that the rest of the arguments are assumed to be that of compound annual interest.

.. ipython:: python

   gr2 = Rate(i=.05)

   print(gr2)

   gr3 = Rate(.05)

   print(gr)

We know just enough about compound interest to do some simple conversions. Instead of being effective over a 1-year interval, what if we had an equivalent rate effective over a two year interval? We can call the method :meth:`.convert_rate` and set the interval to two:

.. ipython:: python

   gr4 = gr3.convert_rate(
      pattern="Effective Interest",
      interval=2
   )

   print(gr4)

What about 5% simple interest that grows annually? As before, we can supply information to multiple arguments, or simple just set a single argument ``s=.05`` if we know the interval is 1 year (the most common case).

.. ipython:: python

   gr5 = Rate(
      rate=.05,
      pattern="Simple Interest",
      interval=1
   )

   print(gr5)

   gr6 = Rate(s=.05)

   print(gr6)

You may be wondering why we would need a separate class just for interest rates. In other Python finance packages, you just need to supply a float because usually the rate is assumed to be compound annual interest. However, in mathematical interest theory, there are many different types of interest rates, which makes things complicated if we want financial instruments such as annuities and bonds to handle all of these types of rates. You will see in the next few sections why it's more convenient to have a separate class for interest rates.

However, since compound annual interest prevails in the vast majority of applications, most of TmVal's classes and functions that take a rate object will assume compound annual interest if you supply a float object instead of a Rate object.