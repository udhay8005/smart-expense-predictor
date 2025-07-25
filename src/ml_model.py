# src/ml_model.py

import pickle
import os
import xgboost as xgb
import numpy as np

def train_model(X_train, y_train):
    """
    Trains an XGBoost Regressor model.

    Args:
        X_train (pd.DataFrame or np.ndarray): The training feature data.
        y_train (pd.Series or np.ndarray): The training target data.

    Returns:
        xgb.XGBRegressor: The trained model.
    """
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=3)
    model.fit(X_train, y_train)
    return model

def predict_next_month(model, last_month_num):
    """
    Predicts the expense for the next month.

    Args:
        model (xgb.XGBRegressor): The trained model.
        last_month_num (int): The numerical representation of the last month.

    Returns:
        float: The predicted expense for the next month.
    """
    next_month_num = np.array([[last_month_num + 1]])
    prediction = model.predict(next_month_num)
    return float(prediction[0])

def save_model(model, path):
    """
    Saves the trained model to a file using pickle.

    Args:
        model: The model to save.
        path (str): The file path to save the model to.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(model, f)
    except Exception as e:
        print(f"Error saving model to {path}: {e}")


def load_model(path):
    """
    Loads a saved model from a file.

    Args:
        path (str): The file path of the model.

    Returns:
        The loaded model, or None if the file is not found or an error occurs.
    """
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading model from {path}: {e}")
        return None

