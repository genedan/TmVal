==================
Introducing TmVal
==================

.. title::
   Introducing TmVal - a Python package for mathematical interest theory and time value of money computations

.. meta::
   :description: a Python package for mathematical interest theory and time value of money computations
   :keywords: financial mathematics, interest theory, annuities, time value of money, bonds, python, package
   :image property=og\:image: _static/tmval_logo.png



`TmVal <https://github.com/genedan/tmval>`_ is a Python library for mathematical interest theory, annuity, and bond calculations. This package arose from the need to have more powerful computational finance tools for another project of mine, `Miniature Economic Insurance Simulator (MIES) <https://github.com/genedan/MIES/>`_. What began as a simple submodule of MIES quickly spun off into its own repository as its complexity grew and as its potential viability in commercial applications became more apparent.

This article begins by highlighting the advantages TmVal has over existing time value of money packages, and then proceeds to demonstrate how TmVal can be used to solve problems found in actuarial science. Feel free to visit the project repository and examine its source code at https://github.com/genedan/tmval.

Feature Highlights
===================

- TmVal supports growth patterns that are more complex than compound interest. In addition to supporting simple, compound, and nominal interest, TmVal handles growth patterns that may be of theoretical interest to actuaries, such as continuously compounded rates (:ref:`force of interest <Force of Interest>`), polynomial growth, and arbitrary amount and accumulation functions.

..

- TmVal provides equations of value computations for core financial instruments in actuarial science, such as annuities, loans, and arbitrary cash flow streams. As development is still in the alpha stage, the types of investments TmVal supports is rapidly expanding. I expect the package to soon offer classes for bonds, stocks, and options.

..

- TmVal's classes are intended to correspond closely to symbols used in actuarial notation. Well-known symbols encountered by actuaries, such as :math:`\ax{\angln i}`, :math:`\sx**{\angln i}[(m)]`, :math:`(I_{P,Q}\ax**{}){\angln i}`, etc., are supported. Refer to the :ref:`Notation guide` in this documentation to see the available symbols.

Amount and Accumulation Functions
==================================

TmVal supports the core growth functions of mathematical interest theory, the :ref:`amount <Amount Functions>` (:math:`A_K(t)`) and :ref:`accumulation <Accumulation Functions>` (:math:`a(t)`)functions, implemented via the :class:`.Amount` and :class:`.Accumulation` classes. These classes support all sorts of growth patterns, from simple and compound interest to more complex cases such as tiered investment accounts and polynomial growth.

For instance, suppose we have the tiered investment account with annually compounded interest rates:

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

If we invest 18,000 today, to what value does it grow after 10 years?

.. ipython:: python

   from tmval import Amount, TieredBal

   tb = TieredBal(
       tiers=[0, 10000, 20000],
       rates=[.01, .02, .03]
   )

   amt = Amount(gr=tb, k=18000)
   print(amt.val(10))

If we were to invest 5,000 today, how long would it take to reach 2% and 3% interest, assuming no future contributions?

.. ipython:: python

   print(tb.get_jump_times(k=5000))

It will take almost 70 years to reach 2%, and about 105 years to reach 3%. That's a long time!

Interest Rate Conversions
==========================

Interest rates are represented by a core data type in TmVal, the :class:`.Rate` class. This custom data type offers a convenient way to perform computations with a variety of interest rate patterns as well as conversions between them. The main patterns supported by the :class:`.Rate` class are:

#. Effective Interest
#. Effective Discount
#. Nominal Interest
#. Nominal Discount
#. Force of Interest
#. Simple Interest
#. Simple Discount

The relationships between compound interest rates can be represented with the following expression:

.. math::

   \left(1 + \frac{i^{n}}{n}\right)^n = 1 + i = (1-d)^{-1} = \left(1 - \frac{d^{(p)}}{p}\right)^{-p}

Since there are so many varieties of rates, as well as relationships between them, an actuary would have to write over twenty conversion functions to handle the full spectrum of interest rates if they weren't using a package like TmVal. The good news is that TmVal handles all these conversions with a single method, :meth:`.Rate.convert_rate`.

