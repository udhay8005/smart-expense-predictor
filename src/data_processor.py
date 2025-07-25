# src/data_processor.py

import pandas as pd
import os

def load_expenses(file_path):
    """
    Loads expense data from a CSV file, sorts it, and adds time-based features.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the expense data.
                      Returns an empty DataFrame if the file is not found.
    """
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=['Date', 'Amount', 'Category', 'Description'])
        
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        # Sort by date to ensure chronological order
        df = df.sort_values(by='Date', ascending=True).reset_index(drop=True)
        df['Month'] = df['Date'].dt.to_period('M')
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return pd.DataFrame(columns=['Date', 'Amount', 'Category', 'Description'])

def aggregate_monthly_expenses(df):
    """
    Aggregates expenses by month and creates a robust month number for ML modeling.

    Args:
        df (pd.DataFrame): The input DataFrame with expense data.

    Returns:
        pd.DataFrame: A DataFrame with total expenses for each month and a 'Month_Num' feature.
    """
    if df.empty:
        return pd.DataFrame(columns=['Month', 'Amount', 'Month_Num'])
        
    monthly_expenses = df.groupby('Month')['Amount'].sum().reset_index()
    
    # Create a robust Month_Num that is resilient to gaps in data
    monthly_expenses['Month'] = monthly_expenses['Month'].dt.to_timestamp()
    min_date = monthly_expenses['Month'].min()
    monthly_expenses['Month_Num'] = ((monthly_expenses['Month'].dt.year - min_date.year) * 12 + 
                                     (monthly_expenses['Month'].dt.month - min_date.month))
    monthly_expenses['Month'] = monthly_expenses['Month'].dt.to_period('M')
    
    return monthly_expenses

def save_expenses(df, file_path):
    """
    Saves the DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        file_path (str): The path to the destination CSV file.
    """
    try:
        # Create a copy to avoid SettingWithCopyWarning
        df_to_save = df.copy()

        # Drop the 'Month' column if it exists, as it's derived
        if 'Month' in df_to_save.columns:
            df_to_save = df_to_save.drop(columns=['Month'])
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df_to_save.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")
