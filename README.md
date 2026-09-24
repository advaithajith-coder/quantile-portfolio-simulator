# Quantile — Monte Carlo Portfolio Risk Simulator

[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.12-3776AB)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-1F8A63)](LICENSE)

Quantile estimates how a stock portfolio might behave over the next year. It learns how the chosen stocks moved
together in the past, replays thousands of possible market years, and reports the full range of outcomes: the median
result, the probability of ending with a loss, and how deep the worst 5% of years go.

## Features

- **S&P 500 stock picker** with search by company name or ticker.
- **Three ways to allocate**: edit weights directly, enter dollar amounts per stock, or let the optimiser choose.
- **Mean-variance optimisation** (long-only, SciPy SLSQP): maximise the Sharpe ratio, or minimise volatility for a target return.
- **Correlated Monte Carlo simulation** of daily returns, 10,000 paths by default.
- **Risk metrics**: expected and median final value, probability of loss, Value at Risk (95%) and Conditional VaR (95%).
- **Interactive dashboard**: simulated paths with percentile bands, outcome distribution, VaR over time, historical annual
  returns and each stock's contribution to portfolio return.

## How it works

```
Yahoo Finance prices ─► daily returns ─► mean vector + covariance matrix
                                              │
                         (optional) optimiser ┤─► portfolio weights
                                              ▼
            10,000 × 252 correlated daily returns (multivariate normal)
                                              ▼
              compound each path ─► final values ─► risk metrics + charts
```

1. **Data** — adjusted daily closing prices are downloaded with `yfinance`.
2. **Returns** — prices become daily percentage returns; their mean and covariance describe each stock's drift, volatility
   and co-movement.
3. **Weights** — taken from the user, or found by the optimiser from annualised (×252) statistics.
4. **Simulation** — each path draws `horizon` days of correlated returns, compounds them per stock and combines them with
   the weights (buy and hold, no rebalancing).
5. **Analysis** — percentiles of the simulated final values give VaR and CVaR; the share below the starting amount gives
   the probability of loss.

## Quick start

Requires **Python 3.10–3.12**.

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python -m venv .venv
```

Activate the environment, then install the pinned dependencies and start the app:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app opens at <http://localhost:8501>. With [uv](https://docs.astral.sh/uv/) installed, `uv venv --python 3.12` followed
by `uv pip install -r requirements.txt` does the same setup faster.

## Project structure

```
.
├── app.py                          # Streamlit entry point: inputs, orchestration, results
├── portfolio_management/
│   ├── data/data_loader.py         # Price download (yfinance)
│   ├── portfolio/portfolio.py      # Prices → daily returns
│   ├── portfolio/optimizer.py      # Max-Sharpe and minimum-volatility optimisation
│   ├── monte_carlo/simulation.py   # Correlated multivariate-normal path simulation
│   └── utils/
│       ├── helpers.py              # Risk metrics and date helpers
│       ├── dashboard.py            # Plotly results dashboard
│       └── ui.py                   # Page styling, hero, tips, empty and loading states
├── tests/                          # unittest suite
├── assets/favicon.png
├── .streamlit/config.toml          # Streamlit theme
├── requirements.in                 # Direct dependencies
├── requirements.txt                # Pinned lock file generated from requirements.in
└── pyproject.toml                  # Package metadata
```

## Running the tests

```bash
python -m unittest -v
```

`tests/test_data_loader.py` downloads real prices, so it needs an internet connection.

## Updating dependencies

Edit `requirements.in`, then regenerate the lock file:

```bash
uv pip compile requirements.in -o requirements.txt --python-version 3.12 --universal
```

## Limitations

- Returns are modelled as normally distributed with constant mean and covariance taken from history. Real markets have
  fatter tails and changing volatility, so VaR and CVaR here likely understate extreme losses.
- Results depend heavily on the chosen history window; a window without a downturn produces optimistic simulations.
- The simulation assumes buy and hold with no rebalancing, fees or taxes.
- Company names and the ticker list come from Wikipedia's S&P 500 table; if it cannot be reached, a short built-in list is used.

This project is for education and exploration only and is not financial advice.

## Acknowledgements

Originally based on [cristianleoo/montecarlo-portfolio-management](https://github.com/cristianleoo/montecarlo-portfolio-management) (MIT).

## License

[MIT](LICENSE)