For example, if we needed to convert 5% rate compounded annually to a nominal discount rate convertible monthly, we could do the following:

.. ipython:: python

   from tmval import Rate

   i = Rate(.05)

   nom_d = i.convert_rate(
       pattern="Nominal Discount",
       freq=12
   )

   print(nom_d)

Furthermore, we can demonstrate a conversion to nominal interest compounded quarterly, and then to :math:`\delta`, the force of interest, and then back to compound annual effective interest:

.. ipython:: python

   nom_i = nom_d.convert_rate(
       pattern="Nominal Interest",
       freq=4
   )

   print(nom_i)

   delta = nom_i.convert_rate(
       pattern="Force of Interest"
   )

   print(delta)

   i2 = delta.convert_rate(
       pattern="Effective Interest",
       interval=1
   )

   print(i2)

For more details, see :ref:`The Rate Class, Revisited` of the :ref:`Usage Tutorial`.

Equations of Value
===================

TmVal can solve for the time :math:`\tau` equation of value for common financial instruments such as annuities and loans, as well as for arbitrary cash flows. This is done via the :class:`.Payments` class:


.. math::

   \sum_{k}C_{t_k}\frac{a(\tau)}{a(t_k)} = B\frac{a(\tau)}{a(T)}.

For example, we can solve for the internal rate of return of an investment of 10,000 at time 0 which returns 5,000 at time 1 and 6,000 at time 2:

.. ipython:: python

  from tmval import Payments

  pmts = Payments(
      amounts=[-10000, 5000, 6000],
      times=[0, 1, 2]
  )

  # internal rate of return - two roots
  print(pmts.irr())

We can also use the :class:`.Payments` class to find the time-weighted yield:

.. math::

   i_{tw} = (1 + j_{tw})^{\frac{1}{T}} -1 = \left[ \prod_{k=1}^{r+1} (1 + j_k)\right]^{\frac{1}{T}} - 1

where

.. math::

   1 + j_k = \begin{cases}
   \frac{B_{t_1}}{B_0} & k = 1\\
   \frac{B_{t_k}}{B_{t_{k-1}} + C_{t_{k-1}}} & k = 2, 3, \cdots, r+1
   \end{cases}.

Suppose we deposit 100,000 in a bank account at time 0. It grows to 105,000 at time 1, and we immediately deposit an additional 5,000. It then grows to 115,000 at time 2. The time-weighted yield is:

.. ipython:: python

   pmts = Payments(
      amounts=[100000, 5000],
      times=[0, 1]
   )

   i = pmts.time_weighted_yield(
      balance_times=[0, 1, 2],
      balance_amounts=[100000, 105000, 115000],
      annual=True
   )

   # time-weighted yield
   print(i)

Annuities
==========

Annuities are one of the core financial instruments underlying life insurance products. TmVal provides support for many kinds of annuities via its :class:`.Annuity` class, such as:

#. Annuity-immediate: :math:`\ax{\angln i}`
#. Annuity-due: :math:`\ax**{\angln i}`
#. Perpetuity-immediate: :math:`\ax{\angl{\infty} i}`
#. Perpetuity-due: :math:`\ax**{\angl{\infty} i}`
#. Arithmetically increasing annuity-immediate: :math:`(I_{P, Q} a)_{\angln i}`
#. Arithmetically increasing annuity-due: :math:`(I_{P, Q} \ax**{})_{\angln i}`
#. Arithmetically increasing perpetuity-immediate: :math:`(I_{P, Q} a)_{\angl{\infty} i}`
#. Arithmetically increasing perpetuity-due: :math:`(I_{P, Q} \ax**{})_{\angl{\infty} i}`
#. Geometrically increasing annuity-immediate
#. Geometrically increasing annuity-due
#. Geometrically increasing perpetuity-immediate
#. Geometrically increasing perpetuity-due
#. Level annuity-immediate with payments more frequent than each interest period: :math:`\ax{\angln i}[(m)]`
#. Continuously-paying annuity: :math:`\ax*{\angln i}`

