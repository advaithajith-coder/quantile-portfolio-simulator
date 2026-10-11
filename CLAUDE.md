# CLAUDE.md

Guide for Claude Code working in this repository. Keep it short and current: if you learn
something non-obvious about this project, add it here.

## What this is

Quantile: a Monte Carlo portfolio risk simulator (Streamlit). Pick S&P 500 stocks, set or
optimise weights (max Sharpe / min volatility), simulate ~10,000 correlated market years, and
show VaR, CVaR, probability of loss. Live at https://quantile-portfolio-simulator.streamlit.app.
Education only, not financial advice.

## Commands (Python 3.10–3.12)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # (macOS/Linux: .venv/bin/python)
.venv/Scripts/python -m streamlit run app.py                # http://localhost:8501
.venv/Scripts/python -m unittest -v                         # tests (unittest, not pytest)
```

- `tests/test_data_loader.py` downloads real prices (yfinance) and needs internet; if offline, run the others:
  `python -m unittest tests.test_helpers tests.test_optimizer tests.test_portfolio tests.test_simulation -v`.
- Dependencies: edit `requirements.in`, then
  `uv pip compile requirements.in -o requirements.txt --python-version 3.12 --universal`. Keep `pyproject.toml` dependencies in sync.

## Layout

```
app.py                               Streamlit entry: inputs, orchestration, results
portfolio_management/
  data/data_loader.py                DataLoader: price download (yfinance)
  portfolio/portfolio.py             Portfolio: prices → daily returns
  portfolio/optimizer.py             PortfolioOptimizer: SciPy SLSQP, long-only
  monte_carlo/simulation.py          MonteCarloSimulation: multivariate-normal paths
  utils/helpers.py                   risk metrics (VaR, CVaR, loss probability), date helpers
  utils/dashboard.py                 Plotly results dashboard
  utils/ui.py                        page styling (injected CSS), hero, empty/loading states
.streamlit/config.toml               theme (primary #1F8A63, warm beige background)
```

## Rules that matter

- Keep model logic (data/portfolio/optimizer/simulation/helpers) free of Streamlit calls so it stays unit-testable; UI lives in `app.py` and `utils/`.
- Weights are long-only (bounds 0–1) and must sum to 1; the app rejects manual weights that don't.
- Simulation is buy-and-hold; the horizon is user-set in trading days (default 252 ≈ one year), and annualisation uses 252.
- The S&P 500 list is scraped from Wikipedia with a browser User-Agent and falls back to a built-in list; keep that fallback working.
- Streamlit is pinned to 1.38.0; check API compatibility before using newer Streamlit features.
- Keep the README's "Limitations" honest if you change the model (e.g. if you add fat tails or rebalancing).
- Add or update unit tests in `tests/` for any change to calculations.
