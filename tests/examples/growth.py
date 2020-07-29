import tmval


def f(k, t):
    return k + 250 * t


my_amt = tmval.Amount(f, k=1000)


my_amt.val(t=4)

my_amt.interest_earned(t1=0, t2=5)

my_amt.effective_rate(1)

def f(k, t):
    return 1.2 ** t

my_acc = tmval.Accumulation(f, k=1)

my_acc.val(t=1)
my_acc.val(t=2)
my_acc.val(t=3)
my_acc.val(t=4)
my_acc.val(t=5)


def f(t):
    if 0 <= t <= 2:
        return (1 - .3) ** t
    else:
        return ((1 - .3) ** 2) * (1 + .4) ** (t - 2)


my_acc = tmval.Accumulation(f)

my_acc.val(1)

my_acc.val(2)

my_acc.val(3)
my_acc.val(4)
my_acc.val(5)


my_simple = tmval.SimpleAmt(k=1000, s=.25)

my_simple.val(4)
my_simple.val(1)

my_simple = tmval.SimpleAcc(.05)
my_simple.val(4)
my_simple.val(1)
1