... and many more. To see what other symbols are supported, consult the :ref:`Notation Guide`.

Unlike other packages, which tend to use functions to represent the different types of annuities, TmVal represents annuities as a class, which gives it access to several methods that can be performed on the annuity, such as equations of value. So rather than simply returning a float value via a function, TmVal expands the manipulations that can be done with an annuity. My aim is to allow the :class:`.Annuity` class to serve as a base class for, or to be embedded into more complex insurance products.

We can perform simple calculations, such as finding the present value of a basic annuity-immediate, :math:`\ax{\angl{5} 5\%}`:

.. ipython:: python

   from tmval import Annuity

   print(Annuity(gr=.05, n=5).pv())

to more complex ones, such as the accumulated value of an arithmetically increasing annuity-due... :math:`(I_{5000, 100}\sx**{})_{{\angl{5} 5\%}}`:

.. ipython:: python

   ann = Annuity(
       amount=5000,
       gr=.05,
       n=5,
       aprog=100,
       imd='due'
   )

   print(ann.sv())

...or even the present value of continuously paying annuities with continually varying payments, such as this one at a simple discount rate of .036:

.. math::

   (\bar{I}\ax*{})_{\angln d_s=.036} = \int_0^5 tv(t)dt

.. ipython:: python

   def f(t):
       return t

   ann = Annuity(
       amount=f,
       period=0,
       term=5,
       gr=Rate(sd=.036)
   )

   print(ann.pv())

Amortization
=============

TmVal's :class:`.Loan` class has methods for obtaining information that we might want about loans, such as amortization schedules and outstanding loan balances.

The output for several TmVal's classes are intended to be compatible with `Pandas <https://pandas.pydata.org>`_, a popular data analysis library. The output for the :class:`.Loan` class's :meth:`amortization()<.Loan.amortization>` method is one such example.

For example, suppose we were to obtain a 2-year loan of 50,000, to be paid back with monthly payments made at the end of each month. If the interest rate were 4% convertible quarterly, what is the amortization schedule?

.. ipython:: python

   import pandas as pd
   from tmval import Loan, Rate

   gr = Rate(
       rate=.04,
       pattern="Nominal Interest",
       freq=4)

   my_loan = Loan(
       amt=50000,
       period=1/12,
       term=2,
       gr=gr,
       cents=True
   )

   amort = pd.DataFrame(my_loan.amortization())

   print(amort)

Using the :class:`.Loan` class's :meth:`.olb_r` method, we can calculate the outstanding loan balance at any time, such as after 1 year, using the :ref:`retrospective method <Outstanding Loan Balance - Retrospective Method>`:

.. math::

   \text{OLB}_k = La(k) - Q\sx{\angl{k}}

.. ipython:: python

   print(my_loan.olb_r(t=1))

Now, what if we choose to overpay during the first two months, with payments of 3,000 each, and then returning to normal payments? What is the outstanding loan balance after 1 year?

.. ipython:: python

   pmts = Payments(
       amounts=[3000] * 2 + [2170.06] * 10,
       times=[(x + 1) / 12 for x in range(12)]
   )

   print(my_loan.olb_r(t=1, payments=pmts))

Development Status
===================

TmVal is currently in the alpha stage of development. In the coming weeks, I expect to add many more features, such as:

#. Bonds
#. Stocks
#. Options
#. Immunization

I anticipate declaring the project to be in beta stage once I've incorporated all of the main concepts on the syllabus of the SOA's financial mathematics exam. The beta stage of the project will involve the construction of a testing suite to insure the accuracy of the computations in preparation for commercial use.

Further Reading
================

Go ahead and give TmVal a try! The next section is the :ref:`Installation and Quickstart` followed by the :ref:`Usage Tutorial`. For technical documentation, consult the :ref:`API Reference`, which links to the source code of the project.

If you encounter bugs, in TmVal or its documentation, feel free to create a `ticket <https://github.com/genedan/tmval/issues>`_ or `pull request <https://github.com/genedan/tmval/pulls>`_ on the `GitHub Repository <https://github.com/genedan/tmval>`_.