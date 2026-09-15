"""
generate_data.py
----------------
Builds the two CSV files the workbooks read.

**You never need to run this yourself.** The first notebook cell you execute
calls ``ensure_data()`` in ``workbook.py``, which runs this once and then leaves
it alone. This file is here so you can see exactly where the data came from.

Nothing is written into the project folder. The CSVs land in

    ~/Desktop/Coding_BootCamp_Data/

so the repository stays clean and nothing you generate ends up in git. Delete
that folder any time you like; it rebuilds itself on the next notebook run, and
because the random seeds are fixed you get byte-identical files back.

The data is SIMULATED, not real. No file contains real prices, real funds, or
real Fama-French factors. Simulated data has one big teaching advantage: we know
the true answer, so when you run a regression in notebook 3 you can check your
estimates against the parameters that actually generated the data. That is
impossible with real data.

When you want real data, use the ``DataDefinition`` class at the project root
(see the main README) — the workbooks show you how at the end.

Files produced
--------------
stock_prices.csv   Daily prices and volume for six fictional companies,
                   2021-01-04 to 2023-12-29, in long ("tidy") format.
                   Used by notebooks 1 and 2.

factor_data.csv    Monthly factor returns and three fictional fund returns,
                   2004-01 to 2023-12. Used by notebook 3.

True parameters behind factor_data.csv (decimal, per month)
-----------------------------------------------------------
                 alpha     mkt_rf    smb     hml    extra mkt beta   resid sd
                                                     in recessions
growth_fund      0.0020    0.90     -0.20   -0.40      +0.50          0.015
value_fund       0.0000    1.05      0.30    0.60       0.00          0.018
index_fund      -0.0002    1.00      0.02    0.00       0.00          0.002

Run with:  python generate_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

FOLDER_NAME = 'Coding_BootCamp_Data'


def default_out_dir() -> Path:
    """Where the workbook data lives: a folder on the user's Desktop.

    ``Path.home()`` resolves to the current user's home folder on macOS,
    Windows and Linux, so nothing here is tied to one machine. If there is no
    Desktop (some Linux setups, a OneDrive-redirected Windows profile), fall
    back to the home folder itself.
    """
    desktop = Path.home() / 'Desktop'
    base = desktop if desktop.is_dir() else Path.home()
    return base / FOLDER_NAME

# ---------------------------------------------------------------------------
# 1. Daily prices for six fictional companies  ->  stock_prices.csv
# ---------------------------------------------------------------------------

COMPANIES = {
    #  ticker : (sector,      start price, annual drift, idio vol, market beta)
    'ACME': ('Technology', 142.00, 0.16, 0.26, 1.25),
    'BOLT': ('Technology', 88.50, 0.04, 0.22, 1.00),
    'CRUX': ('Energy', 61.25, 0.08, 0.24, 0.80),
    'DYNE': ('Energy', 34.80, -0.06, 0.30, 0.95),
    'EVER': ('Consumer', 205.40, 0.06, 0.14, 0.65),
    'FLUX': ('Consumer', 27.15, -0.12, 0.19, 0.75),
}

SECTOR_VOL = {'Technology': 0.13, 'Energy': 0.18, 'Consumer': 0.07}


def make_stock_prices(seed: int = 1234) -> pd.DataFrame:
    """Build the long-format daily price panel."""
    rng = np.random.default_rng(seed)
    rng_vol = np.random.default_rng(seed + 1)   # kept separate so that tweaking
                                                # volume never disturbs prices

    dates = pd.bdate_range('2021-01-04', '2023-12-29')
    n_days = len(dates)
    dt = 1.0 / 252.0

    # One shared market shock per day, plus one shock per sector per day.
    market = rng.normal(0.05 * dt, 0.15 * np.sqrt(dt), n_days)
    sector_shock = {
        s: rng.normal(0.0, v * np.sqrt(dt), n_days) for s, v in SECTOR_VOL.items()
    }

    frames = []
    for ticker, (sector, p0, drift, vol, beta) in COMPANIES.items():
        idio = rng.normal(0.0, vol * np.sqrt(dt), n_days)
        rets = drift * dt + beta * market + sector_shock[sector] + idio
        rets[0] = 0.0
        price = p0 * np.exp(np.cumsum(rets) - 0.5 * (vol ** 2) * dt * np.arange(n_days))

        # Volume: log-normal, fatter on days with big absolute moves.
        base = rng_vol.lognormal(mean=14.2, sigma=0.35, size=n_days)
        volume = base * (1.0 + 6.0 * np.abs(rets))

        frames.append(pd.DataFrame({
            'date': dates,
            'ticker': ticker,
            'sector': sector,
            'price': np.round(price, 2),
            'volume': np.round(volume, 0),
        }))

    panel = pd.concat(frames, ignore_index=True)
    panel = panel.sort_values(['date', 'ticker'], ignore_index=True)

    # A realistic amount of mess: a few missing volume readings.
    missing = rng_vol.choice(panel.index, size=17, replace=False)
    panel.loc[missing, 'volume'] = np.nan

    return panel


# ---------------------------------------------------------------------------
# 2. Monthly factors and funds  ->  factor_data.csv
# ---------------------------------------------------------------------------

FUNDS = {
    #  name          alpha    mkt    smb    hml   recession beta bump  resid sd
    'growth_fund': (0.0020, 0.90, -0.20, -0.40, 0.50, 0.015),
    'value_fund': (0.0000, 1.05, 0.30, 0.60, 0.00, 0.018),
    'index_fund': (-0.0002, 1.00, 0.02, 0.00, 0.00, 0.002),
}

# Month indices (0-based from 2004-01) that sit inside a simulated recession.
RECESSION_BLOCKS = [(47, 65), (194, 197)]


def make_factor_data(seed: int = 19630701, fund_seed: int = 18) -> pd.DataFrame:
    """Build the monthly factor + fund return table."""
    rng = np.random.default_rng(seed)
    rng_funds = np.random.default_rng(fund_seed)   # separate stream, so that
                                                   # editing one fund does not
                                                   # change the others

    dates = pd.date_range('2004-01-31', '2023-12-31', freq='ME')
    n = len(dates)

    recession = np.zeros(n)
    for lo, hi in RECESSION_BLOCKS:
        recession[lo:hi] = 1.0

    # Market is worse and more volatile in recessions.
    mkt_rf = rng.normal(0.0095, 0.040, n) - 0.030 * recession
    mkt_rf += rng.normal(0.0, 0.025, n) * recession
    smb = rng.normal(0.0010, 0.026, n)
    hml = rng.normal(0.0015, 0.029, n)

    # A slow-moving, non-negative short rate.
    rf = np.clip(0.0018 + np.cumsum(rng.normal(0.0, 0.00022, n)), 0.0, None)

    out = pd.DataFrame({
        'date': dates,
        'Mkt-RF': mkt_rf,
        'SMB': smb,
        'HML': hml,
        'RF': rf,
        'recession': recession.astype(int),
    })

    for name, (alpha, b_mkt, b_smb, b_hml, bump, sd) in FUNDS.items():
        excess = (alpha
                  + (b_mkt + bump * recession) * mkt_rf
                  + b_smb * smb
                  + b_hml * hml
                  + rng_funds.normal(0.0, sd, n))
        out[name] = np.round(rf + excess, 6)   # total return, not excess

    for col in ['Mkt-RF', 'SMB', 'HML', 'RF']:
        out[col] = out[col].round(6)

    return out


# ---------------------------------------------------------------------------

def write_datasets(out_dir=None) -> Path:
    """Write both CSVs into out_dir (the Desktop folder by default)."""
    out_dir = Path(out_dir) if out_dir is not None else default_out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    make_stock_prices().to_csv(out_dir / 'stock_prices.csv', index=False)
    make_factor_data().to_csv(out_dir / 'factor_data.csv', index=False)
    return out_dir


if __name__ == '__main__':
    written = write_datasets()
    print(f'Wrote workbook data to {written}')
    for f in sorted(written.glob('*.csv')):
        print(f'  {f.name:20s} {f.stat().st_size // 1024:>4} KB')
