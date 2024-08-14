import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Convert 'created' and 'updated' columns to datetime
    df['created'] = pd.to_datetime(df['created'])
    df['updated'] = pd.to_datetime(df['updated'])

    # Add a date range picker
    st.sidebar.header("Filter by Date Range")
    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        [df['created'].min().date(), df['created'].max().date()]
    )

    # Filter data based on the selected date range
    df = df[(df['created'].dt.date >= start_date) & (df['created'].dt.date <= end_date)]

    # Calculate the start of the week for 'created' and 'updated' columns
    df['week_created'] = df['created'] - pd.to_timedelta(df['created'].dt.weekday, unit='D')
    df['week_updated'] = df['updated'] - pd.to_timedelta(df['updated'].dt.weekday, unit='D')

    # Milestone Movement Overview
    milestone_pivot = df.pivot_table(index='milestone', columns='week_created', aggfunc='count', values='opportunity_id', fill_value=0)
    
    st.header("Milestone Movement Overview")
    st.write("This table shows the number of prospects at each milestone per week.")
    st.dataframe(milestone_pivot)

    st.subheader("Milestone Trend Over Time")
    st.line_chart(milestone_pivot.T)

    # Prospect Progression Tracking
    st.header("Prospect Progression Tracking")
    df['progress'] = df['milestone'] != df['previous_milestone']
    df_progress = df[df['progress']].groupby(['previous_milestone', 'milestone']).size().unstack(fill_value=0)
    
    st.write("This table shows the number of prospects transitioning between milestones.")
    st.dataframe(df_progress)

    st.subheader("Milestone Transition Bar Chart")
    st.bar_chart(df_progress)

    # Stagnation Identification
    st.header("Stagnation Identification")
    stagnation_weeks = (df['updated'] - df['created']).dt.days / 7
    df_stagnant = df[(stagnation_weeks > 4) & (df['milestone'] == df['previous_milestone'])]

    st.write(f"There are {df_stagnant.shape[0]} stagnant prospects.")
    st.write("These are the prospects that have not moved for over 4 weeks:")
    st.dataframe(df_stagnant)

    # Lost Reason Analysis
    st.header("Lost Reason Analysis")
    lost_reasons = df['lost reason'].value_counts()
    
    st.subheader("Lost Reasons Distribution")
    st.bar_chart(lost_reasons)

    # Weekly Summary Dashboard
    st.header("Weekly Summary Dashboard")
    summary_pivot = df.pivot_table(index='milestone', columns='week_created', aggfunc='count', values='opportunity_id', fill_value=0)
    st.write("Total prospects per milestone:")
    st.dataframe(summary_pivot)

    if st.button("Refresh Data"):
        st.experimental_rerun()

else:
    st.write("Please upload an Excel file to proceed.")
