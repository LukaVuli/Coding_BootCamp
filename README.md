# Coding Bootcamp Starter Repo

This repository is the baseline codebase for the coding boot camp. The first
student workflow is simple: open the project in PyCharm, select a Python
interpreter, install the requirements, and run the root `main.py` file.

You need **Python 3.9 or newer** (3.11+ recommended).

## Project Layout

```text
Coding_BootCamp/
├── main.py                     # Demo script to run first
├── requirements.txt            # Python package requirements
├── credentials.py              # Loads optional environment variables
├── .gitignore                  # Keeps your .env out of git
├── LICENSE
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
