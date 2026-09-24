import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

def convert_time_steps_to_dates(start_date_str, time_steps):
    """Map simulation step indices to calendar dates (YYYY-MM-DD) counted from start_date_str."""
    start_date = pd.to_datetime(start_date_str)

    # Calculate the actual dates
    actual_dates = [pd.to_datetime(start_date + relativedelta(days=int(step))).strftime('%Y-%m-%d') for step in time_steps]

    return actual_dates

def compute_simulation_metrics(sim_results, initial_investment):
    """Summary risk metrics for an array of final portfolio values."""
    percentile_5 = np.percentile(sim_results, 5)
    std_dev = np.std(sim_results)
    mean_value = np.mean(sim_results)
    return {
        'initial_investment': float(initial_investment),
        'mean': float(mean_value),
        'median': float(np.median(sim_results)),
        'std_dev': float(std_dev),
        'var_95': float(initial_investment - percentile_5),  # VaR at 95% confidence
        'cvar_95': float(initial_investment - np.mean(sim_results[sim_results <= percentile_5])),
        'prob_loss': float(np.mean(sim_results < initial_investment) * 100),
        'sharpe': float((mean_value - initial_investment) / std_dev) if std_dev else 0.0,  # Assuming risk-free rate is 0
    }
