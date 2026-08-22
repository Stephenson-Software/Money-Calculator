print("You will be asked several questions regarding your financial situation.")
print("")

hourlywage = float(input("How much do you make per hour before taxes? (Format: 8.31, 14) $"))
workweek = float(input("How many hours do you work in a week? (Format: 17.56, 40) "))
taxestakenoutpercentnumber = float(input("How much percent of your paycheck is taken out for taxes? (Format: 10, 20, 30, etc) "))
taxestakenout = taxestakenoutpercentnumber / 10

hourlywageaftertaxes = hourlywage * taxestakenout
moneyperweek = hourlywageaftertaxes * workweek
moneypermonth = moneyperweek * 4
moneyperyear = moneypermonth * 12

print("")
print("In a week, you will make $%d after taxes." % moneyperweek)
print("")
print("In a month, you will make $%d after taxes." % moneypermonth)
print("")
print("In a year, you will make $%d after taxes." % moneyperyear)
print("")

input("\nPress Enter to exit the program.")
