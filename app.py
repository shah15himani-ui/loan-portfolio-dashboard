
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Loan Portfolio Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Loan Portfolio Dashboard")
st.caption("Analyse loan applications, bank performance and disbursements.")

# --------------------------------
# FILE UPLOAD
# --------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload Loan Excel File",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload your loan_records.xlsx file to begin.")
    st.stop()

# --------------------------------
# LOAD AND CLEAN DATA
# --------------------------------

df = pd.read_excel(uploaded_file)

# Remove completely empty columns
df = df.dropna(axis=1, how="all")

# Clean text columns
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()

# Convert loan amount
df["Loan Amount"] = pd.to_numeric(
    df["Loan Amount"], errors="coerce"
)

# Convert date
df["Date"] = pd.to_datetime(
    df["Date"], errors="coerce", dayfirst=True
)

# Remove invalid records
df = df.dropna(subset=["Loan Amount", "Date"])

if df.empty:
    st.error("No valid loan records found.")
    st.stop()

# --------------------------------
# SIDEBAR FILTERS
# --------------------------------

st.sidebar.header("Dashboard Filters")

banks = sorted(df["Bank Name"].dropna().unique())
loan_types = sorted(df["Type of Loan"].dropna().unique())
statuses = sorted(df["Status"].dropna().unique())
executives = sorted(df["Executive Name"].dropna().unique())

selected_banks = st.sidebar.multiselect(
    "Select Bank",
    banks,
    default=banks
)

selected_loans = st.sidebar.multiselect(
    "Select Loan Type",
    loan_types,
    default=loan_types
)

selected_status = st.sidebar.multiselect(
    "Select Status",
    statuses,
    default=statuses
)

selected_executives = st.sidebar.multiselect(
    "Select Executive",
    executives,
    default=executives
)

search = st.sidebar.text_input("Search Customer")

# --------------------------------
# APPLY FILTERS
# --------------------------------

filtered_df = df[
    (df["Bank Name"].isin(selected_banks)) &
    (df["Type of Loan"].isin(selected_loans)) &
    (df["Status"].isin(selected_status)) &
    (df["Executive Name"].isin(selected_executives))
].copy()

if search:
    search_columns = [
        "Customer Name",
        "Bank Name",
        "Type of Loan",
        "Executive Name"
    ]

    mask = filtered_df[search_columns].fillna("").apply(
        lambda col: col.str.contains(
            search, case=False, regex=False
        )
    ).any(axis=1)

    filtered_df = filtered_df[mask]

# --------------------------------
# KPI CALCULATIONS
# --------------------------------

total_applications = len(filtered_df)

total_amount = filtered_df["Loan Amount"].sum()

disbursed_df = filtered_df[
    filtered_df["Status"] == "Disbursed"
]

disbursed_amount = disbursed_df["Loan Amount"].sum()

pending_applications = (
    filtered_df["Status"] == "Pending"
).sum()

disbursed_applications = len(disbursed_df)

# --------------------------------
# KPI DISPLAY
# --------------------------------

st.subheader("Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Applications",
    f"{total_applications:,}"
)

col2.metric(
    "Total Loan Amount",
    f"₹{total_amount / 10000000:.2f} Cr"
)

col3.metric(
    "Disbursed Amount",
    f"₹{disbursed_amount / 10000000:.2f} Cr"
)

col4.metric(
    "Pending Applications",
    f"{pending_applications:,}"
)

st.divider()

# --------------------------------
# APPLICATION STATUS CHART
# --------------------------------

st.subheader("Application Status Analysis")

col1, col2 = st.columns(2)

with col1:

    status_data = (
        filtered_df["Status"]
        .value_counts()
        .reset_index()
    )

    status_data.columns = [
        "Status", "Applications"
    ]

    fig1 = px.pie(
        status_data,
        names="Status",
        values="Applications",
        hole=0.45,
        title="Applications by Status"
    )

    st.plotly_chart(fig1, use_container_width=True)

# --------------------------------
# LOAN TYPE CHART
# --------------------------------

with col2:

    loan_data = (
        filtered_df.groupby("Type of Loan")["Loan Amount"]
        .sum()
        .reset_index()
    )

    fig2 = px.bar(
        loan_data,
        x="Type of Loan",
        y="Loan Amount",
        title="Loan Amount by Loan Type",
        text_auto=".2s"
    )

    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------
# BANK PERFORMANCE
# --------------------------------

st.subheader("Bank Performance")

bank_data = (
    filtered_df.groupby("Bank Name")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Loan Amount", ascending=False)
)

fig3 = px.bar(
    bank_data,
    x="Bank Name",
    y="Loan Amount",
    title="Loan Amount by Bank",
    color="Loan Amount"
)

st.plotly_chart(fig3, use_container_width=True)

# --------------------------------
# EXECUTIVE PERFORMANCE
# --------------------------------

st.subheader("Executive Performance")

executive_data = (
    filtered_df.groupby("Executive Name")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Loan Amount", ascending=False)
)

fig4 = px.bar(
    executive_data,
    x="Executive Name",
    y="Loan Amount",
    title="Loan Amount by Executive"
)

st.plotly_chart(fig4, use_container_width=True)

# --------------------------------
# MONTHLY TREND
# --------------------------------

st.subheader("Monthly Loan Trend")

monthly_data = filtered_df.copy()

monthly_data["Month"] = (
    monthly_data["Date"].dt.to_period("M").astype(str)
)

monthly_data = (
    monthly_data.groupby("Month")["Loan Amount"]
    .sum()
    .reset_index()
)

fig5 = px.line(
    monthly_data,
    x="Month",
    y="Loan Amount",
    markers=True,
    title="Monthly Loan Amount Trend"
)

st.plotly_chart(fig5, use_container_width=True)

# --------------------------------
# DETAILED LOAN RECORDS
# --------------------------------

st.subheader("Detailed Loan Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------
# DOWNLOAD FILTERED DATA
# --------------------------------

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="filtered_loan_records.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully!")
