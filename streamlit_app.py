import streamlit as st
import pandas as pd

# Load the data
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Convert 'created' and 'updated' columns to datetime
    df['created'] = pd.to_datetime(df['created']).dt.date
    df['updated'] = pd.to_datetime(df['updated']).dt.date

    # Add a date range picker
    st.sidebar.header("Filter by Date Range")
    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        [df['created'].min(), df['created'].max()]
    )

    # Filter data based on the selected date range
    df = df[(df['created'] >= start_date) & (df['created'] <= end_date)]

    # Calculate the start of the week for 'created' and 'updated' columns (date only)
    df['week_created'] = df['created'] - pd.to_timedelta(pd.to_datetime(df['created']).dt.weekday, unit='D').dt.date
    df['week_updated'] = df['updated'] - pd.to_timedelta(pd.to_datetime(df['updated']).dt.weekday, unit='D').dt.date

    # Prospect Progression Tracking
    st.header("Prospect Progression Tracking")

    # Track each opportunity's progression from one milestone to the next
    df_sorted = df.sort_values(by=['opportunity_id', 'created'])
    df_progression = df_sorted.groupby('opportunity_id').agg({
        'previous_milestone': 'first',
        'milestone': 'last'
    }).reset_index()

    # Count the transitions
    df_transition = df_progression.groupby(['previous_milestone', 'milestone']).size().unstack(fill_value=0)

    st.write("This table shows the number of unique prospects transitioning between milestones.")
    st.dataframe(df_transition)

    # Detailed Progression for Each Opportunity
    st.header("Detailed Opportunity Progression")

    # Filter opportunities that started with "First Call"
    df_first_call = df_sorted[df_sorted['milestone'] == "First Call"]

    for opportunity_id in df_first_call['opportunity_id'].unique():
        df_opportunity = df_sorted[df_sorted['opportunity_id'] == opportunity_id]
        st.subheader(f"Opportunity ID: {opportunity_id}")
        st.write(f"Name: {df_opportunity['name'].iloc[0]}")
        st.write("Progression:")
        st.write(df_opportunity[['milestone', 'created', 'updated']])

    # Stagnation Identification
    st.header("Stagnation Identification")
    stagnation_weeks = (pd.to_datetime(df['updated']) - pd.to_datetime(df['created'])).dt.days / 7
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
