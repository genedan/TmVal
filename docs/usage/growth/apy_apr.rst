========================
APY vs APR
========================

So far, what we have called the annual effective interest rate is also called the APY, or :term:`annual percentage yield<annual percentage yield (APY)>`. However, in practice, banks often quote what is called the :term:`annual percentage rate (APR)`, which is not the same thing as the APY.

For example, the bank might quote something like an APR of 6% compounded twice a year. In reality, this means that after 6 months of opening an account, each dollar is compounded at %6 / 2 = 3%, and then compounded again at the same rate after another 6 months:

.. math::

   \left(1 + \frac{.06}{2}\right)^2 = 1.0609

Which is equivalent to an APY of 6.09%.

This concept is generalized in interest theory with a term called the :term:`nominal interest rate`. We denote this rate as :math:`i^{(m)}` compounded :math:`m` times per year. For example, an APR of 6% compounded twice per year is the same as a nominal interest rate of :math:`i^{(2)} = 6\%` compounded :math:`m=2` times per year. In each period, money grows at a factor of:

.. math::

   \left(1 + \frac{i^{(m)}}{m}\right)^m

The nominal and effective interest rates are related by the following equations:

.. math::

   i^{(m)} &= m[(1+i)^{\frac{1}{m}} - 1] \\

   i &= \left(1+\frac{i^{(m)}}{m}\right)^m - 1

Examples
==========

Rework section - had conversions