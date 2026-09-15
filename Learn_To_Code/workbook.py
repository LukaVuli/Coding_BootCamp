"""
workbook.py
-----------
The grading helper for the four Learn_To_Code notebooks.

You do not need to read this file to use the workbooks, but you are very
welcome to. There is nothing magic in here — it is a dictionary of small
functions that look at your answer and tell you whether it is right.

Two functions matter to you:

    check('1.4', my_answer)   ->  ✅ or ❌ with a specific explanation
    hint('1.4')               ->  a nudge in the right direction

Two more are useful:

    todo()                    ->  a placeholder you replace with your answer
    ensure_data()             ->  builds the workbook CSVs if they are missing

Nothing is ever written into the project folder. The data lives in
``~/Desktop/Coding_BootCamp_Data`` (see DATA_DIR), so the repository stays clean.
"""

from pathlib import Path

import numpy as np
import pandas as pd

import generate_data

HERE = Path(__file__).resolve().parent      # the Learn_To_Code folder
PROJECT_ROOT = HERE.parent                  # the repo root, for project imports
DATA_DIR = generate_data.default_out_dir()  # ~/Desktop/Coding_BootCamp_Data

# Registry: key -> (validator, hint). A validator takes the student's answer
# and returns None when it is correct, or a string explaining the problem.
_CHECKS: dict[str, tuple] = {}


def _register(key: str, hint_text: str):
    """Decorator that files a validator under an exercise key."""
    def decorator(fn):
        _CHECKS[key] = (fn, hint_text)
        return fn
    return decorator


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class _Todo:
    """Sentinel returned by todo().

    It absorbs whatever you do to it — attribute access, indexing, arithmetic,
    formatting — and hands back another placeholder. That way a half-finished
    exercise cell still runs all the way down to its check(), which tells you
    what is missing, instead of stopping at a traceback that tells you nothing.
    """

    _TEXT = '<still to do>'

    def __repr__(self):
        return self._TEXT

    def __str__(self):
        return self._TEXT

    def __format__(self, spec):
        return self._TEXT

    def __getattr__(self, name):
        # Let dunder lookups fail normally, so NumPy and pandas can still work
        # out that this is not an array.
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        return self

    def __getitem__(self, key):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return False


def _absorb(self, *args, **kwargs):
    return self


for _op in ('__add__', '__radd__', '__sub__', '__rsub__', '__mul__', '__rmul__',
            '__truediv__', '__rtruediv__', '__floordiv__', '__mod__', '__pow__',
            '__matmul__', '__rmatmul__', '__neg__', '__pos__', '__abs__',
            '__round__'):
    setattr(_Todo, _op, _absorb)


def todo():
    """Placeholder for an answer you have not written yet."""
    return _Todo()


REQUIRED_FILES = ('stock_prices.csv', 'factor_data.csv')


def ensure_data(rebuild: bool = False, quiet: bool = False) -> Path:
    """Make sure the workbook CSVs exist on your Desktop, and return the folder.

    Builds them the first time, then does nothing on later runs. Pass
    rebuild=True to force a fresh copy. Because the random seeds are fixed, a
    rebuild reproduces exactly the same files.
    """
    missing = [f for f in REQUIRED_FILES if not (DATA_DIR / f).exists()]

    if rebuild or missing:
        why = 'rebuilding' if rebuild else f'first run, building {len(missing)} file(s)'
        if not quiet:
            print(f'{why} -> {DATA_DIR}')
        generate_data.write_datasets(DATA_DIR)
        _CACHE.clear()

    return DATA_DIR


def check(key: str, *answer):
    """Grade one exercise and print the result.

    Parameters
    ----------
    key : str
        Exercise number, e.g. '1.4'.
    *answer
        Whatever the exercise asked you to produce.
    """
    if key not in _CHECKS:
        print(f"⚠️  There is no exercise {key}. Known: {', '.join(sorted(_CHECKS))}")
        return

    validator, hint_text = _CHECKS[key]

    for a in answer:
        if isinstance(a, _Todo) or a is Ellipsis:
            print(f"❌  Exercise {key} — you left the placeholder in place.")
            print(f"    💡 {hint_text}")
            return

    try:
        problem = validator(*answer)
    except TypeError as exc:
        if 'positional argument' in str(exc):
            print(f"❌  Exercise {key} — check() got {len(answer)} value(s); "
                  f"that is not what this exercise expects.")
            print(f"    💡 {hint_text}")
            return
        problem = f"your answer raised {type(exc).__name__}: {exc}"
    except Exception as exc:                                  # noqa: BLE001
        problem = f"your answer raised {type(exc).__name__}: {exc}"

    if problem is None:
        print(f"✅  Exercise {key} — correct.")
    else:
        print(f"❌  Exercise {key} — {problem}")
        print(f"    💡 {hint_text}")


def hint(key: str):
    """Print the hint for an exercise without grading anything."""
    if key not in _CHECKS:
        print(f"⚠️  There is no exercise {key}.")
        return
    print(f"💡  Exercise {key}: {_CHECKS[key][1]}")


