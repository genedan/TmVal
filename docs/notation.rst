===============
Notation Guide
===============

TmVal is intended to provide a more natural connection to actuarial notation than other time value of money packages from general areas of finance. By providing the main actuarial financial instruments as classes, TmVal makes it easier to represent and manipulate them in ways that more easily match actuarial theory.

This guide shows how common actuarial symbols can be replicated in TmVal. These are written in pseudocode and not meant to be executed directly, and serve as a guide as to what classes and functions correspond to which symbols.

**Amount function:** :math:`A_K(t)`

.. code-block:: python

   Amount(gr, k).val(t)

**Accumulation function:** :math:`a(t)`

.. code-block:: python

   Accumulation(gr).val(t)


**Effective interest rate for the interval:** :math:`i_{[t_1, t_2]} = \frac{a(t_2)-a(t_1)}{a(t_1)}`

.. code-block:: python

   Accumulation(gr).effective_interval(t1, t2)

or, assuming proportionality:

.. code-block:: python

   Amount(gr, k).effective_interval(t1, t2)

**Effective interest for the n-th time period:** :math:`i_n = \frac{a(n) - a(n-1)}{a(n-1)}`

.. code-block:: python

   Amount(gr, k).effective_rate(n)

**Simple interest amount function:** :math:`A_K(t) = K(1 + st)`

.. code-block:: python

   Amount(gr=Rate(s), k).val(t)

.. Compound interest accumulation function:** :math:`a(t) = (1 + i)^t`

.. code-block:: python

   Accumulation(gr=Rate(i)).val(t)

or

.. code-block:: python

   Accumulation(gr=i).val(t)

**Effective discount rate for the interval:** :math:`d_{[t1, t2]} = \frac{a(t_2) - a(t_1)}{a(t_2)}`

.. code-block:: python

   Accumulation(gr).discount_interval(t1, t2)

or, assuming proportionality:

.. code-block:: python

   Amount(gr, k).discount_interval(t1, t2)

**Effective discount rte for the n-th time period:** :math:`d_n = \frac{a(n) - a(n-1)}{a(n)}`

.. code-block:: python

   Accumulation(gr).effective_discount(n)

**Discount function:** :math:`v(t) = \frac{1}{a(t)}`

.. code-block:: python

   Accumulation(gr).discount_func(t)

**Future principal:** :math:`Sv(t_2)a(t_1) = S\frac{a(t_1)}{a(t_2)} = S\frac{v(t_2)}{v(t_1)}`

.. code-block:: python

   Accumulation(gr).future_principal(fv=S, t1, t2)

