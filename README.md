# Coding Bootcamp Starter Repo

This repository is the baseline codebase for the coding boot camp. There are two
things in it:

1. **`Learn_To_Code/`** — four interactive notebooks that teach you to code, from
   variables through to Monte Carlo simulation. This is where students start.
   See [The Learn_To_Code Workbooks](#the-learn_to_code-workbooks).
2. **The working codebase** — `main.py`, `Data/`, `Utilities/`: a small but real
   research setup that pulls market data and analyses it.

The first workflow is simple: open the project in PyCharm, select a Python
interpreter, install the requirements, and run the root `main.py` file to check
everything works. Then open the first notebook.

You need **Python 3.9 or newer** (3.11+ recommended).

## Project Layout

```text
Coding_BootCamp/
├── main.py                     # Demo script to run first
├── requirements.txt            # Python package requirements
├── credentials.py              # Loads optional environment variables
├── .gitignore                  # Keeps your .env out of git
├── LICENSE
├── Learn_To_Code/              # The student workbooks — start here
│   ├── 1.Coding Essentials.ipynb
│   ├── 2.Plotting some data.ipynb
│   ├── 3.Regression.ipynb
│   ├── 4.Monte Carlo Simulation.ipynb
│   ├── workbook.py             # check() / hint() / todo() — the grader
│   └── generate_data.py        # builds the workbook CSVs on your Desktop
├── Data/
│   ├── data_definition.py      # DataDefinition: one interface for data
│   └── sources/
│       ├── famafrench.py       # Fama-French data via requests
│       ├── fred.py             # FRED data via requests
│       └── yfin.py             # Yahoo Finance data via yfinance
├── Classes/
│   └── MGTF_402/
│       └── Assignment_1.py     # Intentionally blank; reserved for exercises
└── Utilities/
    └── tools.py                # Helper functions for returns and statistics
```

The demo chart is written to your **Desktop**, not into the project folder, so
nothing you generate will clutter the repository.

## Setup In PyCharm

1. Open PyCharm.
2. Choose **Open** and select the `Coding_BootCamp` project folder.
3. Select or create a virtual environment:
   - macOS: **PyCharm > Settings > Project > Python Interpreter**
   - Windows: **File > Settings > Project > Python Interpreter**
   - Choose an existing interpreter or create a new virtual environment such as
     `.venv`.
4. Open the PyCharm terminal and install the project requirements:

```bash
python -m pip install -r requirements.txt
```

The main packages are:

| Package | Used for |
| --- | --- |
| `pandas` | DataFrames and time series |
| `numpy` | Numerical operations |
| `scipy` | Summary statistics |
| `matplotlib` | Plotting |
| `requests` | Downloading Fama-French and FRED data |
| `yfinance` | Yahoo Finance market data |
| `python-dotenv` | Loading optional values from `.env` |
| `statsmodels` | Regression with standard errors (notebook 3) |
| `jupyterlab`, `ipykernel` | Running the notebooks |

## Optional FRED API Key

**You can run the whole demo without a FRED key.** The only thing you lose is
the grey NBER recession shading on the chart. The factor data, the statistics
table, the VIX panel, and the saved image all still work.

A key is needed only for live requests to the FRED API, such as pulling the
`USRECD` recession series. Without one, the script prints a short "this part
was skipped" notice and keeps going — that notice is expected, not a crash.

To add a key:

1. Get a free one at
   <https://fred.stlouisfed.org/docs/api/api_key.html> (takes about a minute).
2. Create a file named `.env` in the project root — the same folder as
   `main.py` — containing one line:

```text
FRED_API_KEY=your_key_here
```

3. Run the script again. There is nothing else to restart.

`.env` is already listed in `.gitignore`, so your key will not be committed to
git. Never paste your key directly into a `.py` file.

Even without a key you can still ask FRED what series are available — see
"Listing what is available" below.

## Run The Demo

Run the `main.py` file at the project root.

In PyCharm, right-click `main.py` and choose **Run 'main'**.

From the terminal, run:

```bash
python main.py
```

What to expect:

- Numbered progress messages in the PyCharm Run window or terminal.
- A table of annualized factor statistics.
- **A chart window opens.** The script is not finished until you close that
  window — this is normal, not a freeze.
- The same chart is saved to your Desktop as `ff5_growth_of_dollar.png`.

The demo is designed to show how `DataDefinition`, the data source modules, and
the utility functions work together.

If a live download fails — no FRED key, Yahoo Finance having a bad day, no
internet — the script explains the problem, skips that piece, and still draws
and saves the chart with whatever data it got. A note on the chart itself says
what is missing.

### Configuration

The settings at the top of `main.py` are the first things worth changing:

| Setting | Meaning |
| --- | --- |
| `START_DATE` | Beginning of the analysis window (default `'1990-01-01'`) |
| `END_DATE` | End of the window; `None` means most recent available |
| `SAVE_FIGURE` | Set to `False` to display the chart without saving a file |
| `FIGURE_PATH` | Where the image is written (your Desktop by default) |
| `FREQ` | Periods per year for annualizing, `252` for daily data |

### Troubleshooting

| What you see | What it means |
| --- | --- |
| `Matplotlib is building the font cache; this may take a moment.` | Normal on the first run only. Wait a few seconds. |
| `Heads up: this part of the demo was skipped.` | An optional download failed. The chart still appears. Read the suggestions printed underneath. |
| `ModuleNotFoundError` | The requirements are not installed in the interpreter PyCharm is using. Redo step 4 of Setup. |
| The script seems stuck after step 8 | The chart window is open, possibly behind PyCharm. Close it to finish. |

## The Learn_To_Code Workbooks

`Learn_To_Code/` holds four notebooks. They are **workbooks, not lectures**: you
read a little, run a little, then fill in the gaps yourself and have your answer
checked. Work through them in order — each one assumes the one before it.

| # | Notebook | What it teaches | Exercises |
| - | -------- | --------------- | --------- |
| 1 | Coding Essentials | variables and types, f-strings, lists and dicts, `if`/`for`/`while`, comprehensions, functions, reading tracebacks, NumPy and vectorisation, pandas, classes, imports | 13 |
| 2 | Plotting some data | one figure revised ten times — labels, legends, colour, scales, annotation; then scatter, histogram, bar, small multiples, twin axes, a house style, and saving properly | 7 |
| 3 | Regression | OLS by hand in NumPy — design matrix, `(X'X)⁻¹X'y`, residuals, R², standard errors, t-stats — then `statsmodels`, formulas, robust and HAC errors, dummies and interactions, rolling windows | 10 |
| 4 | Monte Carlo Simulation | seeded randomness, estimating a probability from a card deck, checking it against exact combinatorics, the standard error of a simulation, vectorising 100,000 trials, bankroll paths and risk of ruin | 9 |

The topics deliberately do not overlap. Notebook 1 contains no plotting,
notebook 2 no statistics, notebook 3 no simulation.

### Running them

Install the requirements (step 4 of Setup above), then from the project root:

```bash
python -m jupyter lab
```

That opens a browser tab. Navigate into `Learn_To_Code/` and open notebook 1.

PyCharm Professional opens `.ipynb` files directly, so you can also just
double-click the file in the project tree. PyCharm Community cannot, so use the
command above.

`Shift + Enter` runs the current cell and moves to the next one. Run the cells in
order, top to bottom — a notebook remembers everything you have run, so a cell
can fail simply because you skipped the one above it. When things get confusing,
**Kernel → Restart Kernel and Run All Cells**.

### How the exercises work

Every section ends with a **Your turn** cell containing gaps and a check:

```python
ticker = todo()          # <- replace this with your answer
shares = todo()

check('1.1', ticker, shares)
```

Run it and you get either

```text
✅  Exercise 1.1 — correct.
```

or a specific explanation of what is wrong — not just "incorrect", but
`shares should be an int, you gave float (250.0)`. Three helpers, all imported by
the setup cell at the top of each notebook:

| Helper | Does |
| ------ | ---- |
| `check('1.1', ...)` | grades your answer and says what is wrong |
| `hint('1.1')` | a nudge, without grading anything |
| `todo()` | the placeholder you replace. It absorbs whatever you do to it, so a half-finished cell still runs down to its check instead of stopping on a traceback |

The grader lives in `Learn_To_Code/workbook.py`. Nothing in it is magic — it is a
dictionary of small functions that look at your answer. You are welcome to read
it, though doing so is a slower way to find the answers than just trying them.

### About the data

**Nothing is written into the project folder.** The workbooks read two CSV files
that live on your Desktop:

```text
~/Desktop/Coding_BootCamp_Data/
├── stock_prices.csv     # simulated daily panel (notebooks 1 and 2)
└── factor_data.csv      # simulated monthly factors (notebook 3)
```

The setup cell at the top of every notebook calls `ensure_data()`, which builds
them the first time and then leaves them alone. Delete that folder whenever you
like — it rebuilds on the next run, and because the random seeds are fixed you get
byte-identical files back. Nothing generated ever ends up in git. The same applies
to the figures you save in notebook 2 and the chart `main.py` writes: Desktop, not
the repository.

The data is **simulated, not real**: six fictional companies, three fictional
funds, invented factor returns. That is deliberate. Simulated data has true
parameters that are written down, so in notebook 3 you can fit a regression and
check whether your code recovered the values that actually generated the data. You
cannot do that with real data, and it is the fastest way to discover that your
regression is subtly wrong. `Learn_To_Code/generate_data.py` shows exactly how the
files are built and lists the true parameters.

To rebuild the data by hand at any point:

```bash
python Learn_To_Code/generate_data.py
```

When you want real data, use `DataDefinition` — see the next section. Notebooks 3
and 4 end by pointing you at it.

### If a notebook will not start

| What you see | What it means |
| ------------ | ------------- |
| `ModuleNotFoundError: No module named 'workbook'` | the notebook has been moved away from `workbook.py`. They have to stay in the same folder. |
| `ModuleNotFoundError: No module named 'statsmodels'` | the requirements are not installed in the interpreter Jupyter is using. Redo step 4 of Setup. |
| `FileNotFoundError` on a CSV | run the setup cell at the top of the notebook — `ensure_data()` rebuilds the files. |
| every exercise says "you left the placeholder in place" | that is correct — you have not filled them in yet. |

## How Data Access Works

`Data/data_definition.py` contains the `DataDefinition` class. This is the main
entry point for requesting data:

```python
from Data.data_definition import DataDefinition

# Fama-French 5-Factor daily data
ff5 = DataDefinition(
    source="famafrench",
    item="F-F_Research_Data_5_Factors_2x3_daily",
    start="2000-01-01",
    end=None,
).extract()

# Yahoo Finance closing prices
spy = DataDefinition(
    source="yfin",
    item="SPY",
    start="2000-01-01",
    end=None,
).extract()

# FRED data; requires FRED_API_KEY for the live API request
recessions = DataDefinition(
    source="fred",
    item="USRECD",
    start="2000-01-01",
    end=None,
).extract()
```

**Important:** the download happens when you *create* the object, not when you
call `.extract()`. So in this two-line version:

```python
dd = DataDefinition(source="fred", item="USRECD", start="2000-01-01", end=None)
data = dd.extract()          # instant; just hands back what was already fetched
```

the first line is the slow network call, and the first line is where a missing
API key or a broken connection will raise an error. `.extract()` only returns
the data that is already in memory.

Supported data sources live in `Data/sources/`:

| Source | Module | Purpose |
| --- | --- | --- |
| `famafrench` | `Data/sources/famafrench.py` | Fama-French factor and portfolio data |
| `fred` | `Data/sources/fred.py` | Federal Reserve Economic Data |
| `yfin` | `Data/sources/yfin.py` | Yahoo Finance prices through `yfinance` |

### Listing what is available

Pass `item=None` and the source tells you what it offers instead of downloading
a dataset. This works for FRED **without** an API key:

```python
# Every Fama-French dataset name you can request (a list of strings)
names = DataDefinition(source="famafrench", item=None, start=None, end=None).extract()

# Commonly used FRED series, as {series_id: description} — no API key needed
series = DataDefinition(source="fred", item=None, start=None, end=None).extract()

# Common Yahoo Finance tickers, as {ticker: description}
tickers = DataDefinition(source="yfin", item=None, start=None, end=None).extract()
```

### What each source gives you back

**Fama-French** returns a `DataFrame` with one column per factor. The values
are in **percentage points, not decimals** — a value of `0.53` means 0.53%, not
53%. Divide by 100 before doing any return math:

```python
ff5 = ff5 / 100.0        # now 0.0053, a true decimal return
```

Forgetting this is the single most common bug in this project: it makes
annualized returns and Sharpe ratios come out roughly 100 times too large.
`main.py` does this conversion for you in step 2.

**FRED** returns a `DataFrame` with a date index and a single column named
after the series you asked for. For `USRECD`, the value is `1` during an NBER
recession and `0` otherwise.

**Yahoo Finance** returns a single pandas **`Series`** — not a DataFrame — of
adjusted close prices, named after the ticker and indexed by date. It falls
back to unadjusted close if adjusted close is unavailable. One ticker at a time
through `DataDefinition`; for several at once, use the module directly:

```python
from Data.sources.yfin import get_multiple_close

prices = get_multiple_close(["SPY", "QQQ", "TLT"], start="2020-01-01")
```

## Utilities

`Utilities/tools.py` contains helper functions used by the demo:

| Function | What it does |
| --- | --- |
| `compute_levels_from_returns` | Turns a return series into growth of $1 |
| `compute_returns_from_levels` | The reverse: prices or levels into returns |
| `return_descriptor` | Annualized mean, vol, Sharpe, skew, kurtosis |
| `convert_daily_to_weekly` | Resamples daily data to weekly (Friday) |
| `generate_date_list` | Builds a list of dates at a chosen frequency |

There are also data-cleaning helpers you may need later — `fill_interior`,
`ffill_na`, `fillna_random`, `find_beg_end_dataframe`, and
`find_beg_end_series` — for handling missing values and trimming ragged date
ranges. Read the docstrings in `Utilities/tools.py` before using them.

Import only what you need:

```python
from Utilities.tools import compute_levels_from_returns, return_descriptor
```

Note that `return_descriptor` takes a `freq` argument: the number of periods
per year used for annualizing. Use `252` for daily data, `52` for weekly, and
`12` for monthly.

## Adding A New Data Source

To add another source later:

1. Create a new module in `Data/sources/`.
2. Add the import and routing logic in `Data/data_definition.py`.
3. Use the new source through `DataDefinition(source="your_source", ...)`.

Keep source modules focused on downloading/parsing data, and keep calculations
in `Utilities/tools.py` or your exercise files.
