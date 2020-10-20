===========================================
Nonlevel Annuities - Arithmetic Progression
===========================================

.. meta::
   :description: TmVal documentation on annuities with payments in increasing arithmetic progression.
   :keywords: annuity, payment, increasing, arithmetic, progression, formula, equation, actuarial, python, package

TmVal's :class:`.Annuity` class can also handle annuities with increasing arithmetic progression. This means that if an annuity makes an initial payment :math:`P`, the next payment is :math:`P+Q`, and the payment after that is :math:`P+2Q`, and so on. The present value of such an annuity is:

.. math::

   (I_{P,Q}\ax{}){\angln i} = P\ax{\angln i} + \frac{Q}{i}(\ax{\angln i} - nv^n).

The accumulated value is:

.. math::

   (I_{P,Q}\sx{}){\angln i} = P\sx{\angln i} + \frac{Q}{i}(\sx{\angln i} - n).

The :class:`.Annuity` class can also handle the companion formulas for the annuity-due case:

.. math::

   (I_{P,Q}\sx**{}){\angln i} = P\sx**{\angln i} + \frac{Q}{d}(\sx{\angln i} - n),

and

.. math::

   (I_{P,Q}\ax**{}){\angln i} = P\ax**{\angln i} + \frac{Q}{d}(\ax{\angln i} - n).

For special cases :math:`(I\sx{}){\angln i}`, :math:`(I\ax{}){\angln i}`, :math:`(D\ax{}){\angln i}`, :math:`(I\sx**{}){\angln i}`, :math:`(D\ax**{}){\angln i}`, see the :ref:`Notation guide`.

Examples
=========

Suppose we have a 10-year annuity with an initial end-of-year payment of 100, and subsequent end-of-year payments increasing by 100 for each of the next 9 years. If the interest is 5% compounded annually, what is the present value?

We can solve this problem by setting the ``aprog`` argument of the :class:`.Annuity` class to ``aprog=100``:

.. ipython:: python

   from tmval import Annuity

   ann = Annuity(
       gr=.05,
       amount=100,
       n=10,
       aprog=100
   )

   print(ann.pv())

Now, suppose instead that the annuity makes beginning-of-year payments. What is the accumulated value?


.. ipython:: python

   ann2 = Annuity(
       gr=.05,
       amount=100,
       n=10,
       aprog=100,
   )

   print(ann2.sv())

The special cases mentioned earlier can be achieved by simply modifying the ``amount`` and ``aprog`` argument to be equal to the corresponding special case values. For more information on what these symbols mean and how to derive them, refer to a text on interest theory (some can be found in the :ref:`References` section).