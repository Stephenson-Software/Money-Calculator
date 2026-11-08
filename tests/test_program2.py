"""Characterization tests for program2.

Every expectation here records what the program does today, so that a later
change to the arithmetic has to be deliberate. Where current behavior is
disputed, the test names say so rather than the assertion being softened.
"""

import math
import pathlib
import subprocess
import sys

import pytest

import program2


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


def test_whole_dollar_figures_are_exact_rather_than_just_below():
    # 15 * 40 = 600, less 28% is exactly 432. Turning 28% into the fraction
    # 0.72 first gave 431.99999999999994, printed as $431 (issue #28).
    assert program2.calculate_take_home(15, 40, 28) == (432.0, 1728.0, 20736.0)


def test_before_taxes_is_the_wage_times_the_hours_over_the_same_periods():
    assert program2.calculate_before_taxes(15, 40) == pytest.approx((600.0, 2400.0, 28800.0))


def test_before_taxes_matches_take_home_at_zero_percent_tax():
    assert program2.calculate_before_taxes(20, 40) == pytest.approx(program2.calculate_take_home(20, 40, 0))


def test_whole_dollars_drops_the_cents():
    # Current behavior, disputed in issue #5: cents are dropped, not rounded.
    assert program2.whole_dollars(145.9236) == 145
    assert program2.whole_dollars(145.995) == 145


def test_whole_dollars_is_not_one_dollar_short_after_floating_point_error():
    # 8.04 * 25 is exactly 201, but in floating point it is 200.99999999999997
    # (issue #32).
    assert 8.04 * 25 < 201
    assert program2.whole_dollars(8.04 * 25) == 201


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


def test_ask_for_number_checks_an_answer_too_large_for_a_float_against_the_bounds(monkeypatch, capsys):
    # float("1e309") is infinity, but the answer is written in digits, so it is
    # refused as too high or too low rather than as not a number (issue #38).
    feed_answers(monkeypatch, ["1e309", "-1e309", "40"])
    assert program2.ask_for_number("hours? ", lowest=0, highest=168) == pytest.approx(40.0)
    output = capsys.readouterr().out
    assert "That is too high. Please enter a number of at most 168." in output
    assert "That is too low. Please enter a number of at least 0." in output
    assert "That is not a number." not in output


def test_ask_for_number_refuses_an_answer_too_large_for_a_float_with_no_highest_bound(monkeypatch, capsys):
    feed_answers(monkeypatch, ["1e309", "15"])
    assert program2.ask_for_number("wage? ", lowest=0) == pytest.approx(15.0)
    output = capsys.readouterr().out
    assert output.count("That is too large to calculate. Please try again.") == 1
    assert "That is not a number." not in output


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
    assert "In a week, you will make $600 before taxes and $480 after taxes." in output


def test_main_reasks_on_a_negative_answer_at_every_prompt(monkeypatch, capsys):
    prompts = feed_answers(monkeypatch, ["-15", "15", "-40", "40", "-20", "20", ""])
    program2.main()

    assert len(prompts) == 7
    assert prompts[0] == prompts[1]
    assert prompts[2] == prompts[3]
    assert prompts[4] == prompts[5]

    output = capsys.readouterr().out
    assert output.count("That is too low. Please enter a number of at least 0.") == 3
    assert "In a week, you will make $600 before taxes and $480 after taxes." in output


def test_main_accepts_answers_at_the_lowest_limits(monkeypatch, capsys):
    feed_answers(monkeypatch, ["0", "0", "0", ""])
    program2.main()

    output = capsys.readouterr().out
    assert "That is too low." not in output
    assert "In a week, you will make $0 before taxes and $0 after taxes." in output


def test_main_accepts_answers_at_the_highest_limits(monkeypatch, capsys):
    # 15 * 168 = 2520 a week, 2520 * 4 = 10080 a month, and 10080 * 12 = 120960
    # a year, all of which a 100% tax takes out.
    feed_answers(monkeypatch, ["15", "168", "100", ""])
    program2.main()

    output = capsys.readouterr().out
    assert "That is too high." not in output
    assert "In a week, you will make $2520 before taxes and $0 after taxes." in output
    assert "In a month, you will make $10080 before taxes and $0 after taxes." in output
    assert "In a year, you will make $120960 before taxes and $0 after taxes." in output


def test_main_reasks_all_three_questions_when_the_figures_are_too_large(monkeypatch, capsys):
    # 1e307 * 40 = 4e308 is past the largest float, so the figures would be
    # infinite (issue #21).
    prompts = feed_answers(monkeypatch, ["1e307", "40", "20", "15", "40", "20", ""])
    program2.main()

    assert len(prompts) == 7
    assert prompts[0:3] == prompts[3:6]

    output = capsys.readouterr().out
    assert "Those answers give figures too large to calculate. Please try again." in output
    assert "In a week, you will make $600 before taxes and $480 after taxes." in output


def test_main_reasks_when_the_week_alone_would_fit_but_the_year_would_not(monkeypatch, capsys):
    # 3e304 * 168 = 5.04e306 is below the largest float, but 48 such weeks are
    # not, and neither is the 100 times that the percentage step goes through.
    feed_answers(monkeypatch, ["3e304", "168", "0", "15", "40", "20", ""])
    program2.main()

    output = capsys.readouterr().out
    assert "Those answers give figures too large to calculate." in output
    assert "In a year, you will make $28800 before taxes and $23040 after taxes." in output