def exercises(notebook: str | int | None = None):
    """List the exercise keys, optionally for one notebook only."""
    keys = sorted(_CHECKS, key=lambda k: [int(p) for p in k.split('.')])
    if notebook is not None:
        keys = [k for k in keys if k.startswith(f'{notebook}.')]
    return keys


# ---------------------------------------------------------------------------
# Small comparison helpers used by the validators
# ---------------------------------------------------------------------------

def _close(a, b, tol=1e-6):
    try:
        return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return False


def _kind(x):
    """A readable description of what the student actually handed over."""
    if isinstance(x, pd.DataFrame):
        return f'a DataFrame with shape {x.shape}'
    if isinstance(x, pd.Series):
        return f'a Series of length {len(x)}'
    if isinstance(x, np.ndarray):
        return f'an array with shape {x.shape}'
    if isinstance(x, (list, tuple, set, dict)):
        return f'a {type(x).__name__} of length {len(x)}'
    text = repr(x)
    if text.startswith('<'):
        return f'an instance of {type(x).__name__}'
    return f'{type(x).__name__} ({text})'


def _as_array(x):
    if isinstance(x, (pd.Series, pd.DataFrame)):
        return x.to_numpy()
    return np.asarray(x)


def _needs_number(x, name='answer'):
    if isinstance(x, (bool, np.bool_)) or not isinstance(x, (int, float, np.number)):
        return f'the {name} should be a single number, but you gave {_kind(x)}'
    return None


# The toy numbers that notebook 1 works with. The notebook types them out in
# full; they live here too so that the validators never guess.
PRACTICE_PRICES = [101.2, 99.8, 103.4, 100.0, 105.5, 108.1]
PRACTICE_RETURNS = [0.012, -0.004, 0.000, 0.008, -0.011, 0.003, -0.002, 0.006]

# Cached data, so repeated checks do not re-read the CSVs.
_CACHE: dict[str, pd.DataFrame] = {}


def _prices():
    if 'prices' not in _CACHE:
        ensure_data(quiet=True)
        _CACHE['prices'] = pd.read_csv(DATA_DIR / 'stock_prices.csv',
                                       parse_dates=['date'])
    return _CACHE['prices']


def _factors():
    if 'factors' not in _CACHE:
        ensure_data(quiet=True)
        _CACHE['factors'] = pd.read_csv(DATA_DIR / 'factor_data.csv',
                                        parse_dates=['date'])
    return _CACHE['factors']


# ===========================================================================
# Notebook 1 — Coding Essentials
# ===========================================================================

@_register('1.1', "ticker is text in quotes, shares is a whole number (no "
                  "decimal point), price has a decimal point, is_open is the "
                  "bare word True.")
def _c11(ticker, shares, price, is_open):
    if not isinstance(ticker, str):
        return f'ticker should be a str, you gave {_kind(ticker)}'
    if ticker != 'ACME':
        return f"ticker should be 'ACME', you gave {ticker!r}"
    if not isinstance(shares, int) or isinstance(shares, bool):
        return f'shares should be an int, you gave {_kind(shares)}'
    if shares != 250:
        return f'shares should be 250, you gave {shares}'
    if not isinstance(price, float):
        return (f'price should be a float, you gave {_kind(price)} — '
                f'write 142.5, not 142')
    if not _close(price, 142.5):
        return f'price should be 142.5, you gave {price}'
    if not isinstance(is_open, bool):
        return f'is_open should be a bool, you gave {_kind(is_open)}'
    if is_open is not True:
        return 'is_open should be True'
    return None


@_register('1.2', "Use an f-string with format specs: f'{value:,.2f}' puts in "
                  "the thousands separator and keeps two decimals.")
def _c12(text):
    if not isinstance(text, str):
        return f'this exercise wants a string, you gave {_kind(text)}'
    if text == '35625.0':
        return ("that is what plain str() gives you — you still need the "
                "thousands separator and two decimals")
    if text != '35,625.00':
        return f"expected '35,625.00', you produced {text!r}"
    return None


@_register('1.3', "Slicing is prices[start:stop] and the stop index is NOT "
                  "included. Negative indexes count from the end.")
def _c13(first_three, last_one):
    expected = PRACTICE_PRICES[:3]
    got = list(first_three) if isinstance(first_three, (list, tuple, np.ndarray)) \
        else first_three
    if got != expected:
        return f'first_three should be {expected}, you gave {got!r}'
    if not _close(last_one, PRACTICE_PRICES[-1]):
        return f'last_one should be {PRACTICE_PRICES[-1]}, you gave {last_one!r}'
    return None


@_register('1.4', "sectors['CRUX'] reads a key. For a key that might be "
                  "missing use sectors.get('ZZZZ', 'Unknown') so it returns a "
                  "default instead of raising KeyError.")
def _c14(crux_sector, missing_sector):
    if crux_sector != 'Energy':
        return f"sectors['CRUX'] is 'Energy', you gave {crux_sector!r}"
    if missing_sector != 'Unknown':
        return (f"looking up a ticker that is not there should give 'Unknown', "
                f"you gave {missing_sector!r}")
    return None


@_register('1.5', "Start with total = 0.0 before the loop, then inside the "
                  "loop do total = total + p (or total += p).")
