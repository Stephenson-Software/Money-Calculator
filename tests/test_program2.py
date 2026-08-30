"""Characterization tests for program2.

Every expectation here records what the program does today, so that a later
change to the arithmetic has to be deliberate. Where current behavior is
disputed, the test names say so rather than the assertion being softened.
"""

import pytest

import program2


def test_take_home_fraction_converts_percent_to_a_fraction():
    assert program2.take_home_fraction(20) == pytest.approx(0.8)


def test_take_home_fraction_keeps_everything_at_zero_percent():
    assert program2.take_home_fraction(0) == pytest.approx(1.0)


def test_take_home_fraction_keeps_nothing_at_one_hundred_percent():
    assert program2.take_home_fraction(100) == pytest.approx(0.0)


def test_weekly_pay_is_the_kept_share_of_the_wage_times_the_hours():
    week, _, _ = program2.calculate_take_home(15, 40, 20)
    assert week == pytest.approx(480.0)


def test_monthly_pay_is_four_weeks():
    week, month, _ = program2.calculate_take_home(15, 40, 20)
    assert month == pytest.approx(1920.0)
    assert month == pytest.approx(week * 4)


def test_yearly_pay_assumes_forty_eight_weeks_not_fifty_two():
    # Current behavior, disputed in issue #4: a year is twelve four-week
    # months, so 48 weeks rather than 52.
    week, _, year = program2.calculate_take_home(15, 40, 20)
    assert year == pytest.approx(23040.0)
    assert year == pytest.approx(week * 48)


def test_no_tax_leaves_the_full_gross_pay():
    assert program2.calculate_take_home(20, 40, 0) == pytest.approx((800.0, 3200.0, 38400.0))


def test_full_tax_leaves_nothing():
    assert program2.calculate_take_home(20, 40, 100) == pytest.approx((0.0, 0.0, 0.0))


def test_zero_hours_earn_nothing():
    assert program2.calculate_take_home(15, 0, 20) == pytest.approx((0.0, 0.0, 0.0))


def test_fractional_wages_and_hours_are_not_rounded():
    week, _, _ = program2.calculate_take_home(8.31, 17.56, 10)
    assert week == pytest.approx(131.33124)


def test_main_prompts_in_order_and_prints_the_three_figures(monkeypatch, capsys):
    answers = iter(["15", "40", "20", ""])
    prompts = []

    def fake_input(prompt=""):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)
    program2.main()

    assert "per hour" in prompts[0]
    assert "in a week" in prompts[1]
    assert "percent" in prompts[2]

    output = capsys.readouterr().out
    assert "In a week, you will make $480 after taxes." in output
    assert "In a month, you will make $1920 after taxes." in output
    assert "In a year, you will make $23040 after taxes." in output


def test_printed_figures_drop_the_cents(monkeypatch, capsys):
    # Current behavior, disputed in issue #5: %d truncates rather than rounds.
    answers = iter(["8.31", "17.56", "10", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    program2.main()

    assert "In a week, you will make $131 after taxes." in capsys.readouterr().out
