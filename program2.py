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


def main():
    print("You will be asked several questions regarding your financial situation.")
    print("")

    hourlywage = float(input("How much do you make per hour before taxes? (Format: 8.31, 14) $"))
    workweek = float(input("How many hours do you work in a week? (Format: 17.56, 40) "))
    taxestakenoutpercentnumber = float(input("How much percent of your paycheck is taken out for taxes? (Format: 10, 20, 30, etc) "))

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