def _c15(total):
    problem = _needs_number(total, 'total')
    if problem:
        return problem
    expected = sum(PRACTICE_PRICES)
    if not _close(total, expected, tol=1e-9):
        return f'the six prices add up to {expected}, you got {total}'
    return None


@_register('1.6', "Loop over the returns; inside the loop use "
                  "if r > 0: up += 1 / elif r < 0: down += 1 / else: flat += 1.")
def _c16(up, down, flat):
    want = (sum(1 for r in PRACTICE_RETURNS if r > 0),
            sum(1 for r in PRACTICE_RETURNS if r < 0),
            sum(1 for r in PRACTICE_RETURNS if r == 0))
    if (up, down, flat) != want:
        return (f'expected up={want[0]}, down={want[1]}, flat={want[2]}; you got '
                f'up={up}, down={down}, flat={flat}')
    return None


@_register('1.7', "The shape is [expression for item in collection if "
                  "condition] — here the expression is just p and the "
                  "condition is p > 104.")
def _c17(result):
    expected = [p for p in PRACTICE_PRICES if p > 104]
    got = list(result) if isinstance(result, (list, tuple, np.ndarray)) else result
    if not isinstance(got, list):
        return f'expected a list, you gave {_kind(result)}'
    if len(got) == len(PRACTICE_PRICES):
        return 'you kept every price — the `if` filter is missing'
    if [round(float(g), 6) for g in got] != expected:
        return f'expected {expected}, you gave {got!r}'
    return None


@_register('1.8', "def simple_return(p0, p1): return p1 / p0 - 1.0 — and "
                  "remember `return`, not `print`.")
def _c18(fn):
    if not callable(fn):
        return f'pass the function itself (no parentheses), you gave {_kind(fn)}'
    try:
        got = fn(100.0, 110.0)
    except Exception as exc:                                  # noqa: BLE001
        return f'calling your function raised {type(exc).__name__}: {exc}'
    if got is None:
        return 'your function returned None — did you print instead of return?'
    if not _close(got, 0.10):
        return f'simple_return(100, 110) should be 0.10, yours gave {got}'
    if not _close(fn(50.0, 40.0), -0.20):
        return f'simple_return(50, 40) should be -0.20, yours gave {fn(50.0, 40.0)}'
    return None


@_register('1.9', "prices[1:] is every price from the second onwards and "
                  "prices[:-1] is every price except the last. Divide one by "
                  "the other, element by element, and subtract 1.")
def _c19(rets):
    arr = _as_array(rets)
    prices = np.array(PRACTICE_PRICES)
    expected = prices[1:] / prices[:-1] - 1.0
    if arr.shape != expected.shape:
        return (f'expected an array of {expected.shape[0]} returns (one fewer '
                f'than the six prices), you gave {_kind(rets)}')
    if not np.allclose(arr, expected):
        return f'the numbers are off — first return should be {expected[0]:.6f}'
    return None


@_register('1.10', "A comparison on an array gives an array of True/False. "
                   "The mean of that boolean array is the fraction that are "
                   "True: (rets < 0).mean().")
def _c110(share):
    problem = _needs_number(share, 'answer')
    if problem:
        return problem
    prices = np.array(PRACTICE_PRICES)
    rets = prices[1:] / prices[:-1] - 1.0
    n_neg = int((rets < 0).sum())
    if _close(share, n_neg, tol=1e-9):
        return 'that is the count, not the share — divide by how many there are'
    if not _close(share, n_neg / len(rets), tol=1e-9):
        return (f'{n_neg} of the {len(rets)} returns are negative, so expected '
                f'{n_neg / len(rets)}, got {share}')
    return None


@_register('1.11', "Filter with a boolean mask — acme = prices[prices['ticker'] "
                   "== 'ACME'] — then take .iloc[-1] and .iloc[0] of the price "
                   "column.")
def _c111(total_return):
    df = _prices()
    acme = df[df['ticker'] == 'ACME']['price']
    expected = acme.iloc[-1] / acme.iloc[0] - 1.0
    problem = _needs_number(total_return, 'answer')
    if problem:
        return problem
    if _close(total_return, expected + 1.0, tol=1e-4):
        return 'that is the growth multiple — subtract 1 to turn it into a return'
    if not _close(total_return, expected, tol=1e-4):
        return f'expected about {expected:.4f}, you got {total_return:.4f}'
    return None


@_register('1.12', "prices.groupby('sector')['volume'].mean() gives one number "
                   "per sector. Keep it as a Series.")
def _c112(by_sector):
    expected = _prices().groupby('sector')['volume'].mean()
    if not isinstance(by_sector, pd.Series):
        return f'expected a pandas Series, you gave {_kind(by_sector)}'
    if len(by_sector) != 3:
        return f'expected 3 sectors, you gave {len(by_sector)} rows'
    if sorted(by_sector.index) != sorted(expected.index):
        return f'the index should be the sector names, yours is {list(by_sector.index)}'
    if not np.allclose(by_sector.sort_index().to_numpy(),
                       expected.sort_index().to_numpy(), rtol=1e-4):
        return 'the sector names are right but the numbers are not the mean volume'
    return None


@_register('1.13', "def __init__(self, ticker, shares, price): store each one "
                   "on self. Then def market_value(self): return self.shares * "
                   "self.price.")
def _c113(cls):
    if not isinstance(cls, type):
        return (f'pass the class itself, not an instance — check("1.13", Position) '
                f'not check("1.13", Position(...)). You gave {_kind(cls)}')
    try:
        pos = cls('ACME', 250, 142.5)
    except Exception as exc:                                  # noqa: BLE001
        return (f'Position("ACME", 250, 142.5) raised {type(exc).__name__}: {exc}')
    for attr, want in [('ticker', 'ACME'), ('shares', 250), ('price', 142.5)]:
        if not hasattr(pos, attr):
            return f'the instance has no .{attr} — assign it in __init__'
        if getattr(pos, attr) != want:
            return f'.{attr} should be {want!r}, it is {getattr(pos, attr)!r}'
    if not hasattr(pos, 'market_value'):
        return 'the class needs a market_value() method'
    if not callable(pos.market_value):
        return 'market_value should be a method you can call, not a stored value'
    got = pos.market_value()
    if not _close(got, 35625.0):
        return f'market_value() should be 35625.0, yours gave {got}'
    return None


# ===========================================================================
# Notebook 2 — Plotting
# ===========================================================================

def _axes_of(obj):
    """Accept either an Axes or a Figure and return a list of Axes."""
    if hasattr(obj, 'get_xlabel'):
        return [obj]
    if hasattr(obj, 'axes'):
        return list(obj.axes)
    return []


@_register('2.1', "ax.set_xlabel('Date'), ax.set_ylabel('Price ($)') and "
                  "ax.set_title(...) — every axis needs a name and a unit.")
def _c21(ax):
    axes = _axes_of(ax)
    if not axes:
        return f'pass the Axes object (the `ax` from plt.subplots), you gave {_kind(ax)}'
    a = axes[0]
    if not a.lines:
        return 'nothing has been plotted on these axes yet'
    if not a.get_xlabel().strip():
        return 'the x axis has no label'
    if not a.get_ylabel().strip():
        return 'the y axis has no label'
    if '$' not in a.get_ylabel() and 'usd' not in a.get_ylabel().lower():
        return ('the y axis is a price — say so in the label, e.g. '
                '"Price ($)". Units are not optional')
    if not a.get_title().strip():
        return 'the plot has no title'
    return None


@_register('2.2', "Call ax.plot(...) once per ticker with label='ACME' etc., "
                  "then ax.legend() once at the end.")
def _c22(ax):
    axes = _axes_of(ax)
    if not axes:
        return f'pass the Axes object, you gave {_kind(ax)}'
    a = axes[0]
    if len(a.lines) < 3:
        return f'expected at least 3 lines, these axes have {len(a.lines)}'
    if a.get_legend() is None:
        return 'there is no legend — call ax.legend()'
    labels = [t.get_text() for t in a.get_legend().get_texts()]
    if any(lab.startswith('_') or not lab.strip() for lab in labels):
        return (f'the legend entries are unnamed ({labels}) — pass label=... '
                f'inside each ax.plot call')
    return None


@_register('2.3', "ax.set_yscale('log') switches the axis; ax.set_xlim(left, "
                  "right) trims the window.")
def _c23(ax):
    axes = _axes_of(ax)
    if not axes:
        return f'pass the Axes object, you gave {_kind(ax)}'
    a = axes[0]
    if a.get_yscale() != 'log':
        return f"the y scale is still '{a.get_yscale()}' — set it to 'log'"
    return None


@_register('2.4', "ax.scatter(x, y) draws the points; loop over the rows and "
                  "call ax.annotate(name, (x, y)) to label them.")
def _c24(ax):
    axes = _axes_of(ax)
    if not axes:
        return f'pass the Axes object, you gave {_kind(ax)}'
    a = axes[0]
    if not a.collections:
        return 'no scatter found — ax.scatter() adds a collection, ax.plot() does not'
    n_points = len(a.collections[0].get_offsets())
    if n_points != 6:
        return f'expected one point per ticker (6), found {n_points}'
    if len(a.texts) < 6:
        return (f'only {len(a.texts)} of the 6 points are labelled — use '
                f'ax.annotate inside a loop')
    if not a.get_xlabel().strip() or not a.get_ylabel().strip():
        return 'both axes still need labels'
    return None


@_register('2.5', "ax.hist(values, bins=40) draws the bars; ax.axvline(mean, "
                  "color='...', linestyle='--') draws the reference line.")
def _c25(ax):
    axes = _axes_of(ax)
    if not axes:
        return f'pass the Axes object, you gave {_kind(ax)}'
    a = axes[0]
    if len(a.patches) < 10:
        return f'expected a histogram with plenty of bars, found {len(a.patches)}'
    vertical = [ln for ln in a.lines
                if len(set(np.round(ln.get_xdata(orig=False), 12))) == 1]
    if not vertical:
        return 'no vertical reference line — add ax.axvline(...)'
    if not any(ln.get_linestyle() not in ('-', 'solid') for ln in vertical):
        return 'the reference line should be dashed so it reads as an annotation'
    return None


@_register('2.6', "fig, axes = plt.subplots(2, 2, figsize=(10, 7)); then loop "
                  "with for ax, ticker in zip(axes.flat, tickers).")
def _c26(fig):
    axes = _axes_of(fig)
    if len(axes) != 4:
        return f'expected a 2x2 grid of 4 panels, this figure has {len(axes)}'
    empty = [i for i, a in enumerate(axes) if not a.lines]
    if empty:
        return f'panel(s) {empty} have nothing plotted on them'
    untitled = [i for i, a in enumerate(axes) if not a.get_title().strip()]
    if untitled:
        return f'panel(s) {untitled} have no title — each one needs to say what it shows'
    return None


@_register('2.7', "Work through the checklist one line at a time: figsize, the "
                  "three lines with labels, axis labels with units, a title, a "
                  "legend, a light grid, and fig.savefig(path, dpi=150, "
                  "bbox_inches='tight').")
def _c27(fig, path):
    axes = _axes_of(fig)
    if not axes:
        return f'pass the Figure object, you gave {_kind(fig)}'
    a = axes[0]
    problems = []
    if len(a.lines) < 3:
        problems.append(f'only {len(a.lines)} lines drawn (need 3)')
    if a.get_legend() is None:
        problems.append('no legend')
    if not a.get_xlabel().strip():
        problems.append('no x label')
    if not a.get_ylabel().strip():
        problems.append('no y label')
    if not a.get_title().strip():
        problems.append('no title')
    w, h = fig.get_size_inches()
    if w < 7:
        problems.append(f'the figure is only {w:.1f} inches wide — too cramped')
    p = Path(path)
    if not p.exists():
        problems.append(f'no file was written to {p}')
    elif p.stat().st_size < 10_000:
        problems.append('the saved file is suspiciously small — check the dpi')
    if problems:
        return 'still missing: ' + '; '.join(problems)
    return None


# ===========================================================================
# Notebook 3 — Regression
# ===========================================================================

def _reg_frame():
    """Monthly excess returns used by the regression exercises."""
    f = _factors().rename(columns={'Mkt-RF': 'mkt_rf', 'SMB': 'smb',
                                   'HML': 'hml', 'RF': 'rf'})
    f['value_excess'] = f['value_fund'] - f['rf']
    f['growth_excess'] = f['growth_fund'] - f['rf']
    return f


def _ols_ref(y, X):
    b = np.linalg.solve(X.T @ X, X.T @ y)
    e = y - X @ b
    n, k = X.shape
    s2 = e @ e / (n - k)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r2 = 1.0 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))
    return b, se, r2


def _capm_pieces():
    f = _reg_frame()
    y = f['value_excess'].to_numpy()
    X = np.column_stack([np.ones(len(f)), f['mkt_rf'].to_numpy()])
    return y, X


@_register('3.1', "np.column_stack([np.ones(n), x]) glues a column of ones in "
                  "front of your regressor. n is len(y).")
def _c31(X):
    arr = _as_array(X)
    _, X_ref = _capm_pieces()
    if arr.ndim != 2:
        return f'X must be 2-dimensional (n rows, k columns), you gave {_kind(X)}'
    if arr.shape != X_ref.shape:
        return f'expected shape {X_ref.shape}, you gave {arr.shape}'
    if not np.allclose(arr[:, 0], 1.0):
        if np.allclose(arr[:, -1], 1.0):
            return 'the constant is in the last column — put it first'
        return 'the first column is not a column of ones'
    if not np.allclose(arr[:, 1], X_ref[:, 1]):
        return 'the second column is not the market excess return'
    return None


@_register('3.2', "b = np.linalg.solve(X.T @ X, X.T @ y). The @ symbol is "
                  "matrix multiplication; X.T is the transpose.")
def _c32(b):
    arr = _as_array(b).ravel()
    y, X = _capm_pieces()
    ref, _, _ = _ols_ref(y, X)
    if arr.shape != ref.shape:
        return f'expected {ref.shape[0]} coefficients, you gave {_kind(b)}'
    if np.allclose(arr, ref[::-1], atol=1e-6):
        return 'right numbers, wrong order — the constant comes first'
    if not np.allclose(arr, ref, atol=1e-6):
        return (f'expected roughly [{ref[0]:.5f}, {ref[1]:.5f}], you got '
                f'[{arr[0]:.5f}, {arr[1]:.5f}]')
    return None


@_register('3.3', "resid = y - X @ b. Then R2 = 1 - resid @ resid / "
                  "((y - y.mean()) @ (y - y.mean())).")
def _c33(resid, r2):
    y, X = _capm_pieces()
    ref_b, _, ref_r2 = _ols_ref(y, X)
    arr = _as_array(resid).ravel()
    if arr.shape != y.shape:
        return f'expected {len(y)} residuals, you gave {_kind(resid)}'
    if not np.allclose(arr, y - X @ ref_b, atol=1e-8):
        if np.allclose(arr, X @ ref_b, atol=1e-8):
            return 'those are the fitted values, not the residuals'
        return 'the residuals do not match y - X @ b'
    if abs(arr.mean()) > 1e-10:
        return 'OLS residuals must average to exactly zero when X has a constant'
    if not _close(r2, ref_r2, tol=1e-4):
        return f'R-squared should be about {ref_r2:.4f}, you got {r2}'
    return None


