# src/visualizer.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_monthly_forecast(monthly_df, prediction, next_month_str):
    """
    Generates a bar plot of monthly expenses with a forecast for the next month.

    Args:
        monthly_df (pd.DataFrame): DataFrame with historical monthly expenses.
        prediction (float): The predicted expense for the next month.
        next_month_str (str): The string representation of the next month (e.g., '2024-08').

    Returns:
        matplotlib.figure.Figure: The plot figure.
    """
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))

    # Historical data
    historical_months = monthly_df['Month'].astype(str)
    historical_amounts = monthly_df['Amount']
    
    # Plot historical data
    ax.bar(historical_months, historical_amounts, color='skyblue', label='Historical Monthly Expenses')

    # Plot forecasted data
    ax.bar(next_month_str, prediction, color='salmon', label=f'Forecasted Expense: ₹{prediction:,.2f}')

    ax.set_title('Monthly Expense History and Forecast', fontsize=16)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Total Expense (₹)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    ax.legend()
    plt.tight_layout()
    
    return fig

def plot_category_breakdown(df):
    """
    Creates a pie chart showing the distribution of expenses by category.

    Args:
        df (pd.DataFrame): The DataFrame containing expense data.

    Returns:
        matplotlib.figure.Figure: The plot figure.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if df.empty or 'Category' not in df.columns:
        ax.text(0.5, 0.5, 'No category data available.', horizontalalignment='center', verticalalignment='center')
        return fig

    category_expenses = df.groupby('Category')['Amount'].sum()
    
    ax.pie(category_expenses, labels=category_expenses.index, autopct='%1.1f%%', startangle=140,
           wedgeprops=dict(width=0.4))
    ax.set_title('Expense Breakdown by Category', fontsize=16)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    return fig

def plot_expense_trend(df):
    """
    Generates a line plot showing the trend of expenses over time.

    Args:
        df (pd.DataFrame): The DataFrame containing expense data.

    Returns:
        matplotlib.figure.Figure: The plot figure.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if df.empty or df['Date'].nunique() < 2:
        ax.text(0.5, 0.5, 'Not enough data to plot a trend.', horizontalalignment='center', verticalalignment='center')
        return fig

    # Resample by day to see trends
    daily_expenses = df.set_index('Date').resample('D')['Amount'].sum().reset_index()

    sns.lineplot(data=daily_expenses, x='Date', y='Amount', ax=ax, marker='o')
    ax.set_title('Daily Expense Trend', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Total Expense (₹)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig
