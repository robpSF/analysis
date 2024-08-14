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

    # Ensure correct sorting and get the most recent entry for each opportunity_id
    df = df.sort_values(by=['opportunity_id', 'created']).drop_duplicates(subset=['opportunity_id'], keep='last')

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

        # Table showing the movement for each milestone
        st.header("Milestone Movement Summary")

        # Create a summary table
        df['static'] = df['milestone'] == df['previous_milestone']
        summary_table = df.groupby(['milestone', 'static']).size().unstack(fill_value=0)
        summary_table.columns = ['Moved', 'Static']
        summary_table.reset_index(inplace=True)

        st.write("This table shows how many opportunities are static and how many have moved to a different milestone.")
        st.dataframe(summary_table)

        # Summary of time spent at each milestone (if needed)
        st.subheader("Summary of Time Spent at Each Milestone")
        summary = df.groupby('milestone')['created'].count().reset_index()
        summary.columns = ['Milestone', 'Number of Opportunities']
        st.dataframe(summary)

    else:
        st.error("No valid 'created' dates found after cleaning. Please check your data.")
else:
    st.write("Please upload an Excel or CSV file to proceed.")
