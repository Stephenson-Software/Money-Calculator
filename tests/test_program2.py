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


def feed_answers(monkeypatch, answers):
    """Make input() return the given answers in order, recording each prompt shown.

    Once the answers run out, input() raises EOFError, just as it does when
    standard input is closed.
    """
    answers = iter(answers)
    prompts = []

    def fake_input(prompt=""):
        prompts.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise EOFError("EOF when reading a line") from None

    monkeypatch.setattr("builtins.input", fake_input)
    return prompts


def test_ask_for_number_returns_the_parsed_answer(monkeypatch):
    feed_answers(monkeypatch, ["8.31"])
    assert program2.ask_for_number("wage? ") == pytest.approx(8.31)


def test_ask_for_number_reprompts_until_the_answer_is_numeric(monkeypatch, capsys):
    prompts = feed_answers(monkeypatch, ["abc", "$15", "20%", "", "15"])
    assert program2.ask_for_number("wage? ") == pytest.approx(15.0)
    assert prompts == ["wage? "] * 5
    assert capsys.readouterr().out.count("That is not a number. Please try again.") == 4


def test_ask_for_number_treats_nan_and_inf_as_not_a_number(monkeypatch, capsys):
    feed_answers(monkeypatch, ["nan", "inf", "-inf", "1"])
    assert program2.ask_for_number("hours? ", lowest=0) == pytest.approx(1.0)
    assert capsys.readouterr().out.count("That is not a number.") == 3


def test_ask_for_number_rejects_answers_below_the_lowest_bound(monkeypatch, capsys):
    feed_answers(monkeypatch, ["-15", "0"])
    assert program2.ask_for_number("wage? ", lowest=0) == pytest.approx(0.0)
    assert "That is too low. Please enter a number of at least 0." in capsys.readouterr().out


def test_ask_for_number_rejects_answers_above_the_highest_bound(monkeypatch, capsys):
    feed_answers(monkeypatch, ["150", "100"])
    assert program2.ask_for_number("tax? ", lowest=0, highest=100) == pytest.approx(100.0)
    assert "That is too high. Please enter a number of at most 100." in capsys.readouterr().out


def test_ask_for_number_has_no_bounds_by_default(monkeypatch):
    feed_answers(monkeypatch, ["-1000000"])
    assert program2.ask_for_number("anything? ") == pytest.approx(-1000000.0)


def test_main_reasks_on_bad_answers_and_still_prints_the_figures(monkeypatch, capsys):
    # Each prompt gets one bad answer before the good one: a non-number for the
    # wage, more hours than a week has, and a tax percentage above 100.
    prompts = feed_answers(monkeypatch, ["abc", "15", "500", "40", "150", "20", ""])
    program2.main()

    assert len(prompts) == 7
    assert prompts[0] == prompts[1]
    assert prompts[2] == prompts[3]
    assert prompts[4] == prompts[5]

    output = capsys.readouterr().out
    assert "That is not a number. Please try again." in output
    assert "That is too high. Please enter a number of at most 168." in output
    assert "That is too high. Please enter a number of at most 100." in output
    assert "In a week, you will make $480 after taxes." in output


def test_main_exits_with_a_message_when_input_is_closed_at_a_prompt(monkeypatch, capsys):
    # The wage is answered, then the input is closed while the hours are
    # being asked for (issue #16).
    prompts = feed_answers(monkeypatch, ["15"])

    with pytest.raises(SystemExit) as exit_info:
        program2.main()

    assert exit_info.value.code == "No answer was given, so the program is exiting."
    assert len(prompts) == 2
    assert "in a week" in prompts[1]
    assert "In a week, you will make" not in capsys.readouterr().out


def test_main_exits_with_a_message_when_input_is_closed_at_the_final_prompt(monkeypatch, capsys):
    # All three answers are given, but the input is closed before the
    # "Press Enter to exit" prompt is answered.
    prompts = feed_answers(monkeypatch, ["15", "40", "20"])

    with pytest.raises(SystemExit) as exit_info:
        program2.main()

    assert exit_info.value.code == "No answer was given, so the program is exiting."
    assert len(prompts) == 4
    assert "Press Enter to exit" in prompts[3]
    assert "In a year, you will make $23040 after taxes." in capsys.readouterr().out


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
