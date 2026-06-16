"""
main.py
-------
Bootcamp demonstration script.

What this script does
---------------------
1. Downloads the Fama-French 5-Factor daily returns (Mkt-RF, SMB, HML,
   RMW, CMA) via the ``DataDefinition`` class.
2. Converts the percentage returns to decimal and computes the growth of
   $1 invested in each factor since the start of the sample.
3. Downloads the NBER recession indicator (daily) from FRED and shades
   recession periods on the chart.
4. Downloads the VIX from Yahoo Finance and plots it in a second panel.
5. Saves the figure as ``outputs/ff5_growth_of_dollar.png``.

Run
---
    python main.py

Dependencies
------------
    pip install -r requirements.txt
"""

import warnings
warnings.filterwarnings('ignore')

import os
import sys
import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
os.environ.setdefault(
    'MPLCONFIGDIR',
    str(Path(tempfile.gettempdir()) / 'coding_bootcamp_matplotlib'),
)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# ── project imports ────────────────────────────────────────────────────────
from Utilities.tools import (
    compute_levels_from_returns,
    return_descriptor,
)

# ── configuration ──────────────────────────────────────────────────────────
START_DATE  = '1990-01-01'   # beginning of the analysis window
END_DATE    = None            # None  →  most recent available data
SAVE_FIGURE = True
FIGURE_PATH = PROJECT_DIR / 'outputs' / 'ff5_growth_of_dollar.png'
FREQ        = 252             # trading days per year (for annualisation)

FACTOR_COLORS = {
    'Mkt-RF': '#1f77b4',   # blue
    'SMB':    '#ff7f0e',   # orange
    'HML':    '#2ca02c',   # green
    'RMW':    '#d62728',   # red
    'CMA':    '#9467bd',   # purple
}

FACTOR_LABELS = {
    'Mkt-RF': 'Market (Mkt-RF)',
    'SMB':    'Size (SMB)',
    'HML':    'Value (HML)',
    'RMW':    'Profitability (RMW)',
    'CMA':    'Investment (CMA)',
}


# ===========================================================================
# Helper functions
# ===========================================================================

class DemoDataError(Exception):
    """Friendly exception for problems students can usually fix."""

    def __init__(self, message, suggestions=None, detail=None):
        super().__init__(message)
        self.suggestions = suggestions or []
        self.detail = detail


def unique_suggestions(suggestions):
    """Keep the printed guidance short and avoid repeated tips."""
    result = []
    for suggestion in suggestions:
        if suggestion not in result:
            result.append(suggestion)
    return result


def guidance_for_error(source, error):
    """Translate common live-data errors into classroom-friendly guidance."""
    text = str(error)
    lower_text = text.lower()
    suggestions = []

    network_words = [
        'connection',
        'connecttimeout',
        'failed to establish',
        'name resolution',
        'network',
        'read timed out',
        'timeout',
        'temporarily unavailable',
        'urlopen error',
    ]
    if any(word in lower_text for word in network_words):
        suggestions.append(
            "Check your internet connection, then press Run again."
        )

    if isinstance(error, ModuleNotFoundError):
        suggestions.append(
            "Install the project dependencies in your Python environment."
        )
        suggestions.append(
            "In PyCharm, confirm this run configuration is using the boot camp interpreter."
        )

    if source == 'fred' or 'fred_api_key' in lower_text:
        suggestions.append(
            "For FRED, add a real FRED_API_KEY before running this live-data demo."
        )
        suggestions.append(
            "The FRED key goes in the project credential setup used by your class."
        )

    if 'credentials' in lower_text:
        suggestions.append(
            "Make sure the project credential file exists and contains the class FRED setup."
        )

    if source == 'yfin' or 'yahoo' in lower_text or 'yfinance' in lower_text:
        suggestions.append(
            "Yahoo Finance can be temporarily unavailable; wait a minute and try again."
        )
        suggestions.append(
            "If Yahoo keeps failing, update yfinance and confirm the ticker is ^VIX."
        )

    if source == 'famafrench' or 'fama' in lower_text or 'french' in lower_text:
        suggestions.append(
            "Fama-French data comes from a live Dartmouth download, so it needs internet access."
        )

    if 'could not import' in lower_text or 'cannot import' in lower_text:
        suggestions.append(
            "A data-source file may be missing or mid-edit; try again after the data layer is fixed."
        )

    if not suggestions:
        suggestions.append(
            "Read the technical detail below, fix the setup issue, and press Run again."
        )

    return unique_suggestions(suggestions)