def test_main_reasks_when_only_the_percentage_step_is_too_large(monkeypatch, capsys):
    # 5e304 * 40 = 2e306 and 48 such weeks are about 9.6e307, both below the
    # largest float, but the pay is multiplied by 100 before it is divided by
    # 100 (issue #28), and 2e308 is past it. These answers are refused even
    # though the figures themselves would fit.
    feed_answers(monkeypatch, ["5e304", "40", "0", "15", "40", "20", ""])
    program2.main()

    output = capsys.readouterr().out
    assert "Those answers give figures too large to calculate." in output
    assert "In a year, you will make $28800 before taxes and $23040 after taxes." in output


def test_weekly_pay_overflows_once_a_hundred_times_it_is_too_large():
    # The largest float is about 1.8e308, so the limit is a week of about
    # 1.8e306. Its year is then only about 8.6e307, so the yearly figure is
    # never the only one too large.
    assert program2.calculate_before_taxes(1.7e306, 1) == pytest.approx((1.7e306, 6.8e306, 8.16e307))
    assert program2.calculate_before_taxes(1.8e306, 1) == (math.inf, math.inf, math.inf)


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
    assert "In a year, you will make $28800 before taxes and $23040 after taxes." in capsys.readouterr().out


def test_main_exits_with_a_message_when_interrupted_at_a_prompt(monkeypatch, capsys):
    # The wage is answered, then Ctrl-C is pressed while the hours are being
    # asked for (issue #24).
    answers = iter(["15"])
    prompts = []

    def fake_input(prompt=""):
        prompts.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise KeyboardInterrupt from None

    monkeypatch.setattr("builtins.input", fake_input)

    with pytest.raises(SystemExit) as exit_info:
        program2.main()

    assert exit_info.value.code == "The program was interrupted, so it is exiting."
    assert len(prompts) == 2
    assert "In a week, you will make" not in capsys.readouterr().out


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_main_ends_the_prompt_line_before_exiting(monkeypatch, capsys, error):
    # The exit message goes to standard error, so without this blank line it
    # would appear on the same line as the unanswered prompt.
    def fake_input(prompt=""):
        raise error

    monkeypatch.setattr("builtins.input", fake_input)

    with pytest.raises(SystemExit):
        program2.main()

    assert capsys.readouterr().out == (
        "You will be asked several questions regarding your financial situation.\n\n\n"
    )


def test_running_the_script_prints_the_exact_session():
    # A run of the real file, so this also covers the __main__ guard. The
    # answers are piped in, so they are not echoed between the prompts.
    result = subprocess.run(
        [sys.executable, "program2.py"],
        input="15\n40\n20\n\n",
        capture_output=True,
        text=True,
        cwd=pathlib.Path(program2.__file__).parent,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == (
        "You will be asked several questions regarding your financial situation.\n"
        "\n"
        "How much do you make per hour before taxes? (Format: 8.31, 14) $"
        "How many hours do you work in a week? (Format: 17.56, 40) "
        "How much percent of your paycheck is taken out for taxes? (Format: 10, 20, 30, etc) "
        "\n"
        "In a week, you will make $600 before taxes and $480 after taxes.\n"
        "\n"
        "In a month, you will make $2400 before taxes and $1920 after taxes.\n"
        "\n"
        "In a year, you will make $28800 before taxes and $23040 after taxes.\n"
        "\n"
        "\n"
        "Press Enter to exit the program."
    )


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
    assert "In a week, you will make $600 before taxes and $480 after taxes." in output
    assert "In a month, you will make $2400 before taxes and $1920 after taxes." in output
    assert "In a year, you will make $28800 before taxes and $23040 after taxes." in output


def test_printed_whole_dollar_figures_are_not_one_dollar_short(monkeypatch, capsys):
    # Issue #28: at 28% tax these figures used to print as $431, $1727 and $20735.
    answers = iter(["15", "40", "28", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    program2.main()

    output = capsys.readouterr().out
    assert "In a week, you will make $600 before taxes and $432 after taxes." in output
    assert "In a month, you will make $2400 before taxes and $1728 after taxes." in output
    assert "In a year, you will make $28800 before taxes and $20736 after taxes." in output


def test_printed_whole_dollar_figures_from_a_wage_with_cents_are_not_one_dollar_short(monkeypatch, capsys):
    # Issue #32: 8.04 * 25 = 201 exactly, but these used to print as $200, $803 and $9647.
    answers = iter(["8.04", "25", "0", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    program2.main()

    output = capsys.readouterr().out
    assert "In a week, you will make $201 before taxes and $201 after taxes." in output
    assert "In a month, you will make $804 before taxes and $804 after taxes." in output
    assert "In a year, you will make $9648 before taxes and $9648 after taxes." in output


def test_figure_just_below_a_whole_dollar_prints_one_dollar_high(monkeypatch, capsys):
    # Current behavior, disputed in issue #34: 43.56 * 60.44 * 57.62 / 100 is
    # exactly 1516.99999968, which the six-decimal round in whole_dollars
    # carries up to 1517. The month, 6067.99999872, is further from a whole
    # dollar and keeps its truncated figure, so it is not four printed weeks.
    answers = iter(["43.56", "60.44", "42.38", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    program2.main()

    output = capsys.readouterr().out
    assert "In a week, you will make $2632 before taxes and $1517 after taxes." in output
    assert "In a month, you will make $10531 before taxes and $6067 after taxes." in output


def test_printed_figures_drop_the_cents(monkeypatch, capsys):
    # Current behavior, disputed in issue #5: %d truncates rather than rounds.
    answers = iter(["8.31", "17.56", "10", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    program2.main()

    # 8.31 * 17.56 = 145.9236 before taxes, 131.33124 after; both lose the cents.
    assert "In a week, you will make $145 before taxes and $131 after taxes." in capsys.readouterr().out
