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