def print_intro():
    print("\nFama-French boot camp demo")
    print("--------------------------------")
    print("This script downloads live data, computes factor statistics,")
    print("and saves a chart with recession shading and the VIX.")


def print_done(message):
    print(f"   Done: {message}")


def print_friendly_error(error):
    print("\nThe demo stopped before the chart could be created.")
    print(f"Problem: {error}")

    if error.suggestions:
        print("\nWhat to try:")
        for suggestion in error.suggestions:
            print(f"  - {suggestion}")

    if error.detail is not None:
        print(
            f"\nTechnical detail: "
            f"{type(error.detail).__name__}: {error.detail}"
        )

    print("\nAfter fixing that, press Run again.")


def get_data_definition_class():
    """Import the data loader only when the demo starts running."""
    try:
        from Data.data_definition import DataDefinition
    except Exception as error:
        raise DemoDataError(
            "The project data loader could not start.",
            guidance_for_error('setup', error),
            error,
        ) from error
    return DataDefinition


def load_live_data(data_definition_class, source, item, label):
    """Load one live dataset and convert common failures to friendly messages."""
    try:
        data = data_definition_class(
            source=source,
            item=item,
            start=START_DATE,
            end=END_DATE,
        ).extract()
    except Exception as error:
        raise DemoDataError(
            f"Could not download {label}.",
            guidance_for_error(source, error),
            error,
        ) from error

    if data is None:
        raise DemoDataError(
            f"{label} returned no data.",
            [
                "Confirm the data source name and item are correct.",
                "Try the download again; live sources sometimes return an empty response.",
            ],
        )

    return data


def describe_time_series(data):
    """Return a short row-count/date-range description for console output."""
    if isinstance(data, (pd.DataFrame, pd.Series)) and not data.empty:
        index = data.index
        if isinstance(index, pd.DatetimeIndex):
            start = index.min().date()
            end = index.max().date()
            return f"{len(data):,} rows ({start} to {end})"
        return f"{len(data):,} rows"
    return "no rows"


def ensure_datetime_index(data, label):
    """Make sure a Series or DataFrame has a usable date index."""
    data = data.copy()

    if not isinstance(data.index, pd.DatetimeIndex):
        try:
            data.index = pd.to_datetime(data.index)
        except Exception as error:
            raise DemoDataError(
                f"{label} did not have dates in a format pandas could read.",
                [
                    "Check that the data source returned a table indexed by date.",
                    "Try running again after the data layer is fixed.",
                ],
                error,
            ) from error

    if data.index.isna().any():
        raise DemoDataError(
            f"{label} included blank or invalid dates.",
            ["Check the live data response before building the chart."],
        )

    return data.sort_index()


def prepare_ff5_data(ff5_raw):
    """Validate and clean the Fama-French factor returns."""
    if not isinstance(ff5_raw, pd.DataFrame):
        raise DemoDataError(
            "Fama-French returned an unexpected data shape.",
            ["Expected a pandas DataFrame with the five factor columns."],
        )

    ff5_raw = ensure_datetime_index(ff5_raw, "Fama-French data")
    factors = list(FACTOR_COLORS.keys())
    missing = [factor for factor in factors if factor not in ff5_raw.columns]
    if missing:
        raise DemoDataError(
            "Fama-French data is missing required factor columns.",
            [
                f"Missing columns: {', '.join(missing)}.",
                "The demo expects Mkt-RF, SMB, HML, RMW, and CMA.",
            ],
        )

    ff5 = ff5_raw[factors].apply(pd.to_numeric, errors='coerce') / 100.0
    ff5.dropna(how='all', inplace=True)

    if ff5.empty:
        raise DemoDataError(
            "Fama-French returned no usable factor rows.",
            ["Check the date range and try the live download again."],
        )
    if ff5.dropna().empty:
        raise DemoDataError(
            "Fama-French factor rows were all incomplete after cleaning.",
            ["Check whether the live response was malformed or partially downloaded."],
        )

    return ff5