@_register('3.4', "s2 = resid @ resid / (n - k); then se = np.sqrt(np.diag(s2 "
                  "* np.linalg.inv(X.T @ X))) and t = b / se.")
def _c34(se, tstats):
    y, X = _capm_pieces()
    ref_b, ref_se, _ = _ols_ref(y, X)
    arr = _as_array(se).ravel()
    if arr.shape != ref_se.shape:
        return f'expected {len(ref_se)} standard errors, you gave {_kind(se)}'
    if np.allclose(arr, ref_se * np.sqrt((len(y) - 2) / len(y)), rtol=1e-3):
        return ('you divided by n — OLS divides the sum of squared residuals '
                'by n - k, where k is the number of coefficients')
    if not np.allclose(arr, ref_se, rtol=1e-4):
        return (f'expected roughly [{ref_se[0]:.5f}, {ref_se[1]:.5f}], you got '
                f'[{arr[0]:.5f}, {arr[1]:.5f}]')
    t_arr = _as_array(tstats).ravel()
    if not np.allclose(t_arr, ref_b / ref_se, rtol=1e-4):
        return 'the t-statistics are not coefficient / standard error'
    return None


@_register('3.5', "Move the code you already wrote into the function body and "
                  "return a dict with keys 'beta', 'se', 'tstat', 'r2'.")
def _c35(fn):
    if not callable(fn):
        return f'pass the function itself, you gave {_kind(fn)}'
    rng = np.random.default_rng(0)
    n = 200
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
    y = X @ np.array([0.5, 2.0, -1.0]) + rng.normal(0, 0.5, n)
    try:
        out = fn(y, X)
    except Exception as exc:                                  # noqa: BLE001
        return f'calling your function raised {type(exc).__name__}: {exc}'
    if not isinstance(out, dict):
        return f'the function should return a dict, it returned {_kind(out)}'
    missing = {'beta', 'se', 'tstat', 'r2'} - set(out)
    if missing:
        return f'the returned dict is missing key(s): {sorted(missing)}'
    ref_b, ref_se, ref_r2 = _ols_ref(y, X)
    if not np.allclose(_as_array(out['beta']).ravel(), ref_b, rtol=1e-6):
        return 'the coefficients are wrong on a fresh dataset — is anything hard-coded?'
    if not np.allclose(_as_array(out['se']).ravel(), ref_se, rtol=1e-6):
        return 'the standard errors are wrong on a fresh dataset'
    if not np.allclose(_as_array(out['tstat']).ravel(), ref_b / ref_se, rtol=1e-6):
        return 'the t-statistics are wrong on a fresh dataset'
    if not _close(out['r2'], ref_r2, tol=1e-6):
        return 'R-squared is wrong on a fresh dataset'
    return None


@_register('3.6', "sm.add_constant(x) builds the design matrix for you; then "
                  "sm.OLS(y, X).fit(). Note the argument order: y first.")
def _c36(result):
    if not hasattr(result, 'params'):
        return (f'pass the fitted results object (what .fit() returned), you '
                f'gave {_kind(result)}')
    y, X = _capm_pieces()
    ref_b, ref_se, ref_r2 = _ols_ref(y, X)
    params = _as_array(result.params).ravel()
    if params.shape != ref_b.shape:
        return f'expected 2 coefficients, the model has {len(params)}'
    if not np.allclose(params, ref_b, rtol=1e-6):
        if np.allclose(params[0], ref_b[1], rtol=1e-3) and len(params) == 1:
            return 'no constant in the model — statsmodels does not add one for you'
        return 'the coefficients do not match the by-hand answer'
    if not np.allclose(_as_array(result.bse).ravel(), ref_se, rtol=1e-6):
        return 'the standard errors do not match the by-hand answer'
    return None


@_register('3.7', "smf.ols('value_excess ~ mkt_rf + smb + hml', data=df).fit() "
                  "— the constant is included automatically by the formula.")
def _c37(result):
    if not hasattr(result, 'params'):
        return f'pass the fitted results object, you gave {_kind(result)}'
    params = result.params
    if not hasattr(params, 'index'):
        return 'use the formula API (smf.ols) so the coefficients keep their names'
    names = [str(i).lower() for i in params.index]
    if 'intercept' not in names:
        return 'there is no Intercept — the formula should not include -1'
    for need in ['mkt_rf', 'smb', 'hml']:
        if not any(need in nm for nm in names):
            return f'{need} is not in the model'
    if len(params) != 4:
        return f'expected 4 coefficients, the model has {len(params)}'
    f = _reg_frame()
    y = f['value_excess'].to_numpy()
    X = np.column_stack([np.ones(len(f)), f['mkt_rf'], f['smb'], f['hml']])
    ref_b, _, _ = _ols_ref(y, X)
    if not np.allclose(_as_array(params).ravel(), ref_b, rtol=1e-5):
        return 'the coefficients are not the ones this dataset implies'
    return None


@_register('3.8', "Refit with cov_type='HAC' and cov_kwds={'maxlags': 6}. The "
                  "coefficients must be identical; only the standard errors "
                  "move.")
