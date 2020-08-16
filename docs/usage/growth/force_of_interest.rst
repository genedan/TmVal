========================
Force of Interest
========================

It can be shown that as the compounding frequency approaches infinity, the nominal interest and discount rates approach a value :math:`\delta` called the :term:`force of interest`:

.. math::

   \lim_{m \to \infty} i^{(m)} = \lim_{m \to \infty} d^{(m)} = \delta.

Examples
========

TmVal can handle force of interest problems by supplying a continually compounded interest rate to the :class:`.Amount` or :class:`.Accumulation` classes.

Suppose we have the force of interest :math:`\delta = .05`. What is the value at time 5 of 5000 invested at time 0?

.. ipython:: python

   from tmval import Amount, Rate

   my_amt = Amount(gr=Rate(delta=.05), k=5000)

   print(my_amt.val(5))

Suppose instead, we have 5000 at time 5. What is the present value if the force of interest remains at 5%?

.. ipython:: python

   from tmval import Accumulation, Rate

   my_acc = Accumulation(gr=Rate(delta=.05))

   pv = my_acc.discount_func(t=5, fv=5000)

   print(pv)

This could have also been solved by using the previously-introduced :func:`.compound_solver`:

.. ipython:: python

   from tmval import compound_solver, Rate

   gr = Rate(delta=.05)

   pv = compound_solver(gr=gr, fv=5000, t=5)

   print(pv)
