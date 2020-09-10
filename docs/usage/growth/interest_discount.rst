===============================
Interest-Discount Relationships
===============================

.. meta::
   :keywords: interest rate conversion, simple interest, simple discount, nominal interest, nominal discount, effective interest, effective discount, compound interest, compound discount, force of interest, conversions, python, package

The relationship between interest rates and discount rates can be expressed with a variety of equations. One thing to keep in mind is that if we borrow a dollar at time :math:`t_1` a discount rate of :math:`d`, we will receive :math:`(1-d)` dollars today.

If we were to hold invest that dollar for a year at the interest rate :math:`i`, it would grow to:

.. math::

   (1 -d)(1 + i) = 1.

This relationship can be generalized to apply between two time periods, :math:`t_1` and :math:`t_2`:

.. math::

   1 = (1 + i_{[t_1, t_2]})(1 - d_{[t_1, t_2]}).

In the age of hand calculations, several other equations have been useful:

.. math::

   i_{[t_1, t_2]} &= \frac{d_{[t_1, t_2]}}{1-d_{[t_1, t_2]}}\\

   d_{[t_1, t_2]} &= \frac{i_{[t_1, t_2]}}{1 + i_{[t_1, t_2]}}\\

   1 &= (1 + i_n)(1 - d_n)\\

   i_n &= \frac{d_n}{1 - d_n}\\

   d_n &= \frac{i_n}{1 + i_n} \\

   i &= \frac{d}{1-d} \\

   i &= \frac{1}{1-d} - 1 \\

   d &= \frac{i}{1 + i} \\

   d &= 1 - \frac{1}{1 + i}

Examples
=========

TmVal's :class:`.Rate` class provides a built-in method to convert interest rates to discount rates and vice-versa. These are simple functions, but are very useful as they tend to be embedded in more complex financial instruments.

Suppose the interest rate is 5%, what is the discount rate?

First, we define a compound effective rate using the :class:`.Rate` class. Then, we use the method :meth:`.convert_rate` to convert the rate to a discount rate:

.. ipython:: python

   from tmval import Rate

   i = Rate(.05)

   d = i.convert_rate(
      pattern='Effective Discount',
      interval=1
   )

   print(d)

Again using :meth:`.convert_rate()`, we can convert the discount rate back to an interest rate:

.. ipython:: python

   from tmval import Rate

   i = d.convert_rate(
      pattern='Effective Interest',
      interval=1
   )

   print(i)