import math


def calculate_take_home(hourly_wage, hours_per_week, tax_percent):
    """Return after-tax pay as (per week, per month, per year).

    A month is treated as four weeks and a year as twelve such months.
    """
    # The percentage is applied last, as a single division by 100, so that
    # whole-number answers give exact figures. Turning it into a fraction
    # first (1 - 0.28) is not exact in floating point, and $432 would print
    # as $431 (issue #28).
    money_per_week = hourly_wage * hours_per_week * (100 - tax_percent) / 100
    money_per_month = money_per_week * 4
    money_per_year = money_per_month * 12
    return money_per_week, money_per_month, money_per_year


def calculate_before_taxes(hourly_wage, hours_per_week):
    """Return pre-tax pay as (per week, per month, per year).

    The periods are the same as in calculate_take_home, with nothing taken out.
    """
    return calculate_take_home(hourly_wage, hours_per_week, 0)


def whole_dollars(amount):
    """Return the amount with its cents dropped.

    The amount is first rounded to six decimal places, which removes the tiny
    floating-point error left by a wage with cents. Without this, 8.04 * 25 is
    200.99999999999997, and $201 would print as $200 (issue #32).
    """
    return math.floor(round(amount, 6))


def ask_for_number(prompt, lowest=None, highest=None):
    """Keep asking until the answer is a number, optionally within the given bounds.

    Both bounds are inclusive. Non-numeric answers, and answers that are not a
    finite number, are rejected with a message and the prompt is shown again.
    """
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            value = math.nan
        if not math.isfinite(value):
            print("That is not a number. Please try again.")
        elif lowest is not None and value < lowest:
            print("That is too low. Please enter a number of at least %g." % lowest)
        elif highest is not None and value > highest:
            print("That is too high. Please enter a number of at most %g." % highest)
        else:
            return value


def ask_questions_and_print_figures():
    print("You will be asked several questions regarding your financial situation.")
    print("")

    while True:
        hourlywage = ask_for_number("How much do you make per hour before taxes? (Format: 8.31, 14) $", lowest=0)
        workweek = ask_for_number("How many hours do you work in a week? (Format: 17.56, 40) ", lowest=0, highest=168)
        taxestakenoutpercentnumber = ask_for_number("How much percent of your paycheck is taken out for taxes? (Format: 10, 20, 30, etc) ", lowest=0, highest=100)

        grossperweek, grosspermonth, grossperyear = calculate_before_taxes(hourlywage, workweek)
        # The yearly figure before taxes is the largest one, so if it is
        # finite, every other figure is too.
        if math.isfinite(grossperyear):
            break
        print("Those answers give figures too large to calculate. Please try again.")
        print("")

    moneyperweek, moneypermonth, moneyperyear = calculate_take_home(
        hourlywage, workweek, taxestakenoutpercentnumber
    )

    grossperweek, grosspermonth, grossperyear = map(whole_dollars, (grossperweek, grosspermonth, grossperyear))
    moneyperweek, moneypermonth, moneyperyear = map(whole_dollars, (moneyperweek, moneypermonth, moneyperyear))

    print("")
    print("In a week, you will make $%d before taxes and $%d after taxes." % (grossperweek, moneyperweek))
    print("")
    print("In a month, you will make $%d before taxes and $%d after taxes." % (grosspermonth, moneypermonth))
    print("")
    print("In a year, you will make $%d before taxes and $%d after taxes." % (grossperyear, moneyperyear))
    print("")

    input("\nPress Enter to exit the program.")


def main():
    """Run the program, ending cleanly if the input is closed or interrupted.

    Pressing Ctrl-D, or piping in answers that run out early, makes input()
    raise EOFError. Since no answer exists, re-asking cannot help, so the
    program stops with a short message and a non-zero exit status instead of
    a traceback. Pressing Ctrl-C raises KeyboardInterrupt, which is handled
    the same way.
    """
    try:
        ask_questions_and_print_figures()
    except EOFError:
        print("")
        raise SystemExit("No answer was given, so the program is exiting.")
    except KeyboardInterrupt:
        print("")
        raise SystemExit("The program was interrupted, so it is exiting.")


if __name__ == "__main__":
    main()