def prepare_recession_data(usrecd_raw):
    """Validate and clean the FRED recession indicator."""
    if isinstance(usrecd_raw, pd.Series):
        usrecd = usrecd_raw.to_frame(name=usrecd_raw.name or 'USRECD')
    elif isinstance(usrecd_raw, pd.DataFrame):
        usrecd = usrecd_raw.copy()
    else:
        raise DemoDataError(
            "FRED returned an unexpected data shape.",
            ["Expected a pandas Series or DataFrame for USRECD."],
        )

    usrecd = ensure_datetime_index(usrecd, "FRED recession data")
    if 'USRECD' in usrecd.columns:
        col = 'USRECD'
    elif len(usrecd.columns) == 1:
        col = usrecd.columns[0]
    else:
        raise DemoDataError(
            "FRED recession data had too many columns.",
            ["The demo expects a single USRECD recession-indicator column."],
        )

    usrecd = usrecd[[col]].rename(columns={col: 'USRECD'})
    usrecd['USRECD'] = pd.to_numeric(usrecd['USRECD'], errors='coerce')
    usrecd.dropna(how='all', inplace=True)

    if usrecd.empty:
        raise DemoDataError(
            "FRED returned no usable USRECD rows.",
            ["Check the FRED key and try the live download again."],
        )

    return usrecd


def prepare_vix_data(vix_raw):
    """Validate and clean the Yahoo Finance VIX series."""
    if isinstance(vix_raw, pd.Series):
        vix = vix_raw.copy()
    elif isinstance(vix_raw, pd.DataFrame):
        if '^VIX' in vix_raw.columns:
            vix = vix_raw['^VIX'].copy()
        elif 'Close' in vix_raw.columns:
            vix = vix_raw['Close'].copy()
        elif len(vix_raw.columns) == 1:
            vix = vix_raw.iloc[:, 0].copy()
        else:
            raise DemoDataError(
                "Yahoo Finance returned too many VIX columns.",
                ["The demo expects one VIX close-price series."],
            )
    else:
        raise DemoDataError(
            "Yahoo Finance returned an unexpected data shape.",
            ["Expected a pandas Series or one-column DataFrame for ^VIX."],
        )

    vix = ensure_datetime_index(vix, "VIX data")
    vix = pd.to_numeric(vix, errors='coerce').rename('^VIX').dropna()

    if vix.empty:
        raise DemoDataError(
            "Yahoo Finance returned no usable VIX rows.",
            ["Try again later or confirm that the ^VIX ticker is available."],
        )

    return vix


def align_plot_data(levels, usrecd, vix):
    """Trim recession and VIX data to the factor-data date range."""
    if levels.empty:
        raise DemoDataError(
            "The factor growth table is empty.",
            ["Check the Fama-French download before plotting."],
        )

    t0, t1 = levels.index[0], levels.index[-1]
    usrecd_plot = usrecd.loc[t0:t1]
    vix_plot = vix.loc[t0:t1]

    if usrecd_plot.empty:
        raise DemoDataError(
            "The recession data does not overlap the Fama-French date range.",
            ["Check the FRED response and the START_DATE/END_DATE settings."],
        )
    if vix_plot.empty:
        raise DemoDataError(
            "The VIX data does not overlap the Fama-French date range.",
            ["Check the Yahoo response and the START_DATE/END_DATE settings."],
        )

    return usrecd_plot, vix_plot


