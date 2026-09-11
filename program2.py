import math


def take_home_fraction(tax_percent):
    """Return the fraction of a paycheck that is kept, given a tax percentage."""
    return 1 - (tax_percent / 100)


def calculate_take_home(hourly_wage, hours_per_week, tax_percent):
    """Return after-tax pay as (per week, per month, per year).

    A month is treated as four weeks and a year as twelve such months.
    """
    hourly_wage_after_taxes = hourly_wage * take_home_fraction(tax_percent)
    money_per_week = hourly_wage_after_taxes * hours_per_week
    money_per_month = money_per_week * 4
    money_per_year = money_per_month * 12
    return money_per_week, money_per_month, money_per_year


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


def main():
    print("You will be asked several questions regarding your financial situation.")
    print("")

    hourlywage = ask_for_number("How much do you make per hour before taxes? (Format: 8.31, 14) $", lowest=0)
    workweek = ask_for_number("How many hours do you work in a week? (Format: 17.56, 40) ", lowest=0, highest=168)
    taxestakenoutpercentnumber = ask_for_number("How much percent of your paycheck is taken out for taxes? (Format: 10, 20, 30, etc) ", lowest=0, highest=100)

    moneyperweek, moneypermonth, moneyperyear = calculate_take_home(
        hourlywage, workweek, taxestakenoutpercentnumber
    )

    print("")
    print("In a week, you will make $%d after taxes." % moneyperweek)
    print("")
    print("In a month, you will make $%d after taxes." % moneypermonth)
    print("")
    print("In a year, you will make $%d after taxes." % moneyperyear)
    print("")

    input("\nPress Enter to exit the program.")


if __name__ == "__main__":
    main()
