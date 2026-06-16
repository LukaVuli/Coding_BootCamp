# Coding Bootcamp Starter Repo

This repository is the baseline codebase for the coding boot camp. The first
student workflow is simple: open the project in PyCharm, select a Python
interpreter, install the requirements, and run the root `main.py` file.

## Project Layout

```text
Coding_BootCamp/
├── main.py                     # Demo script to run first
├── requirements.txt            # Python package requirements
├── credentials.py              # Loads optional environment variables
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

You do not need a `FRED_API_KEY` just to open the repo, import most modules, or
work with non-FRED examples. A FRED API key is only needed when you make live
requests to the FRED API, such as pulling the NBER recession series.

If you need live FRED data, create a `.env` file in the project root:

```text
FRED_API_KEY=your_key_here
```

Free keys are available from the FRED API documentation.

## Run The Demo

Run the `main.py` file at the project root.

In PyCharm, right-click `main.py` and choose **Run 'main'**.

From the terminal, run:

```bash
python main.py
```

You should see progress messages and printed output in the PyCharm Run window
or terminal. The demo is designed to show how `DataDefinition`, the data source
modules, and the utility functions work together. When the live downloads
succeed, the chart is saved to `outputs/ff5_growth_of_dollar.png`.

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

Supported data sources live in `Data/sources/`:

| Source | Module | Purpose |
| --- | --- | --- |
| `famafrench` | `Data/sources/famafrench.py` | Fama-French factor and portfolio data |
| `fred` | `Data/sources/fred.py` | Federal Reserve Economic Data |
| `yfin` | `Data/sources/yfin.py` | Yahoo Finance prices through `yfinance` |

## Utilities

`Utilities/tools.py` contains helper functions used by the demo, including:

- `compute_levels_from_returns`
- `compute_returns_from_levels`
- `return_descriptor`
- `convert_daily_to_weekly`
- `generate_date_list`

Import only what you need:

```python
from Utilities.tools import compute_levels_from_returns, return_descriptor
```

## Adding A New Data Source

To add another source later:

1. Create a new module in `Data/sources/`.
2. Add the import and routing logic in `Data/data_definition.py`.
3. Use the new source through `DataDefinition(source="your_source", ...)`.

Keep source modules focused on downloading/parsing data, and keep calculations
in `Utilities/tools.py` or your exercise files.
