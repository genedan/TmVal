# TmVal
[![PyPI version](https://badge.fury.io/py/tmval.svg)](https://badge.fury.io/py/tmval)

Time Value of Money

### Introduction
[Documentation](https://genedan.com/tmval/docs) | [Development Blog](https://genedan.com) | [PyPI](https://pypi.org/project/tmval/)

TmVal is a package that provides tools for the valuation of various financial instruments (annutities, bonds).

It can be used to study for Actuarial Exam FM, and (hopefully) used on the job for projects where time value of money is relevant.

### Installation

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

### Examples

Suppose we have a nominal discount rate of d<sup>(12)</sup> = .06 compounded monthly. What is the equivalent nominal interest rate compounded quarterly?

```python
from tmval import Rate

nom_d = Rate(
    rate=.06, 
    pattern="Nominal Discount",
    freq=12
)

nom_i = nom_d.convert_rate( 
    pattern='Nominal Interest', 
    freq=4
)

print(nom_i)

out:
Pattern: Nominal Interest
Rate: 0.06060503776426174
Compounding Frequency: 4 times per year
```

Suppose we have the following tiered investment account with the following interest rate schedule. This means the account pays 1% if the balance is below 10,000. Once it reaches 10,000, it pays 2%, and beyond 20,000, it pays 3%.

Required Minimum Balance | Interest Rate 
-------------------------|----------------
0|1%
10,000|2%
20,000| 3%
 
If we invested 5,000 today and made no further contributions, at what times would we expect to reach 2% and 3% interest?

```python
from tmval import Amount, TieredBal

my_tiered_bal = TieredBal(
    tiers=[0, 10000, 20000],
    rates=[.01, .02, .03]
)

print(my_tiered_bal.get_jump_times(k=5000))

out:
[69.66071689357483, 104.66350567472134]
```

Suppose we purchase an annuity-immediate that makes payments of 1,000 each year for a term of five years, with the first payment beginning 5 years from now. If the annual effective interest rate is 5%, how much would the accumulated payments grow to 20 years from now?

```python
from tmval import Annuity, Rate

ann = Annuity(
   amount=1000,
   n=5,
   gr=Rate(.05),
   deferral=4
)

print(ann.eq_val(20))
out:
9450.704605312447
```