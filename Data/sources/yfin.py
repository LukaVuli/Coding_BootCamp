"""
yfin.py
-------
Small Yahoo Finance helper module for beginner-friendly market data pulls.

The public source name in DataDefinition is still 'yfin'.  This module wraps
yfinance and normalizes the common output shapes into simple pandas objects.
"""

import warnings
warnings.filterwarnings('ignore')

from collections.abc import Iterable

import pandas as pd


COMMON_TICKERS = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "^VIX": "CBOE Volatility Index",
    "QQQ": "Invesco QQQ Trust",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "GLD": "SPDR Gold Shares",
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
}


def available_tickers():
    """Return a small quick-reference dict of common Yahoo Finance symbols."""
    return COMMON_TICKERS


def _load_yfinance():
    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError(
            "The yfinance package is required for source='yfin'. "
            "Install it with: pip install yfinance"
        ) from exc
    return yf


def _normalize_tickers(tickers):
    if isinstance(tickers, str):
        tickers = tickers.replace(",", " ").split()
    elif isinstance(tickers, Iterable):
        tickers = list(tickers)
    else:
        raise ValueError("tickers must be a ticker string or an iterable of strings.")

    clean = [str(ticker).strip() for ticker in tickers if str(ticker).strip()]
    if not clean:
        raise ValueError("Please provide at least one Yahoo Finance ticker.")
    return clean


def _column_for(data: pd.DataFrame, field: str, ticker: str):
    """Return a price column from common yfinance single/MultiIndex shapes."""
    if not isinstance(data.columns, pd.MultiIndex):
        return data[field] if field in data.columns else None

    columns = data.columns
    ticker_matches = [ticker, ticker.upper()]

    for key in [(field, ticker), (field, ticker.upper())]:
        if key in columns:
            return data.loc[:, key]

    for key in [(ticker, field), (ticker.upper(), field)]:
        if key in columns:
            return data.loc[:, key]

    for level in range(columns.nlevels):
        if field not in columns.get_level_values(level):
            continue
        sliced = data.xs(field, axis=1, level=level, drop_level=True)
        if isinstance(sliced, pd.Series):
            return sliced
        if isinstance(sliced, pd.DataFrame):
            for match in ticker_matches:
                if match in sliced.columns:
                    return sliced[match]
            if sliced.shape[1] == 1:
                return sliced.iloc[:, 0]

    return None


def get_close(ticker: str, start=None, end=None) -> pd.Series:
    """Download adjusted close or close prices for one Yahoo Finance ticker."""
    ticker = str(ticker).strip()
    if not ticker:
        raise ValueError("Please provide a Yahoo Finance ticker.")

    yf = _load_yfinance()
    data = yf.download(
        ticker,
        start=start,
        end=end,
        progress=False,
        auto_adjust=False,
    )

    if data is None or data.empty:
        raise ValueError(
            f"No Yahoo Finance data returned for '{ticker}'. "
            "Check the ticker symbol and date range."
        )

    close = _column_for(data, "Adj Close", ticker)
    if close is None:
        close = _column_for(data, "Close", ticker)

    if close is None:
        raise ValueError(
            f"Yahoo Finance returned data for '{ticker}', but no close price "
            "column was found."
        )

    close = pd.to_numeric(close, errors="coerce").dropna()
    if close.empty:
        raise ValueError(
            f"No usable close prices returned for '{ticker}'. "
            "Check the ticker symbol and date range."
        )

    close.index = pd.to_datetime(close.index)
    close.index.name = "Date"
    close.name = ticker
    return close


def get_multiple_close(tickers, start=None, end=None) -> pd.DataFrame:
    """Download close prices for multiple Yahoo Finance tickers."""
    series = [
        get_close(ticker, start=start, end=end)
        for ticker in _normalize_tickers(tickers)
    ]

    prices = pd.concat(series, axis=1)
    prices.index.name = "Date"
    return prices
