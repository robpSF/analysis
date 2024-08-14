import streamlit as st
import pandas as pd

# Load the data
uploaded_file = st.file_uploader("Upload your Excel file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Convert 'created' and 'updated' columns to datetime
    df['created'] = pd.to_datetime(df['created'], errors='coerce')
    df['updated'] = pd.to_datetime(df['updated'], errors='coerce')

    # Drop rows where 'created' is NaT after conversion
    df = df.dropna(subset=['created'])

    # Ensure correct sorting
    df = df.sort_values(by=['opportunity_id', 'created'])

    # Calculate days spent at each milestone
    df['days_at_milestone'] = df.groupby('opportunity_id')['created'].diff().shift(-1).dt.days

    # Handle the last milestone for each opportunity
    df['days_at_milestone'].fillna((pd.Timestamp.now() - df['created']).dt.days, inplace=True)

    # Check if the 'created' column contains valid dates after dropping NaT
    if not df.empty and df['created'].notna().any():
        # Add a date range picker with valid date range
        st.sidebar.header("Filter by Date Range")
        start_date, end_date = st.sidebar.date_input(
            "Select date range",
            [df['created'].min().date(), df['created'].max().date()]
        )

        # Filter data based on the selected date range
        df = df[(df['created'].dt.date >= start_date) & (df['created'].dt.date <= end_date)]

        # Prospect Progression Tracking with Days at Each Milestone
        st.header("Prospect Progression Tracking with Days at Each Milestone")

        # Display the updated DataFrame with days spent at each milestone
        st.write(df[['opportunity_id', 'name', 'milestone', 'created', 'updated', 'days_at_milestone']])

        # Summary of time spent at each milestone
        st.subheader("Summary of Time Spent at Each Milestone")
        summary = df.groupby('milestone')['days_at_milestone'].mean().reset_index()
        summary.columns = ['Milestone', 'Average Days Spent']
        st.dataframe(summary)

    else:
        st.error("No valid 'created' dates found after cleaning. Please check your data.")
else:
    st.write("Please upload an Excel or CSV file to proceed.")
