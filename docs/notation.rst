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

**Compound interest accumulation function:** :math:`a(t) = (1 + i)^t`

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

**Effective discount rate for the n-th time period:** :math:`d_n = \frac{a(n) - a(n-1)}{a(n)}`

.. code-block:: python

   Accumulation(gr).effective_discount(n)

**Discount function:** :math:`v(t) = \frac{1}{a(t)}`

.. code-block:: python

   Accumulation(gr).discount_func(t)

**Future principal:** :math:`Sv(t_2)a(t_1) = S\frac{a(t_1)}{a(t_2)} = S\frac{v(t_2)}{v(t_1)}`

.. code-block:: python

   Accumulation(gr).future_principal(fv=S, t1, t2)

**Simple discount amount function:** :math:`A_K(t) = \frac{K}{(1-dt)}`

.. code-block:: python

   Amount(gr=Rate(sd), k).val(t)

**Simple discount accumulation function:** :math:`a(t) = \frac{1}{(1-dt)}`

.. code-block:: python

   Accumulation(gr=Rate(sd), k).val(t)

**Nominal interest rate of** :math:`i^{(m)}` **convertible or compounded or payable** :math:`m` **times per year**

.. code-block:: python

   Rate(
       rate,
       pattern="Nominal Interest",
       freq=m)

**Nominal discount rate** :math:`d^{(m)}` **convertible or compounded or payable** :math:`m` **times per year**

.. code-block:: python

    Rate(
        rate,
        pattern="Nominal Discount",
        freq=m)

**Force of interest:** :math:`\delta = \lim_{m \to \infty} i^{(m)} = \ln(1+i)`

.. code-block:: python

   Rate(delta)

**Accumulation function under the force of interest:** :math:`a(t) = e^{\delta t}`

.. code-block:: python

   Accumulation(gr=Rate(delta))

**Time** :math:`\tau` **equation of value:** :math:`\sum_k C_{t_k}\frac{a(\tau)}{a(t_k)} = B\frac{a(\tau)}{a(T)}`

.. code-block:: python

   Payments(amounts, times, gr).eq_val(t)

**Equated time:** :math:`T=\frac{\ln\left(\frac{\sum_{k=1}^n C_{t_k} v^{t_k}}{C}\right)}{\ln v}`

.. code-block:: python

   Payments(amounts, times, gr).equated_time(c=C)


**Approximate dollar-weighted yield, k=1/2:** :math:`j \approx \frac{2I}{A + B - I}`

.. code-block:: python

   Payments(amounts, times, gr).dollar_weighted_yield(k_approx=True)

**Annual time-weighted yield rate:** :math:`i_{tw} = (1 + j_{tw})^{\frac{1}{T}} - 1 = \left[\prod_{k=1}^{r+1}(1 + j_k)\right]^{\frac{1}{T}} - 1`

.. code-block:: python

   Payments(amounts, times, gr).time_weighted_yield()

