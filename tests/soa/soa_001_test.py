from tmval import Rate

delta = Rate(
    rate=.04,
    pattern="Nominal Interest",
    freq=2
).convert_rate(
    pattern="Force of Interest"
)


def test_result():
    assert round(delta, 4) == .0396
