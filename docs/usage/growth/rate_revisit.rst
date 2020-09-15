===============================
The Rate Class, Revisited
===============================

.. meta::
   :description: The Rate class is TmVal's class for representing interest rates.
   :keywords: interest rate, class, conversions, compound interest, effective interest, compound discount, effective discount, nominal interest, nominal discount, force of interest, simple interest, actuarial, python, package

Now that we have introduced several types of interest rates as well as the relationships between them, it's worth revisiting the :class:`.Rate` class to appreciate more of its features.

**Pattern**

The types of patterns that you can supply to the rate class are:

#. Effective Interest
#. Effective Discount
#. Nominal Interest
#. Nominal Discount
#. Force of Interest
#. Simple Interest
#. Simple Discount

**Interval**

Effective Interest, Effective Discount, Simple Interest, and Simple Discount are classified internally by TmVal as "effectives." When specifying an effective pattern, you must also supply an interval over which the rate is effective to the ``interval`` argument. This value is usually 1, representing a 1-year rate.

**Compounding Frequency**

Nominal Interest and Nominal discount are classified internally as the "nominals." When supplying a nominal pattern, you must also supply a compounding frequency to the argument ``freq``.

**Conversions**

Effective Interest, Effective Discount, Nominal Interest, Nominal Discount, and Force of Interest are classified as "compounds" and are convertible to each other.

Simple Interest and Simple Discount are classified as "simples" and are not convertible to each other because they do not correspond to the same accumulation function. You can however, use the :meth:`.convert_rate` method to change the interval of a simple pattern, but not the pattern itself.

Simple patterns cannot be converted to compound patterns and vice-versa.

**Standardization**

Many of the TmVal's classes, such as the previously-introduced :class:`.Amount` and :class:`.Accumulation` classes, as well as more complex financial instruments to be introduced later, such as the :class:`.Annuity` class, will standardize a compound rate prior to performing computations.

The :class:`.Rate` class has a method called :meth:`.standardize`, which will convert any compound pattern to an annually compounded effective interest rate.

**Shortcut Arguments**

Effective Interest, Effective Discount, Simple Interest, Simple Discount, and Force of Interest can be declared by providing a single arguments ``i``, ``d``, ``s``, ``sd``, and ``delta``, respectively. In the case of annual Effective Interest, the most common scenario by far, you do not have to use any keyword arguments at all. Simply calling ``Rate(.05)`` will declare an annually compounded interest rate of 5%.

Examples
=========

Suppose we have a continually compound interest rate of 5%, what is the equivalent nominal discount rate compounded 6 times per year?

.. ipython:: python

   from tmval import Rate

   fr = Rate(delta=.05)

   print(fr)

   nom_d = fr.convert_rate(
      pattern="Nominal Discount",
      freq=6
   )

   print(nom_d)

Let's see what happens when we call :meth:`.standardize`:

.. ipython:: python

   i = fr.standardize()

   print(i)

We get an annually compounded effective interest rate.