# app.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Import functions from the src directory
from src import data_processor, ml_model, visualizer, utils

# --- Configuration ---
st.set_page_config(
    page_title="Smart Expense Predictor",
    page_icon="💰",
    layout="wide"
)

# --- File Paths ---
DATA_DIR = "data"
MODEL_DIR = "models"
EXPENSE_FILE = os.path.join(DATA_DIR, "expenses.csv")
MODEL_FILE = os.path.join(MODEL_DIR, "model.pkl")

# --- Session State and Data Handling ---
def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if 'df_expenses' not in st.session_state:
        st.session_state.df_expenses = data_processor.load_expenses(EXPENSE_FILE)
    
    if 'model' not in st.session_state:
        st.session_state.model = ml_model.load_model(MODEL_FILE)

    if 'budget' not in st.session_state:
        st.session_state.budget = 10000.0  # Default budget

    if 'categories' not in st.session_state:
        default_categories = ['Groceries', 'Rent', 'Transport', 'Entertainment', 'Utilities', 'Other']
        existing_categories = []
        if not st.session_state.df_expenses.empty:
            existing_categories = st.session_state.df_expenses['Category'].unique().tolist()
        st.session_state.categories = sorted(
    list(set(str(cat) for cat in default_categories + existing_categories))
)

def _update_and_save_data(df):
    """Central function to process, save data, and retrain the model."""
    # Ensure 'Date' is datetime and sort
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date', ascending=True).reset_index(drop=True)
    df['Month'] = df['Date'].dt.to_period('M')
    
    # Update session state
    st.session_state.df_expenses = df
    
    # Save to CSV
    data_processor.save_expenses(df, EXPENSE_FILE)
    
    # Train and save the model
    train_and_save_model()

def train_and_save_model():
    """Trains the model if there's enough data and saves it."""
    df = st.session_state.df_expenses
    if not df.empty and df['Month'].nunique() > 1:
        monthly_df = data_processor.aggregate_monthly_expenses(df)
        X_train = monthly_df[['Month_Num']]
        y_train = monthly_df['Amount']
        
        model = ml_model.train_model(X_train, y_train)
        st.session_state.model = model
        ml_model.save_model(model, MODEL_FILE)
        st.toast("Model trained and updated successfully!", icon="🤖")
    else:
        st.session_state.model = None

# --- UI Sections ---
def render_dashboard():
    """Renders the main dashboard with predictions and visualizations."""
    st.title("📊 Dashboard")
    st.markdown("An overview of your expenses and future predictions.")

    df = st.session_state.df_expenses
    model = st.session_state.model

    if df.empty:
        st.warning("No expense data found. Please upload a CSV or add an expense to get started.")
        return

    # --- Metrics ---
    col1, col2, col3 = st.columns(3)
    total_expense = df['Amount'].sum()
    monthly_summary = df.groupby('Month')['Amount'].sum()
    avg_monthly_expense = monthly_summary.mean() if not monthly_summary.empty else 0
    
    col1.metric("Total Expenses", f"₹{total_expense:,.2f}")
    col2.metric("Avg. Monthly Expense", f"₹{avg_monthly_expense:,.2f}")

    # --- Prediction ---
    if model:
        monthly_df = data_processor.aggregate_monthly_expenses(df)
        last_month_num = monthly_df['Month_Num'].max()
        prediction = ml_model.predict_next_month(model, last_month_num)
        
        col3.metric("Predicted Next Month's Expense", f"₹{prediction:,.2f}")
        
        is_over, message = utils.check_budget_warning(prediction, st.session_state.budget)
        if is_over:
            st.error(message)
        else:
            st.success(message)
    else:
        col3.metric("Predicted Next Month's Expense", "N/A")
        st.info("Not enough data to train a prediction model. Add at least two months of expenses.")

    # --- Visualizations ---
    st.markdown("---")
    st.subheader("Visual Insights")

    tab1, tab2, tab3 = st.tabs(["Forecast", "Category Breakdown", "Expense Trend"])

    with tab1:
        if model:
            monthly_df = data_processor.aggregate_monthly_expenses(df)
            next_month_str = utils.get_next_month_date_str(monthly_df['Month'].max())
            fig_forecast = visualizer.plot_monthly_forecast(monthly_df, prediction, next_month_str)
            st.pyplot(fig_forecast)
        else:
            st.info("A forecast chart will be available once enough data is present.")
            
    with tab2:
        fig_category = visualizer.plot_category_breakdown(df)
        st.pyplot(fig_category)

    with tab3:
        fig_trend = visualizer.plot_expense_trend(df)
        st.pyplot(fig_trend)

def render_add_expense():
    """Renders the form to add a new expense."""
    st.title("➕ Add New Expense")
    st.markdown("Use this form to add a new transaction to your records.")

    with st.form("add_expense_form", clear_on_submit=True):
        date = st.date_input("Date", value=datetime.now())
        amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")
        category = st.selectbox("Category", options=st.session_state.categories)
        description = st.text_input("Description (Optional)")
        
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            new_expense = pd.DataFrame([{
                'Date': pd.to_datetime(date),
                'Amount': amount,
                'Category': category,
                'Description': description
            }])
            
            updated_df = pd.concat([st.session_state.df_expenses, new_expense], ignore_index=True)
            _update_and_save_data(updated_df)
            
            st.success("Expense added successfully!")
            st.toast("Your expense has been recorded.", icon="🎉")

def render_manage_expenses():
    """Renders the section to view, edit, and delete expenses."""
    st.title("🗂️ Manage Expenses")
    st.markdown("View, edit, or delete your expense records here.")

    if st.session_state.df_expenses.empty:
        st.warning("No expenses to manage.")
        return

    edited_df = st.data_editor(
        st.session_state.df_expenses.drop(columns=['Month'], errors='ignore'),
        num_rows="dynamic",
        key="expense_editor",
        use_container_width=True
    )

    if st.button("Save Changes"):
        _update_and_save_data(edited_df)
        st.success("Changes saved successfully!")
        st.toast("Your records have been updated.", icon="💾")
        st.rerun()

# --- Main App ---
def main():
    """Main function to run the Streamlit app."""
    initialize_session_state()

    with st.sidebar:
        st.header("Smart Expense Predictor 💰")
        
        page = st.radio("Navigation", ["Dashboard", "Add Expense", "Manage Expenses"], key="navigation")
        st.markdown("---")
        
        st.session_state.budget = st.number_input(
            "Set Your Monthly Budget (₹)",
            min_value=0.0,
            value=st.session_state.budget,
            step=500.0,
            format="%.2f"
        )

        st.markdown("---")

        uploaded_file = st.file_uploader("Upload Your expenses.csv", type=['csv'])
        if uploaded_file is not None:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(EXPENSE_FILE, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.df_expenses = data_processor.load_expenses(EXPENSE_FILE)
            train_and_save_model()
            st.success("File uploaded and data loaded successfully!")
            st.rerun()

        st.markdown("---")

        if st.button("Force Retrain Model"):
            with st.spinner("Training model..."):
                train_and_save_model()

        
        #auther
        #st.markdown("---------udhayachandra---------")

    if page == "Dashboard":
        render_dashboard()
    elif page == "Add Expense":
        render_add_expense()
    elif page == "Manage Expenses":
        render_manage_expenses()

if __name__ == "__main__":
    main()