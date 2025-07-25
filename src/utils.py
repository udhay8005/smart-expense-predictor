# src/utils.py

import pandas as pd

def check_budget_warning(prediction, budget):
    """
    Checks if the predicted expense exceeds the budget.

    Args:
        prediction (float): The predicted expense amount.
        budget (float): The user-defined monthly budget.

    Returns:
        tuple: A tuple containing a boolean (True if over budget) and a message string.
    """
    if budget > 0 and prediction > budget:
        overage = prediction - budget
        message = f"Warning: Predicted expense (₹{prediction:,.2f}) is ₹{overage:,.2f} over your budget of ₹{budget:,.2f}!"
        return True, message
    elif budget > 0:
        under = budget - prediction
        message = f"Good News: Predicted expense (₹{prediction:,.2f}) is ₹{under:,.2f} under your budget of ₹{budget:,.2f}."
        return False, message
    else:
        return False, "Set a budget to get a comparison."

def get_next_month_date_str(last_month_period):
    """
    Gets the string representation for the next month.

    Args:
        last_month_period (pd.Period): The last month period from the data.

    Returns:
        str: A string for the next month (e.g., '2024-08').
    """
    if last_month_period is None:
        # Default to next month from today if no data exists
        return (pd.Timestamp.now() + pd.DateOffset(months=1)).strftime('%Y-%m')
        
    next_month = last_month_period + 1
    return next_month.strftime('%Y-%m')

