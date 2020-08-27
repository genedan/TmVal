========================
Net Present Value
========================

In the context of this section, we define a return at time :math:`t` to be the net cash flow of payments occurring at that time. For example, if you have to pay someone 5,000 at time t=0, but receive 2500 from your pay check at the same time, your return is 5,000 - 2,500 = 500.

The :term:`net present value (NPV)` is the sum of the present value of a stream of returns. If we denote the undiscounted returns as :math:`R_0, R_1, R_2, ... , R_n`, occurring at times :math:`0, t_1, t_2, ..., t_n`, the NPV is defined as:

.. math::

   \sum_{k=0}^n R_k v(t_k)

NPV is useful in situations when you need to evaluate the value of an investment or deal. If the NPV is positive, the deal is worth undertaking. If it is negative, than the investment is not worth it.

Examples
=========

Suppose we are considering a potential investment where we must pay 10,000 up front, in exchange for payments of 1000 occurring at time 1, 2000 occurring at time 2, and 9000 occurring at time 3. If the effective interest rate is 10% compounded annually, should we make the investment?


.. ipython:: python

      from tmval import Payments

      pmts = Payments(
          amounts=[-10000, 1000, 2000, 9000],
          times=[0, 1, 2, 3],
          gr=.10
      )

      print(pmts.npv())

The NPV is negative, so we should not make this investment.
