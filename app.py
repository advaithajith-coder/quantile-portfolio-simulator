import os
import streamlit as st
import requests
from io import StringIO
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from portfolio_management.data.data_loader import DataLoader
from portfolio_management.portfolio.portfolio import Portfolio
from portfolio_management.portfolio.optimizer import PortfolioOptimizer
from portfolio_management.monte_carlo.simulation import MonteCarloSimulation
from portfolio_management.utils.dashboard import render_dashboard
from portfolio_management.utils.ui import (
    inject_global_styles,
    render_nav,
    render_hero,
    panel,
    section_head,
    results_head,
    render_results_empty,
    render_tickers_empty,
    render_tips,
    skeleton_html,
    enable_magnetic_cta,
)

def main():
    st.set_page_config(page_title='Quantile · Portfolio simulator', page_icon=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'favicon.png'), layout='wide')
    inject_global_styles()
    render_nav()
    render_hero()

    # Load tickers (for autocomplete) and their company names (for the results)
    @st.cache_data
    def load_ticker_names():
        sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        try:
            # Wikipedia returns 403 without a browser-like User-Agent
            html = requests.get(sp500_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15).text
            table = pd.read_html(StringIO(html))[0]
            return dict(zip(table['Symbol'], table['Security']))
        except Exception:
            return {
                'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft', 'GOOG': 'Alphabet Inc. (Class C)', 'AMZN': 'Amazon',
                'NVDA': 'Nvidia', 'META': 'Meta Platforms', 'TSLA': 'Tesla, Inc.', 'JPM': 'JPMorgan Chase',
                'V': 'Visa Inc.', 'JNJ': 'Johnson & Johnson', 'WMT': 'Walmart', 'XOM': 'ExxonMobil',
            }

    ticker_names = load_ticker_names()
    ticker_list = list(ticker_names)

    # 01 — Universe: stocks and date range
    with st.container(border=True):
        panel()
        section_head('universe', '01', 'Universe', 'Pick your assets',
                     'Search the S&P 500 and choose the history window the model learns from.')
        selected_tickers = st.multiselect(
            'Stocks',
            options=ticker_list,
            format_func=lambda t: f'{ticker_names.get(t, t)} ({t})',
            placeholder='Search by company or ticker, for example Johnson or XOM',
            help='Type a company name or ticker symbol to search the S&P 500.'
        )
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input('Start date', value=pd.to_datetime('2020-01-01'), help='The start date for historical data.')
        with col2:
            end_date = st.date_input('End date', value=pd.to_datetime(datetime.today() - relativedelta(days=1)), help='The end date for historical data.')

        if not selected_tickers:
            render_tickers_empty()

    render_tips()

    if not selected_tickers:
        render_results_empty()
        st.stop()

    tickers = selected_tickers
    weights = None
    initial_investment = 1000.0  # Default value
    risk_free_rate = 0.02
    optimize = False
    balanced = False
    inputs_valid = True

    alloc_col, sim_col = st.columns([7, 5], gap='medium')

    # 02 — Allocation
    with alloc_col:
        with st.container(border=True):
            panel(delay=1)
            section_head('allocation', '02', 'Allocation', 'Split your capital',
                         'Set weights yourself, let the optimiser choose, or enter dollar amounts.')
            investment_option = st.radio(
                'Input mode',
                ('Use Weights and Initial Investment', 'Use Dollar Amounts per Stock'),
                format_func=lambda o: 'Weights + total' if o.startswith('Use Weights') else 'Dollar amounts',
                horizontal=True,
                help='Select how you want to input your investment allocations.'
            )

            if investment_option == 'Use Weights and Initial Investment':
                optimize = st.toggle('Optimise portfolio', value=False, help='Automatically calculate optimal weights for your portfolio.')
                if optimize:
                    optimization_choice = st.selectbox(
                        'Strategy',
                        ('Maximize Sharpe Ratio', 'Balanced Portfolio'),
                        help='Choose an optimization strategy.'
                    )
                    balanced = (optimization_choice == 'Balanced Portfolio')
                    risk_free_rate = st.number_input(
                        'Risk-free rate',
                        value=0.02, min_value=0.0, max_value=1.0, step=0.01,
                        help='The risk-free rate used by the optimiser, typically a treasury bond yield.'
                    )
                else:
                    default_weight = 1.0 / len(tickers)
                    weights_df = pd.DataFrame({
                        'Company': [ticker_names.get(t, t) for t in tickers],
                        'Ticker': tickers,
                        'Weight': [default_weight] * len(tickers)
                    })
                    weights_df = st.data_editor(
                        weights_df,
                        num_rows="fixed",
                        disabled=['Company', 'Ticker'],
                        use_container_width=True,
                        hide_index=True,
                        key='weights_editor',
                    )
                    # Validate weights
                    total_weight = weights_df['Weight'].sum()
                    if abs(total_weight - 1.0) > 1e-6:
                        st.error(f'Weights must sum to 1.0 — currently {total_weight:.4f}')
                        inputs_valid = False
                    weights = weights_df['Weight'].tolist()

                initial_investment = st.number_input(
                    'Initial investment ($)',
                    value=1000.0,
                    min_value=0.0,
                    help='Total amount you plan to invest.'
                )
            else:
                amounts = []
                amount_cols = st.columns(2)
                for i, ticker in enumerate(tickers):
                    with amount_cols[i % 2]:
                        amount = st.number_input(
                            f'{ticker_names.get(ticker, ticker)} ($)',
                            value=100.0,
                            min_value=0.0,
                            help=f'Amount to invest in {ticker_names.get(ticker, ticker)} ({ticker}).'
                        )
                    amounts.append(amount)
                total_investment = sum(amounts)
                if total_investment == 0:
                    st.error('Total investment cannot be zero.')
                    inputs_valid = False
                else:
                    weights = [amount / total_investment for amount in amounts]
                    initial_investment = total_investment

    # 03 — Simulation parameters
    with sim_col:
        with st.container(border=True):
            panel(delay=2)
            section_head('simulation', '03', 'Simulation', 'Set the experiment',
                         'More paths give smoother estimates; 252 trading days ≈ one year.')
            num_simulations = st.number_input(
                'Number of simulations',
                value=10000,
                min_value=100,
                step=100,
                help='Number of Monte Carlo simulations to run.'
            )
            time_horizon = st.number_input(
                'Time horizon (trading days)',
                value=252,
                min_value=1,
                step=1,
                help='Investment period in days (e.g., 252 for one year).'
            )
            st.write('')
            run_simulation = st.button('Run simulation', type='primary', use_container_width=True, disabled=not inputs_valid)
            enable_magnetic_cta()

    if not run_simulation:
        render_results_empty()
        return

    if optimize:
        alloc_title = 'Balanced (minimum-volatility) weights' if balanced else 'Max-Sharpe weights'
    elif investment_option == 'Use Weights and Initial Investment':
        alloc_title = 'Custom weights'
    else:
        alloc_title = f'Weights from ${initial_investment:,.0f} in dollar amounts'

    # 04 — Results: skeleton while prices download and paths are simulated
    results_head(int(num_simulations), int(time_horizon), alloc_title)
    loading = st.empty()
    loading.markdown(skeleton_html(), unsafe_allow_html=True)

    # Load data
    data_loader = DataLoader()
    stock_data = data_loader.load_data(tickers, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    missing = [t for t in tickers if t not in stock_data.columns]
    if stock_data.empty or missing:
        loading.empty()
        st.error(f"No price data for {', '.join(missing) or 'the selected tickers'} between {start_date} and {end_date}. "
                 'Remove it or widen the date range, then run again.')
        return

    # Create portfolio
    portfolio = Portfolio(stock_data)
    portfolio.calculate_returns()

    # Annualize returns and covariance
    expected_returns = portfolio.returns.mean() * 252
    covariance_matrix = portfolio.returns.cov() * 252

    # Determine weights
    if optimize:
        optimizer = PortfolioOptimizer(
            expected_returns,
            covariance_matrix,
            risk_free_rate=risk_free_rate
        )
        if balanced:
            weights = optimizer.minimize_volatility(target_return=expected_returns.mean())
        else:
            weights = optimizer.maximize_sharpe_ratio()

    # Perform Monte Carlo Simulation
    simulation = MonteCarloSimulation(portfolio.returns, initial_investment, weights)
    all_cumulative_returns, final_portfolio_values = simulation.run_simulation(
        int(num_simulations), int(time_horizon)
    )

    loading.empty()
    render_dashboard(all_cumulative_returns, final_portfolio_values, initial_investment, end_date,
                     int(num_simulations), stock_data, weights, ticker_names)

if __name__ == '__main__':
    main()
