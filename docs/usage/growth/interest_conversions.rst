==================================
Interest-Discount Rate Conversions
==================================

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

It would cumbersome to have to use over a dozen different functions to convert one rate to another. The good news is that TmVal offers a general conversion formula called :func:`.convert_rate` that can be used to convert any type of rate into any other type of rate.

This function can take a lot of arguments, but some guidelines to keep in mind are:

#. Supply a type of rate (i=, d=, nom_i=, nom_d=)
#. Supply a desired result, intdisc=, with valid values, 'interest' or 'discount'
#. Specify a desired result, effnom=, with valid values, 'effective' or 'nominal'
#. If 'nominal,' specify a compounding frequency, freq=
#. If 'effective,' specify a unit of time, interval=, which defaults to 1, which means annually effective.

Examples
=========

Suppose we have a nominal discount rate of :math:`d^{(12)} = .06` compounded monthly. What is the equivalent nominal interest rate compounded quarterly?

TmVal also comes with the class :class:`NominalDisc` to handle nominal discount rates, like :class:`NominalInt`, you supply the nominal rate and compounding frequency:

.. ipython:: python

   from tmval import convert_rate, NominalDisc

   nom_d = NominalDisc(dm=.06, m=12)

   nom_i = convert_rate(nom_d=nom_d, intdisc='interest', effnom='nominal', freq=4)

   print(nom_i)

Now, let's convert it to an annual effective interest rate:

.. ipython:: python

   i = convert_rate(nom_i=nom_i, intdisc='interest', effnom='effective')

   print(i)

Now, let's convert it back to a nominal discount rate compounded monthly:

.. ipython:: python

   nom_d2 = convert_rate(i=i, intdisc='discount', effnom='nominal', freq=12)

   print(nom_d2)