def _c38(ols_result, hac_result):
    for name, r in [('first', ols_result), ('second', hac_result)]:
        if not hasattr(r, 'bse'):
            return f'the {name} argument is not a fitted results object'
    if not np.allclose(_as_array(ols_result.params).ravel(),
                       _as_array(hac_result.params).ravel(), rtol=1e-8):
        return ('the coefficients changed — robust standard errors never move '
                'the point estimates, so something else differs between the '
                'two models')
    if np.allclose(_as_array(ols_result.bse).ravel(),
                   _as_array(hac_result.bse).ravel(), rtol=1e-8):
        return 'the standard errors are identical — cov_type did not take effect'
    return None


@_register('3.9', "mkt_rf * recession in a formula expands to mkt_rf + "
                  "recession + mkt_rf:recession. The interaction is the number "
                  "you want.")
def _c39(result, beta_in_recession):
    if not hasattr(result, 'params'):
        return f'pass the fitted results object, you gave {_kind(result)}'
    names = [str(i) for i in result.params.index]
    inter = [nm for nm in names if ':' in nm]
    if not inter:
        return 'there is no interaction term — use mkt_rf * recession'
    base = [nm for nm in names if nm.lower() == 'mkt_rf']
    if not base:
        return 'the model has no plain mkt_rf term'
    expected = float(result.params[base[0]]) + float(result.params[inter[0]])
    if not _close(beta_in_recession, expected, tol=1e-4):
        return (f'the recession beta is the base coefficient PLUS the '
                f'interaction, i.e. {expected:.3f}; you gave {beta_in_recession}')
    return None


@_register('3.10', "Loop i from window to len(df); slice the last `window` rows "
                   "with .iloc[i - window:i]; fit; append the slope.")
def _c310(betas, window=36):
    f = _reg_frame()
    y = f['growth_excess'].to_numpy()
    x = f['mkt_rf'].to_numpy()
    ref = []
    for i in range(window, len(f) + 1):
        yy, xx = y[i - window:i], x[i - window:i]
        Xw = np.column_stack([np.ones(window), xx])
        ref.append(np.linalg.solve(Xw.T @ Xw, Xw.T @ yy)[1])
    ref = np.array(ref)
    arr = _as_array(betas).ravel()
    arr = arr[~np.isnan(arr)]
    if len(arr) != len(ref):
        return (f'expected {len(ref)} rolling betas from a {window}-month '
                f'window over {len(f)} months, you produced {len(arr)}')
    if not np.allclose(arr, ref, rtol=1e-5):
        return (f'the first window should give beta = {ref[0]:.3f} and the last '
                f'{ref[-1]:.3f}; yours give {arr[0]:.3f} and {arr[-1]:.3f}')
    return None


# ===========================================================================
# Notebook 4 — Monte Carlo
# ===========================================================================

P_PAIR_EXACT = 1.0 - (1287 * 1024) / 2598960.0     # 0.4929...
HOUSE_EDGE_EXACT = 3.0 / 51.0                       # 0.0588...


@_register('4.1', "rng = np.random.default_rng(42) twice gives two generators "
                  "that produce exactly the same stream.")
def _c41(first, second):
    a, b = _as_array(first).ravel(), _as_array(second).ravel()
    if a.shape != b.shape:
        return 'the two draws are not even the same length'
    if not np.allclose(a, b):
        return ('the two draws differ — each generator needs its own '
                'default_rng(seed) call with the SAME seed')
    if len(a) < 3:
        return 'draw at least 3 numbers so the comparison means something'
    if np.allclose(a, a[0]):
        return 'every value is identical — you seeded inside the draw, not before it'
    return None


@_register('4.2', "Two nested loops, or a comprehension: [(rank, suit) for suit "
                  "in suits for rank in ranks]. 13 ranks x 4 suits = 52.")
def _c42(deck):
    try:
        n = len(deck)
    except TypeError:
        return f'the deck should be something with a length, you gave {_kind(deck)}'
    if n != 52:
        return f'a deck has 52 cards, yours has {n}'
    if len(set(map(str, deck))) != 52:
        return 'some cards appear more than once'
    return None


@_register('4.3', "Take the rank of each of the 5 cards, then compare the "
                  "number of distinct ranks with 5: fewer than 5 means a "
                  "repeat.")
def _c43(fn):
    if not callable(fn):
        return f'pass the function itself, you gave {_kind(fn)}'
    cases = [
        ([0, 13, 5, 7, 9], True),     # two aces, different suits
        ([0, 1, 2, 3, 4], False),     # five different ranks
        ([12, 25, 38, 51, 3], True),  # four of a kind
        ([2, 15, 28, 41, 7], True),
        ([0, 5, 10, 20, 30], False),
    ]
    for cards, want in cases:
        try:
            got = fn(np.array(cards))
        except Exception as exc:                              # noqa: BLE001
            return f'calling your function raised {type(exc).__name__}: {exc}'
        if bool(got) != want:
            ranks = [c % 13 for c in cards]
            return (f'for cards {cards} (ranks {ranks}) the answer should be '
                    f'{want}, yours said {bool(got)}')
    return None


@_register('4.4', "Run the trial in a loop, count the hits, divide by the "
                  "number of trials. Use at least 20,000 trials.")
