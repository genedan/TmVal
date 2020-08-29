# TmVal
[![PyPI version](https://badge.fury.io/py/tmval.svg)](https://badge.fury.io/py/tmval)

Time Value of Money

## Introduction
[Documentation](https://genedan.com/tmval/docs) | [Development Blog](https://genedan.com) | [PyPI](https://pypi.org/project/tmval/)

TmVal is a package that provides tools for the valuation of various financial instruments (annuities, bonds).

It can be used to study for Actuarial Exam FM, and (hopefully) used on the job for projects where time value of money is relevant.

## Feature Highlights

-   TmVal supports growth patterns that are more complex than compound
    interest. In addition to supporting simple, compound, and nominal
    interest, TmVal handles growth patterns that may be of theoretical
    interest to actuaries, such as continuously compounded rates (Force
    of Interest), polynomial growth, and arbitrary amount and
    accumulation functions.
    
-   TmVal provides equations of value computations for core financial
instruments in actuarial science, such as annuities, loans, and
arbitrary cash flow streams. As development is still in the alpha
stage, the types of investments TmVal supports is rapidly expanding.
I expect the package to soon offer classes for bonds, stocks, and
options.
    
-   TmVal's classes are intended to correspond closely to symbols used
in actuarial notation. Well-known symbols encountered by actuaries are supported. Refer to the
[Notation guide](https://genedan.com/tmval/docs/notation.html) in this documentation
to see the available symbols.

## Installation

```
pip install tmval
```

or

```
git clone https://github.com/genedan/TmVal
cd TmVal
python3 -m setup sdist bdist_wheel
cd dist
sudo pip3 install tmval*
```

### Amount and Accumulation Functions

TmVal supports the core growth functions of mathematical interest
theory, the [amount](https://genedan.com/tmval/docs/usage/growth/amount.html) and [accumulation](https://genedan.com/tmval/docs/usage/growth/ccumulation.html) functions, implemented via the
[Amount](https://genedan.com/tmval/docs/api_ref/amount/index.html) and
[Accumulation](https://genedan.com/tmval/docs/api_ref/amount/index.html) classes. These classes support all sorts of growth patterns, from simple and compound interest to more complex cases such as tiered investment accounts and polynomial growth.

For instance, suppose we have the tiered investment account with
annually compounded interest rates:

Required Minimum Balance | Interest Rate 
-------------------------|----------------
0|1%
10,000|2%
20,000| 3%

If we invest 18,000 today, to what value does it grow after 10 years?

```python
from tmval import Accumulation

def f(t):
    return .05 * (t **2) + .05 * t + 1


my_acc = Accumulation(gr=f)

print(my_acc.val(5))
2.5
```

If we were to invest 5000 today, how long would it take to reach 2% and
3% interest, assuming no future contributions?

```python
print(tb.get_jump_times(k=5000))
[69.66071689357483, 104.66350567472134]
```
It will take almost 70 years to reach 2%, and about 105 years to reach
3%. That\'s a long time!

### Interest Rate Conversions

Interest rates are represented by a core data type in TmVal, the
[Rate](file:///home/ubuntu/TmVal/docs/_build/html/api_ref/rate/index.html) class. This custom data type offers a convenient way to perform computations with a variety of interest rate patterns as well as conversions between them. The main patterns supported by the [Rate](file:///home/ubuntu/TmVal/docs/_build/html/api_ref/rate/index.html) class
are:

1.  Effective Interest
2.  Effective Discount
3.  Nominal Interest
4.  Nominal Discount
5.  Force of Interest
6.  Simple Interest
7.  Simple Discount

The relationships between compound interest rates can be represented
with the following expression:

![interest conversion](https://github.com/genedan/TmVal/blob/master/docs/readme_gh/interest_conversion.svg)

Since there are so many varieties of rates, as well as relationships
between them, an actuary would have to write over twenty conversion
functions to handle the full spectrum of interest rates if they weren't
using a package like TmVal. The good news is that TmVal handles all
these conversions with a single method,
[Rate.convert_rate](https://genedan.com/tmval/docs/api_ref/rate/convert_rate.html).

For example, if we needed to convert 5% rate compounded annually to a
nominal discount rate convertible monthly, we could do the following:

```python
from tmval import Rate

i = Rate(.05)

nom_d = i.convert_rate(
    pattern="Nominal Discount",
    freq=12
)

print(nom_d)
Pattern: Nominal Discount
Rate: 0.048691111787194874
Compounding Frequency: 12 times per year
```

Furthermore, we can demonstrate a conversion to nominal interest
compounded quarterly, and then to δ, the force of interest, and
then back to compound annual effective interest:

```python
nom_i = nom_d.convert_rate(
    pattern="Nominal Interest",
    freq=4
)

print(nom_i)
Pattern: Nominal Interest
Rate: 0.04908893771615652
Compounding Frequency: 4 times per year

delta = nom_i.convert_rate(
    pattern="Force of Interest"
)

print(delta)
Pattern: Force of Interest
Rate: 0.04879016416943141

i2 = delta.convert_rate(
    pattern="Effective Interest",
    interval=1
)

print(i2)
Pattern: Effective Interest
Rate: 0.04999999999999938
Unit of time: 1 year
```

For more details, see [The Rate Class, Revisited](https://genedan.com/tmval/docs/usage/growth/rate_revisit.html) of the [Usage Tutorial](https://genedan.com/tmval/docs/usage/index.html).

### Equations of Value

TmVal can solve for the time $\tau$ equation of value for common
financial instruments such as annuities and loans, as well as for
arbitrary cash flows. This is done via the [Payments](https://genedan.com/tmval/docs/api_ref/payments/index.html) class:

![equation of value](https://github.com/genedan/TmVal/blob/master/docs/readme_gh/eq_val.svg)

For example, we can solve for the internal rate of return of an
investment of 10,000 at time 0 which returns 5,000 at time 1 and 6,000
at time 2:

```python
from tmval import Payments

pmts = Payments(
    amounts=[-10000, 5000, 6000],
    times=[0, 1, 2]
)

# internal rate of return
print(pmts.irr())
[0.0639410298049854, -1.5639410298049854]
```

We can also use the [Payments](https://genedan.com/tmval/docs/api_ref/payments/index.html) class to
find the time-weighted yield:

![time weighted yield](https://github.com/genedan/TmVal/blob/master/docs/readme_gh/tw_yield.svg)

where

![time weighted factor](https://github.com/genedan/TmVal/blob/master/docs/readme_gh/tw_factor.svg)

Suppose we deposit 100,000 in a bank account at time 0. It grows to
105,000 at time 1, and we immediately deposit an additional 5,000. It
then grows to 115,000 at time 2. The time-weighted yield is:

```python
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
Pattern: Effective Interest
Rate: 0.0477248077273309
Unit of time: 1 year
```

Annuities
=========

Annuities are one of the core financial instruments underlying life
insurance products. TmVal provides support for many kinds of annuities
via its [Annuity](https://genedan.com/tmval/docs/api_ref/annuity/index.html#tmval.annuity.Annuity) class, such as:

1.  Annuity-immediate
2.  Annuity-due
3.  Perpetuity-immediate
4.  Perpetuity-due
5.  Arithmetically increasing annuity-immediate
6.  Arithmetically increasing annuity-due
7.  Arithmetically increasing perpetuity-immediate
8.  Arithmetically increasing perpetuity-due
9.  Geometrically increasing annuity-immediate
10. Geometrically increasing annuity-due
11. Geometrically increasing perpetuity-immediate
12. Geometrically increasing perpetuity-due
13. Level annuity-immediate with payments more frequent than each
    interest period
14. Continuously-paying annuity

... and many more. To see what other symbols are supported, consult the
[Notation guide](https://genedan.com/tmval/docs/notation.html).

Unlike other packages, which tend to use functions to represent the
different types of annuities, TmVal represents annuities as a class,
which gives it access to several methods that can be performed on the
annuity, such as equations of value. So rather than simply returning a
float value via a function, TmVal expands the manipulations that can be
done with an annuity. My aim is to allow the
[Annuity](https://genedan.com/tmval/docs/api_ref/annuity/index.html#tmval.annuity.Annuity) class to serve as a base
class for or be embedded in more complex insurance products.

We can perform simple calculations, such as finding the present value of
a basic annuity-due with a five year term and a compound interest rate of 5%:

```python
from tmval import Annuity

print(Annuity(gr=.05, n=5).pv())
4.329476670630819
```

To more complex ones, such as the accumulated value of an arithmetically
increasing annuity with a starting payment of 5,000, and subsequent payments of 100 over a 5-year term, at 5% compound interest:
```python
ann = Annuity(
    amount=5000,
    gr=.05,
    n=5,
    aprog=100,
    imd='due'
)

print(ann.sv())
30113.389687500014
```

###Amortization


TmVal's Loan class has methods for
obtaining information that we might want about loans, such as
amortization schedules and outstanding loan balances.

The output for several TmVal\'s classes are intended to be compatible
with [Pandas](https://pandas.pydata.org), a popular data analysis
library. The output for the Loan class's
amortization method is one such
example.

For example, suppose we were to obtain a 2-year loan of 50,000, to be
paid back with monthly payments made at the end of each month. If the
interest rate were 4% convertible monthly, what is the amortization
schedule?

```python
import pandas as pd

from tmval import Loan, Rate

gr = Rate(
    rate=.04,
    pattern="Nominal Interest",
    freq=4
)

my_loan = Loan(
    amt=50000,
    period=1/12,
    term=2,
    gr=gr,
    cents=True
)

amort = pd.DataFrame(my_loan.amortization())

print(amort)
    time  payment_amt  interest_paid  principal_paid  remaining_balance
0   0.00          NaN            NaN             NaN           50000.00
1   0.08      2170.96         166.11         2004.85           47995.15
2   0.17      2170.96         159.45         2011.51           45983.65
3   0.25      2170.96         152.77         2018.19           43965.46
4   0.33      2170.96         146.07         2024.89           41940.56
5   0.42      2170.96         139.34         2031.62           39908.94
6   0.50      2170.96         132.59         2038.37           37870.57
7   0.58      2170.96         125.82         2045.14           35825.43
8   0.67      2170.96         119.02         2051.94           33773.49
9   0.75      2170.96         112.21         2058.75           31714.74
10  0.83      2170.96         105.37         2065.59           29649.14
11  0.92      2170.96          98.50         2072.46           27576.68
12  1.00      2170.96          91.62         2079.34           25497.34
13  1.08      2170.96          84.71         2086.25           23411.09
14  1.17      2170.96          77.78         2093.18           21317.91
15  1.25      2170.96          70.82         2100.14           19217.77
16  1.33      2170.96          63.85         2107.11           17110.66
17  1.42      2170.96          56.85         2114.11           14996.55
18  1.50      2170.96          49.82         2121.14           12875.41
19  1.58      2170.96          42.78         2128.18           10747.22
20  1.67      2170.96          35.71         2135.25            8611.97
21  1.75      2170.96          28.61         2142.35            6469.62
22  1.83      2170.96          21.49         2149.47            4320.16
23  1.92      2170.96          14.35         2156.61            2163.55
24  2.00      2170.74           7.19         2163.55              -0.00

```

Using the Loan class's
olb_r method, we can calculate the
outstanding loan balance at any time, such as after 1 year, using the
[retrospective method](https://genedan.com/tmval/docs/usage/loan/retrospective.html#outstanding-loan-balance-retrospective-method):

![olb retrospective](https://github.com/genedan/TmVal/blob/master/docs/readme_gh/olb_r.svg)

```python
print(my_loan.olb_r(t=1))
25497.34126843426
```

Now, what if we choose to overpay during the first two months, with
payments of 3,000 each, and then returning to normal payments? What is
the outstanding loan balance after 1 year?

```python
pmts = Payments(
    amounts=[3000] * 2 + [2170.06] * 10,
    times=[(x + 1) / 12 for x in range(12)]
)

print(my_loan.olb_r(t=1, payments=pmts))
23789.6328174795
```

## Development Status

TmVal is currently in the alpha stage of development. In the coming
weeks, I expect to add many more features, such as:

1.  Bonds
2.  Stocks
3.  Options
4.  Immunization

I anticipate declaring the project to be in beta stage once I\'ve
incorporated all of the main concepts on the syllabus of the SOA\'s
financial mathematics exam. The beta stage of the project will involve
the construction of a testing suite to insure the accuracy of the
computations in preparation for commercial use.

## Further Reading


Go ahead and give TmVal a try! The next section is the
[Installation and Quickstart](https://genedan.com/tmval/docs/quickstart.html#installation-and-quickstart) followed by
the [Usage Tutorial](https://genedan.com/tmval/docs/usage/index.html#usage-tutorial). For technical
documentation, consult the [API Reference](https://genedan.com/tmval/docs/api_ref/index.html#api-reference), which links to the source code of the project.