============
Bonds
============

A :term:`bond` is a financial instrument that entities can use to borrow money. An entity, called a bond issuer, can issue bonds to parties, called bondholders, who are willing to lend it money. The bond itself is a promise from the issuer to pay the bondholders a stream of one more payments on specified dates in exchange for the amount borrowed, which is called the initial bond price.

TmVal's :class:`.Bond` class is used to define bonds. You can initialize a bond by supplying certain characteristics about the bonds to the bond constructor:

#. Bond price
#. Coupons
#. Yield rate
#. Redemption amount
#. Face value
#. Term

The bond price is the amount a bondholder pays to acquire a bond. If purchased from the issuer, this also represents the amount loaned to the issuer. Otherwise, it refers to the amount one pays to another bondholder for the rights to the remaining stream of payments promised by the bond.

Coupons are regular payments made by the bond issuer to the bondholder. A bond may have zero coupons, in which case it is referred to as a :ref:`zero-coupon <usage/bond/zerocoupon:Zero-Coupon Bonds>` bond.

The yield rate on a bond is the yield rate to the bondholder if the bond is held to maturity.

The redemption amount an amount paid on the due date of a bond, not including any coupons.

The face value is an amount used to calculate the coupon amount of a bond. Coupons are often referred to as being a certain % of the face value.

The term is the time between when the bond is purchased and its due date, after which the bond is considered to be repaid.

You do not have to specify all of these characteristics to initialize a bond in TmVal. Common bond problems involve those where not all the aforementioned quantities are known, and TmVal can be used to solve for these missing quantities.

This section explains how you can use TmVal to define bonds as well as the calculations you can perform on them.


.. toctree::
   :maxdepth: 1

   zerocoupon
   couponbond
   nonlevelcoupon
   premdisc
   makeham