def shade_recessions(ax, usrecd: pd.DataFrame):
    """Draw grey shading over NBER recession periods on *ax*.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    usrecd : pd.DataFrame
        Single-column DataFrame with the USRECD series (1 = recession).
    """
    if usrecd.empty:
        return

    col          = usrecd.columns[0]
    in_recession = False
    rec_start    = None

    for date, val in usrecd[col].items():
        if val == 1 and not in_recession:
            in_recession = True
            rec_start    = date
        elif val == 0 and in_recession:
            in_recession = False
            ax.axvspan(rec_start, date, color='grey', alpha=0.15,
                       zorder=0, label='_nolegend_')

    # Handle data that ends mid-recession
    if in_recession and rec_start is not None:
        ax.axvspan(rec_start, usrecd.index[-1], color='grey', alpha=0.15,
                   zorder=0, label='_nolegend_')


# ===========================================================================
# Main routine
# ===========================================================================

def main():
    print_intro()

    try:
        print("\n1. Starting the boot camp data loader...")
        data_definition_class = get_data_definition_class()
        print_done("Data loader is ready.")

        # -------------------------------------------------------------------
        # 2.  Fama-French 5-Factor daily returns
        # -------------------------------------------------------------------
        print("\n2. Downloading Fama-French 5-Factor daily returns...")
        ff5_raw = load_live_data(
            data_definition_class,
            source='famafrench',
            item='F-F_Research_Data_5_Factors_2x3_daily',
            label='Fama-French 5-Factor daily returns',
        )
        ff5 = prepare_ff5_data(ff5_raw)
        print_done(f"Loaded {describe_time_series(ff5)}.")
        print("   Converted percentage returns to decimal returns.")

        # -------------------------------------------------------------------
        # 3.  Growth of $1
        # -------------------------------------------------------------------
        print("\n3. Computing growth of $1 for each factor...")
        try:
            levels = compute_levels_from_returns(ff5)
        except Exception as error:
            raise DemoDataError(
                "Could not compute growth of $1 from the factor returns.",
                ["Check that the Fama-French columns are numeric return series."],
                error,
            ) from error
        print_done(f"Built a growth table with {len(levels):,} dates.")

        # -------------------------------------------------------------------
        # 4.  Descriptive statistics
        # -------------------------------------------------------------------
        print("\n4. Computing annualized factor statistics...")
        try:
            stats = return_descriptor(ff5.dropna(), freq=FREQ)
        except Exception as error:
            raise DemoDataError(
                "Could not compute the factor summary statistics.",
                ["Check that the cleaned factor data has complete numeric rows."],
                error,
            ) from error

        pd.set_option('display.float_format', '{:.4f}'.format)
        print("\nAnnualized factor statistics")
        print("--------------------------------")
        print(stats.loc[['Annualized mu', 'Annualized std', 'Sharpe',
                          'skewness', 'kurtosis']].to_string())

        # -------------------------------------------------------------------
        # 5.  NBER recession indicator from FRED
        # -------------------------------------------------------------------
        print("\n5. Downloading NBER recession data from FRED...")
        usrecd_raw = load_live_data(
            data_definition_class,
            source='fred',
            item='USRECD',
            label='NBER recession indicator from FRED',
        )
        usrecd = prepare_recession_data(usrecd_raw)
        print_done(f"Loaded {describe_time_series(usrecd)}.")

        # -------------------------------------------------------------------
        # 6.  VIX from Yahoo Finance
        # -------------------------------------------------------------------
        print("\n6. Downloading VIX from Yahoo Finance...")
        vix_raw = load_live_data(
            data_definition_class,
            source='yfin',
            item='^VIX',
            label='VIX from Yahoo Finance',
        )
        vix = prepare_vix_data(vix_raw)
        print_done(f"Loaded {describe_time_series(vix)}.")

        # -------------------------------------------------------------------
        # 7.  Align date ranges to the FF5 window
        # -------------------------------------------------------------------
        print("\n7. Aligning all data to the Fama-French date range...")
        usrecd_plot, vix_plot = align_plot_data(levels, usrecd, vix)
        t0, t1 = levels.index[0], levels.index[-1]
        print_done(f"Chart window is {t0.date()} to {t1.date()}.")

        # -------------------------------------------------------------------
        # 8.  Plot
        # -------------------------------------------------------------------
        print("\n8. Building the chart...")
        try:
            fig = plt.figure(figsize=(15, 9))
            gs  = GridSpec(2, 1, figure=fig,
                           height_ratios=[3, 1],
                           hspace=0.04)          # tiny gap between panels

            ax_top = fig.add_subplot(gs[0])
            ax_bot = fig.add_subplot(gs[1], sharex=ax_top)

            # ── Top panel: Growth of $1 ──────────────────────────────────
            for factor, color in FACTOR_COLORS.items():
                ax_top.plot(
                    levels.index,
                    levels[factor],
                    label=FACTOR_LABELS[factor],
                    color=color,
                    linewidth=1.4,
                    alpha=0.9,
                )

            shade_recessions(ax_top, usrecd_plot)

            ax_top.set_yscale('log')
            ax_top.set_ylabel('Growth of $1  (log scale)', fontsize=12)
            ax_top.set_title(
                'Fama-French 5 Factors — Growth of $1 with NBER Recession Shading',
                fontsize=14, fontweight='bold', pad=12,
            )
            ax_top.grid(True, which='both', alpha=0.25, linestyle='--')
            ax_top.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda y, _: f'${y:.2f}')
            )

            # Build a custom legend that includes the recession patch
            rec_patch = mpatches.Patch(
                color='grey',
                alpha=0.35,
                label='NBER Recession',
            )
            handles, labels_ = ax_top.get_legend_handles_labels()
            ax_top.legend(handles + [rec_patch], labels_ + ['NBER Recession'],
                          loc='upper left', fontsize=10, framealpha=0.9)

            # Share x-axis with bottom panel
            plt.setp(ax_top.get_xticklabels(), visible=False)

            # ── Bottom panel: VIX ───────────────────────────────────────
            ax_bot.fill_between(vix_plot.index, vix_plot.to_numpy(),
                                color='#7f7f7f', alpha=0.5, label='VIX')
            ax_bot.plot(vix_plot.index, vix_plot.to_numpy(),
                        color='black', linewidth=0.8, alpha=0.8)

            shade_recessions(ax_bot, usrecd_plot)

            # Annotate notable VIX spikes
            notable = {
                '2008-11-20': 'GFC',
                '2020-03-18': 'COVID',
            }
            for date_str, label in notable.items():
                dt = pd.Timestamp(date_str)
                if dt in vix_plot.index:
                    spike = vix_plot.loc[dt]
                    ax_bot.annotate(
                        label,
                        xy=(dt, spike),
                        xytext=(0, 10),
                        textcoords='offset points',
                        fontsize=8,
                        ha='center',
                        arrowprops=dict(arrowstyle='->', color='black', lw=0.8),
                    )

            ax_bot.set_ylabel('VIX', fontsize=12)
            ax_bot.set_xlabel('Date', fontsize=12)
            ax_bot.set_ylim(bottom=0)
            ax_bot.grid(True, alpha=0.25, linestyle='--')
            ax_bot.legend(loc='upper left', fontsize=10, framealpha=0.9)

            # ── Save & show ──────────────────────────────────────────────
            plt.tight_layout()

            if SAVE_FIGURE:
                FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(FIGURE_PATH, dpi=150, bbox_inches='tight')
                plt.close(fig)
                print_done(f"Chart saved to {FIGURE_PATH}")
            else:
                print_done("Chart is ready to display.")
                plt.show()

        except Exception as error:
            raise DemoDataError(
                "Could not build or save the chart.",
                [
                    "Check that the cleaned FF5, FRED, and VIX data all have dates.",
                    "If saving failed, confirm the project folder is writable.",
                ],
                error,
            ) from error

        print("\nSuccess! The demo finished.")
        if SAVE_FIGURE:
            print(f"Open the chart here: {FIGURE_PATH}")
        return 0

    except DemoDataError as error:
        print_friendly_error(error)
        return 1
    except Exception as error:
        print_friendly_error(
            DemoDataError(
                "Something unexpected happened while running the demo.",
                [
                    "Check the technical detail below.",
                    "If you are in class, ask the instructor to review main.py.",
                ],
                error,
            )
        )
        return 1


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    sys.exit(main())
