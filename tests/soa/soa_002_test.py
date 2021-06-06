from tmval import Annuity, isolve_multiple

j = isolve_multiple(
    t1=20,
    t2=40,
    period=4,
    multiple=5,
    x0=.3,
    result_period=4
)


def test_rate():
    assert round(j, 4) == 0.3195


sv = Annuity(
    gr=j,
    amount=100,
    period=4,
    term=40,
    imd="due"
).sv()


def test_result():
    assert round(sv, 4) == 6194.7194


