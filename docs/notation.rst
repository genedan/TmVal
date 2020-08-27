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

**Present value of basic annuity-immediate:** :math:`\ax{\angln i}`

.. code-block:: python

   Annuity(gr=i, n).pv()

**Accumulated value of basic annuity-immediate:** :math:`\sx{\angln i}`

.. code-block:: python

   Annuity(gr=i, n).sv()

**Loan payment, level:** :math:`Q=\frac{L}{\ax{\angln i}}`

.. code-block:: python

   get_loan_pmt(
       loan_amt=L,
       period,
       term,
       gr=Rate(i))

**Savings payment to obtain accumulated balance:** :math:`Q=\frac{B}{\sx{\angln i}}`

.. code-block:: python

   get_savings_pmt(
       fv=B,
       period,
       term,
       gr=Rate(i)
   )

**Present value of basic annuity-due:** :math:`\ax**{\angln i}`

.. code-block:: python

   Annuity(
       gr=i,
       n=n,
       imd='due'
   ).pv()

**Accumulated value of basic annuity-due:** :math:`\sx**{\angln i}`

.. code-block:: python

   Annuity(
       gr=i,
       n=n,
       imd='due'
   ).sv()

**Present value of basic perpetuity-immediate:** :math:`\ax{\angl{\infty} i}`

.. code-block:: python

   Annuity(
       gr=i,
       term=np.Inf,
   ).pv()

**Present value of basic perpetuity-due:** :math:`\ax**{\angl{\infty} i}`

.. code-block:: python

   Annuity(
       gr=i,
       term=np.Inf,
       imd='due'
   ).sv()

**Present value of deferred annuity-immediate:** :math:`\ax[w|n]{}`

.. code-block:: python

   Annuity(
       gr,
       n=n,
       deferral=w
   ).pv()

**Present value of deferred annuity-due:** :math:`\ax**[w|n]{}`

.. code-block:: python

   Annuity(
       gr,
       n=n,
       deferral=w,
       imd='due'
   ).pv()

**Outstanding loan balance, retrospective method:** :math:`\text{OLB}_k = La(k) - Q\sx{\angl{k}}`

.. code-block:: python

   Loan(
       amt=L,
       pmt=Q,
       gr,
       period,
       term
   ).olb_r()

**Outstanding loan balance, prospective method (adjusted final payment):** :math:`\text{OLB}_k = Q\ax{\angl{n-k-1} i} + R(1 + i)^{-(n-k)}`

.. code-block:: python

   Loan(
       amt=L,
       pmt=Q,
       gr,
       period,
       term
   ).olb_p(t, r)

**Outstanding loan balance, prospective method (equal payments):** :math:`\text{OLB}_k = Q\ax{\angl{n-k} i}`

.. code-block:: python

   Loan(
       amt=L,
       pmt=Q,
       gr,
       period,
       term
   ).olb_p(t)

**Present value of an annuity-immediate with geometrically increasing payments:** :math:`P\left(\frac{1-\left(\frac{1+g}{1 + i}\right)^n}{i-g}\right)`

.. code-block:: python

    Annuity(
        amount=P,
        n=n,
        gr=Rate(i),
        grog=g
    ).pv()

**Present value of annuity-immediate with arithmetically increasing payments:** :math:`(I_{P, Q} a){\angln i}`

.. code-block:: python

   Annuity(
       amount=P,
       n=n,
       gr=Rate(i)
       aprog=Q
   ).pv()

**Accumulated value of annuity-immediate with arithmetically increasing payments:** :math:`(I_{P, Q} s){\angln i}`

.. code-block:: python

   Annuity(
       amount=P,
       n=n,
       gr=Rate(i)
       aprog=Q
   ).sv()

**Present value of annuity-immediate with arithmetically decreasing payments:** :math:`(Da){\angln i}`

.. code-block:: python

    Annuity(
       amount=n,
       n=n,
       gr=Rate(i)
       aprog=-1
   ).pv()

**Accumulated value of annuity-immediate with arithmetically decreasing payments:** :math:`(Ds){\angln i}`

.. code-block:: python

    Annuity(
       amount=n,
       n=n,
       gr=Rate(i)
       aprog=-1
   ).sv()

**Present value of annuity-due with arithmetically increasing payments:** :math:`(I_{P, Q} \ax**{}){\angln i}`

.. code-block:: python

   Annuity(
       amount=P,
       n=n,
       gr=Rate(i)
       aprog=Q,
       imd='due'
   ).pv()

**Accumulated value of annuity-due with arithmetically increasing payments:** :math:`(I_{P, Q} \sx**{}){\angln i}`

.. code-block:: python

   Annuity(
       amount=P,
       n=n,
       gr=Rate(i)
       aprog=Q,
       imd='due'
   ).sv()

**Present value of annuity-due with arithmetically decreasing payments:** :math:`(D\ax**{}){\angln i}`

.. code-block:: python

    Annuity(
       amount=n,
       n=n,
       gr=Rate(i)
       aprog=-1,
       imd='due'
   ).pv()

**Accumulated value of annuity-due with arithmetically decreasing payments:** :math:`(D\sx**{}){\angln i}`

.. code-block:: python

    Annuity(
       amount=n,
       n=n,
       gr=Rate(i),
       aprog=-1,
       imd='due'
   ).sv()

**Present value of perpetuity-immediate with arithmetically increasing payments:** :math:`(I_{P, Q} a){\angl{\infty} i}`

.. code-block:: python

    Annuity(
       amount=P,
       term=np.Inf,
       gr=Rate(i),
       aprog=Q
   ).pv()

**Present value of perpetuity-due with arithmetically increasing payments:** :math:`(I_{P, Q} \ax**{}){\angl{\infty} i}`

.. code-block:: python

    Annuity(
       amount=P,
       term=np.Inf,
       gr=Rate(i)
       aprog=Q,
       imd='due'
   ).pv()

**Present value of annuity-immediate with payments more frequent than each interest period:** :math:`\ax{\angln i}[(m)]`

.. code-block:: python

   Annuity(
       amount=1/m,
       term=n,
       gr=Rate(i),
       period=1/m
   ).pv()


**Accumulated value of annuity-immediate with payments more frequent than each interest period:** :math:`\sx{\angln i}[(m)]`

.. code-block:: python

   Annuity(
       amount=1/m,
       term=n,
       gr=Rate(i),
       period=1/m
   ).sv()

**Present value of annuity-due with payments more frequent than each interest period:** :math:`\ax**{\angln i}[(m)]`

.. code-block:: python

   Annuity(
       amount=1/m,
       term=n,
       gr=Rate(i),
       period=1/m,
       imd='due'
   ).pv()

**Accumulated value of annuity-due with payments more frequent than each interest period:** :math:`\sx**{\angln i}[(m)]`

.. code-block:: python

   Annuity(
       amount=1/m,
       term=n,
       gr=Rate(i),
       period=1/m,
       imd='due'
   ).sv()

**Present value of perpetuity-immediate with payments more frequent than each interest period:** :math:`\ax{\angl{\infty} i}[(m)]`

.. code-block:: python

   Annuity(
       amount=1/m,
       term=np.Inf,
       gr=Rate(i),
       period=1/m
   ).pv()

**Present value of perpetuity-due with payments more frequent than each interest period:** :math:`\sx**{\angl{\infty} i}[(m)]`

.. code-block:: python

   Annuity(
       amount=1/m,
       term=np.Inf,
       gr=Rate(i),
       period=1/m,
       imd='due'
   ).pv()