def _c44(estimate, n_trials):
    problem = _needs_number(estimate, 'estimate')
    if problem:
        return problem
    if n_trials < 5000:
        return f'{n_trials} trials is not enough to land within tolerance — use 20,000+'
    tol = 4.0 * np.sqrt(0.25 / n_trials) + 0.002
    if abs(estimate - P_PAIR_EXACT) > tol:
        return (f'the exact answer is {P_PAIR_EXACT:.4f}; your estimate '
                f'{estimate:.4f} is further away than {n_trials} trials should '
                f'allow')
    if estimate == P_PAIR_EXACT:
        return 'that is the exact combinatorial value — simulate it, do not copy it'
    return None


@_register('4.5', "se = sqrt(p * (1 - p) / n). Rearranged, n = p * (1 - p) / "
                  "se**2 — then round up.")
def _c45(se, n_needed):
    p = P_PAIR_EXACT
    ref_se = np.sqrt(p * (1 - p) / 20_000)
    if not _close(se, ref_se, tol=1e-3):
        if _close(se, np.sqrt(p * (1 - p)), tol=1e-3):
            return 'that is the standard deviation of one trial — divide by n first'
        return f'expected a standard error near {ref_se:.5f}, you gave {se}'
    ref_n = p * (1 - p) / (0.0005 ** 2)
    if not (0.9 * ref_n <= n_needed <= 1.2 * ref_n):
        return (f'to get a standard error of 0.0005 you need about '
                f'{ref_n:,.0f} trials; you said {n_needed:,.0f}')
    return None


@_register('4.6', "rng.random((n_sims, 52)).argsort(axis=1)[:, :5] deals 5 "
                  "distinct cards for every simulation at once.")
def _c46(hands, estimate):
    arr = _as_array(hands)
    if arr.ndim != 2 or arr.shape[1] != 5:
        return f'expected an (n_sims, 5) array of card indices, you gave {_kind(hands)}'
    n = arr.shape[0]
    if n < 50_000:
        return f'run at least 50,000 simulations; you ran {n}'
    if arr.min() < 0 or arr.max() > 51:
        return 'card indices must lie between 0 and 51'
    dup_rows = int((np.array([len(set(row)) for row in arr[:200]]) < 5).sum())
    if dup_rows:
        return f'{dup_rows} of the first 200 hands contain the same card twice'
    tol = 4.0 * np.sqrt(0.25 / n) + 0.002
    if abs(estimate - P_PAIR_EXACT) > tol:
        return (f'the exact answer is {P_PAIR_EXACT:.4f}, your vectorised '
                f'estimate is {estimate:.4f}')
    return None


@_register('4.7', "Per $1 bet the house edge is -(your average profit). You "
                  "win when your rank is higher, lose on a tie as well as a "
                  "loss.")
def _c47(edge):
    problem = _needs_number(edge, 'edge')
    if problem:
        return problem
    if abs(edge + HOUSE_EDGE_EXACT) < 0.01:
        return ('sign check — report the edge as a positive number, the share '
                'of each bet the house keeps')
    if abs(edge - HOUSE_EDGE_EXACT) > 0.015:
        return (f'the exact house edge is 3/51 = {HOUSE_EDGE_EXACT:.4f}; you '
                f'got {edge:.4f}')
    return None


@_register('4.8', "np.cumsum(profits, axis=1) turns per-hand profits into a "
                  "running bankroll. A player is ruined if the running minimum "
                  "of their path ever hits -start.")
def _c48(paths, p_ruin):
    arr = _as_array(paths)
    if arr.ndim != 2:
        return f'expected a 2-D array (one row per player), you gave {_kind(paths)}'
    n_players, n_hands = arr.shape
    if n_players < 2000 or n_hands < 50:
        return (f'simulate at least 2,000 players over at least 50 hands; you '
                f'have {n_players} x {n_hands}')
    steps = np.diff(arr, axis=1)
    if np.abs(steps).max() > 1.5:
        return 'the bankroll moves by more than one bet per hand — is it cumulative?'
    if not (0.0 <= p_ruin <= 1.0):
        return f'a probability has to sit between 0 and 1, you gave {p_ruin}'
    return None


@_register('4.9', "Compound the simulated returns along the time axis with "
                  ".cumprod(axis=1) or .prod(axis=1), then use np.percentile "
                  "on the terminal values.")
def _c49(terminal, median, p05):
    arr = _as_array(terminal).ravel()
    if arr.size < 5000:
        return f'expected at least 5,000 simulated outcomes, you gave {arr.size}'
    if arr.min() < 0:
        return 'wealth from compounding returns cannot go negative — check the formula'
    if not _close(median, np.median(arr), tol=1e-3):
        return f'the median of your own array is {np.median(arr):,.2f}'
    if not _close(p05, np.percentile(arr, 5), tol=1e-3):
        return f'the 5th percentile of your own array is {np.percentile(arr, 5):,.2f}'
    if median <= p05:
        return 'the median cannot be below the 5th percentile'
    return None


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    ensure_data()
    print(f'Data folder : {DATA_DIR}')
    for f in sorted(DATA_DIR.glob('*.csv')):
        print(f'  {f.name:20s} {f.stat().st_size // 1024:>4} KB')
    for nb in (1, 2, 3, 4):
        print(f'Notebook {nb}: {len(exercises(nb))} exercises')
