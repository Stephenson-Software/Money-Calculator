# Money Calculator

A Python program that calculates how much you make in a week, a month, and a year, before and after taxes.

## Requirements

- Python 3 (no third-party packages are needed)

## Running

```bash
python3 program2.py
```

## Prompts

Three values are asked for, in this order. Each is entered as a bare number.

| Order | Prompt | Example answer | Meaning |
|-------|--------|----------------|---------|
| 1 | `How much do you make per hour before taxes?` | `15` | Gross hourly wage, in dollars — `0` or more |
| 2 | `How many hours do you work in a week?` | `40` | Hours worked per week — `0` to `168` |
| 3 | `How much percent of your paycheck is taken out for taxes?` | `20` | Tax percentage, as a plain number — `20`, not `0.20` or `20%` — `0` to `100` |

An answer that is not a number (such as `abc`, `$15`, or `20%`) or that falls outside the range shown is refused with a short message, and the same question is asked again.

The program then prints the three figures and waits on a final `Press Enter to exit the program.` prompt, so it does not close on its own.

If the input is closed at any prompt instead — by pressing Ctrl-D, or because piped-in answers ran out — the program stops with the message `No answer was given, so the program is exiting.` and a non-zero exit status.

## Example

```
You will be asked several questions regarding your financial situation.

How much do you make per hour before taxes? (Format: 8.31, 14) $15
How many hours do you work in a week? (Format: 17.56, 40) 40
How much percent of your paycheck is taken out for taxes? (Format: 10, 20, 30, etc) 20

In a week, you will make $600 before taxes and $480 after taxes.

In a month, you will make $2400 before taxes and $1920 after taxes.

In a year, you will make $28800 before taxes and $23040 after taxes.


Press Enter to exit the program.
```

## How the figures are derived

- Weekly pay before taxes is the hourly wage multiplied by the hours worked per week.
- Weekly pay after taxes is the hourly wage, less the given tax percentage, multiplied by the hours worked per week.
- Monthly pay, before or after taxes, is four weeks of the matching weekly figure.
- Yearly pay is twelve of those months — that is, 48 weeks rather than 52.

## Known limitations

- The printed figures are truncated to whole dollars, so cents are dropped ([#5](https://github.com/Stephenson-Software/Money-Calculator/issues/5)).
- A year is treated as 48 weeks ([#4](https://github.com/Stephenson-Software/Money-Calculator/issues/4)).

## Tests

The arithmetic is covered by [pytest](https://docs.pytest.org/) tests in `tests/`:

```bash
python3 -m pytest
```

## License

Licensed under the Stephenson Software Non-Commercial License (Stephenson-NC) — non-commercial use only. See [LICENSE](LICENSE).
