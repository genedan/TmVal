==================================
Interest-Discount Rate Conversions
==================================

.. meta::
   :description: Documentation for TmVal interest rate conversions.
   :keywords: interest rate conversion, simple interest, simple discount, nominal interest, nominal discount, effective interest, effective discount, compound interest, compound discount, force of interest, conversions, python, package

In addition to the concept of :term:`nominal interest<nominal interest rate>`, there's also :term:`nominal discount<nominal discount rate>`. In interest theory, various relationships between interest rates, discount rates, and their nominal counterparts can be derived:

.. math::

   d = 1 - \left(1 - \frac{d^{(m)}}{m}\right)^m \\

.. math::

   d^{(m)} = m[1-(1-d)^{\frac{1}{m}}] \\

.. math::

   1 = \left(1 - \frac{d^{(m)}}{m} \right) \left(1 + \frac{i^{(m)}}{m} \right) \\

.. math::

   0 = \frac{i^{(m)}}{m} - \frac{d^{(m)}}{m} - \frac{i^{(m)}}{m}\frac{d^{(m)}}{m} \\

.. math::
   \frac{i^{(m)}}{m} = \frac{\frac{d^{(m)}}{m}}{1 - \frac{d^{(m)}}{m}} \\

.. math::

   \frac{d^{(m)}}{m} = \frac{\frac{i^{(m)}}{m}}{1 + i^{(m)}{m}} \\

.. math::

   \left(1 + \frac{i^{n}}{n}\right)^n = 1 + i = (1-d)^{-1} = \left(1 - \frac{d^{(p)}}{p}\right)^{-p}

It would cumbersome to have to use over a dozen different functions to convert one rate to another. Fortunately, the method :meth:`.convert_rate` of the :class:`.Rate` class allows us to convert between any of these rates. Now, you can see why it's useful to have interest rates represent by a custom data type, rather than a float object.

To a convert a rate from one pattern to another, take the following steps:

#. Supply a desired pattern to convert to ('Effective Interest', 'Effective Discount, 'Nominal Interest', 'Nominal Discount')
#. If the desired pattern is nominal, supply a compounding frequency
#. If the desired pattern is an effective interest or discount rate, supply a desired interval


Examples
=========

Suppose we have a nominal discount rate of :math:`d^{(12)} = .06` compounded monthly. What is the equivalent nominal interest rate compounded quarterly?

.. ipython:: python

   from tmval import Rate

   nom_d = Rate(
       rate=.06,
       pattern="Nominal Discount",
       freq=12
   )

   print(nom_d)

   nom_i = nom_d.convert_rate(
       pattern="Nominal Interest",
       freq=4
   )

   print(nom_i)

Now, let's convert it to an annual effective interest rate:

.. ipython:: python

   i = nom_i.convert_rate(
       pattern="Effective Interest",
       interval=1
   )

   print(i)

Now, let's convert it back to a nominal discount rate compounded monthly:

.. ipython:: python

   nom_d2 = i.convert_rate(
       pattern="Nominal Discount",
       freq=12
   )

   print(nom_d2)
