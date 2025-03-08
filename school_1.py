import os
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

DATA_FILE = "monitoring_data.csv"
SCHOOL_DATA_FILE = "school name.csv"

# Function to reset session state
def reset_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]

# User Role Selection
st.sidebar.header("User Authentication")
USER_ROLE = st.sidebar.selectbox("Select Role", ["user", "admin"], index=0)

# Check if school data file exists
district_school_data = pd.DataFrame()
if os.path.exists(SCHOOL_DATA_FILE):
    try:
        district_school_data = pd.read_csv(SCHOOL_DATA_FILE, encoding="utf-8")
        district_school_data.columns = district_school_data.columns.str.strip()  # Strip any leading/trailing whitespace
    except Exception as e:
        st.error(f"Error reading {SCHOOL_DATA_FILE}: {e}")
else:
    st.error(f"File '{SCHOOL_DATA_FILE}' not found. Please upload the correct file.")

# Layout for Data Entry, Filters, and Reset Button
col1, col2 = st.columns([3, 2])

with col1:
    st.sidebar.header("Data Entry")
    with st.sidebar.form("data_form"):
        team_member = st.selectbox("👤 Team Member", ["Anand Mohan", "A Srivastava", "Sajan Snehi", "Sumi Sindhi", "A Raghuvanshi", "Shyam Mishra", "Jeet Kumar", "Shiv Pandit", "Biren Kumar"])

        if "District" in district_school_data.columns and "School" in district_school_data.columns:
            district_options = district_school_data["District"].dropna().unique().tolist() if not district_school_data.empty else []
            district = st.selectbox("📍 District", district_options)

            schools = district_school_data[district_school_data["District"] == district]["School"].dropna().tolist() if not district_school_data.empty else []
            school_name = st.selectbox("🏫 School", schools)
        else:
            st.error("Columns 'District' or 'School' not found in school data.")

        metric_name = st.selectbox("📊 Metric", ["Cleanliness", "Assembly activities", "Presence of Students", "Teachers' presence", "New Edu Init Imp", "Co-curricular Act.", "Others"])
        value = st.text_input("📈 Value", placeholder="Enter metric value (text or number)")
        is_anomaly = st.checkbox("Is this an anomaly?")
        anomaly_comment = st.text_area("💬 Anomaly Comment", placeholder="Enter comments for anomaly (if any)", height=70)
        add_metric = st.form_submit_button("✅ Add")

if USER_ROLE == "admin":
    with col2:
        st.header("Filters")
        if "District" in district_school_data.columns and "School" in district_school_data.columns:
            selected_district = st.selectbox("Filter by District", ["All"] + list(district_school_data["District"].dropna().unique()) if not district_school_data.empty else ["All"])
            selected_school = st.selectbox("Filter by School", ["All"] + list(district_school_data["School"].dropna().unique()) if not district_school_data.empty else ["All"])
        else:
            st.error("Columns 'District' or 'School' not found in school data.")

        selected_metric = st.selectbox("Filter by Metric", ["All", "Cleanliness", "Assembly activities", "Presence of Students", "Teachers' presence", "New Edu Init Imp", "Co-curricular Act.", "Others"])
        st.button("Reset Data", on_click=reset_session_state)

    # Load Data
    if os.path.exists(DATA_FILE) and os.stat(DATA_FILE).st_size > 0:
        data = pd.read_csv(DATA_FILE)
        data.fillna("Unknown", inplace=True)
    else:
        data = pd.DataFrame(columns=["Team Member", "District", "School Name", "Metric Name", "Value", "Is Anomaly", "Anomaly Comment", "Timestamp"])

    # Filter Data
    filtered_data = data.copy()
    if selected_district != "All":
        filtered_data = filtered_data[filtered_data["District"] == selected_district]
    if selected_school != "All":
        filtered_data = filtered_data[filtered_data["School Name"] == selected_school]
    if selected_metric != "All":
        filtered_data = filtered_data[filtered_data["Metric Name"] == selected_metric]

    # Display Filtered Data
    st.header("Filtered Data Display")
    st.dataframe(filtered_data)

    # Anomaly Analysis Button
    show_analysis = st.button("Show Anomaly Analysis")
    if show_analysis and not filtered_data.empty:
        st.header("Anomaly Analysis")
        anomalies = filtered_data[filtered_data["Is Anomaly"] == True]
        if not anomalies.empty:
            anomaly_counts = anomalies.groupby("District")["Metric Name"].count().reset_index()
            fig = px.bar(anomaly_counts, x="District", y="Metric Name", title="Anomalies by District")
            st.plotly_chart(fig)
        else:
            st.info("No anomalies detected.")
