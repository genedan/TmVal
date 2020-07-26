# TmVal
[![PyPI version](https://badge.fury.io/py/tmval.svg)](https://badge.fury.io/py/tmval)

Time Value of Money

### Introduction

TmVal is a package that provides tools for the valuation of various financial instruments (annutities, bonds).

It can be used to study for Actuarial Exam FM, and (hopefully) used on the job for projects where time value of money is relevant.

### Installation

```
pip install tmval
```

or

```
git clone https://github.com/genedan/TmVal
```

### Examples

Define an amount function that pays 25% simple interest per period:

```
import tmval

def f(k, t):
    return k + 250 * t

my_amt = tmval.Amount(f, k=1000)
```
Check the value at time t=4
```
my_amt.val(t=4)
Out[3]: 2000
```

Check the interest earned during the first 5 periods:

```
my_amt.interest_earned(t1=0, t2=5)
Out[4]: 1250
```

Check the interest rate between times t=0 and t=1:

```
my_amt.effective_rate(1)
Out[6]: 0.25
```

The above example can also be constructed with a special subclass, SimpleAmt, representing the simple interest amount function:

```
my_simple = tmval.SimpleAmt(k=1000, s=.25)
my_simple.val(t=4)
my_simple.interest_earned(t1=0, t2=5)
my_simple.effective_rate(1)
``` 
