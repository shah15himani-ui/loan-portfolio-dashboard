
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Loan Portfolio Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: #F5F8FC;
}

/* Main title */
h1 {
    color: #153653;
    font-weight: 750;
}

h2, h3 {
    color: #153653;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #102A43 0%,
        #163B5C 100%
    );
}

/* Sidebar text */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] span {
    color: white;
}

/* Sidebar dropdown */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFFFF;
    border-radius: 9px;
    border: 1px solid #DCE5EF;
}

/* Dropdown text */
[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #183B56;
}

/* Sidebar input */
[data-testid="stSidebar"] input {
    background-color: white;
    color: #183B56;
    border-radius: 9px;
}

/* Expandable sections */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    margin-bottom: 10px;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton button {
    background-color: #F28C28;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 650;
    transition: 0.2s ease;
}

[data-testid="stSidebar"] .stButton button:hover {
    background-color: #D97616;
    color: white;
    transform: translateY(-2px);
}

/* KPI cards */
[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #E3EAF2;
    box-shadow: 0 3px 12px rgba(20, 50, 80, 0.05);
}

[data-testid="stMetricLabel"] {
    color: #63758A;
}

[data-testid="stMetricValue"] {
    color: #153653;
    font-weight: 750;
}

/* Divider */
hr {
    border-color: #DCE5EF;
}

/* Info box */
.stAlert {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. HEADER
# =====================================================

st.title("💰 Loan Portfolio Dashboard")

st.markdown(
    "Monitor loan applications, portfolio performance, "
    "bank activity and executive performance."
)

st.divider()


# =====================================================
# 4. FILE UPLOAD
# =====================================================

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Loan Records",
    type=["xlsx"]
)

if uploaded_file is None:

    st.info(
        "Please upload your loan_records.xlsx file "
        "using the sidebar to view your dashboard."
    )

    st.stop()


# =====================================================
# 5. LOAD AND CLEAN DATA
# =====================================================

try:

    df = pd.read_excel(uploaded_file)

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    # Required columns
    required_columns = [
        "Customer Name",
        "Type of Loan",
        "Status",
        "Loan Amount",
        "Bank Name",
        "Executive Name",
        "Date"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            f"Missing required columns: {missing_columns}"
        )

        st.stop()

    # Clean text columns
    for col in df.select_dtypes(include="object").columns:

        df[col] = df[col].str.strip()

    # Convert loan amount
    df["Loan Amount"] = pd.to_numeric(
        df["Loan Amount"],
        errors="coerce"
    )

    # Convert date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        dayfirst=True
    )

    # Remove invalid important records
    df = df.dropna(
        subset=["Loan Amount", "Date"]
    )

    if df.empty:

        st.error("No valid loan records found.")

        st.stop()

except Exception as e:

    st.error(f"Error loading Excel file: {e}")

    st.stop()


# =====================================================
# 6. FILTER OPTIONS
# =====================================================

bank_options = (
    ["All Banks"] +
    sorted(df["Bank Name"].dropna().unique().tolist())
)

loan_options = (
    ["All Loan Types"] +
    sorted(df["Type of Loan"].dropna().unique().tolist())
)

status_options = (
    ["All Statuses"] +
    sorted(df["Status"].dropna().unique().tolist())
)

executive_options = (
    ["All Executives"] +
    sorted(df["Executive Name"].dropna().unique().tolist())
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()


# =====================================================
# 7. RESET FILTER FUNCTION
# =====================================================

def reset_filters():

    st.session_state["bank_filter"] = "All Banks"

    st.session_state["loan_filter"] = "All Loan Types"

    st.session_state["status_filter"] = "All Statuses"

    st.session_state["executive_filter"] = "All Executives"

    st.session_state["date_filter"] = (
        min_date,
        max_date
    )

    st.session_state["customer_search"] = ""


# =====================================================
# 8. INTERACTIVE SIDEBAR
# =====================================================

st.sidebar.markdown("## 🎛️ Dashboard Filters")

st.sidebar.caption(
    "Customize your loan portfolio view"
)

# Bank selection
with st.sidebar.expander(
    "🏦 Bank Selection",
    expanded=True
):

    selected_bank = st.selectbox(
        "Select Bank",
        bank_options,
        key="bank_filter"
    )


# Loan details
with st.sidebar.expander(
    "💰 Loan Details",
    expanded=True
):

    selected_loan = st.selectbox(
        "Type of Loan",
        loan_options,
        key="loan_filter"
    )

    selected_status = st.selectbox(
        "Application Status",
        status_options,
        key="status_filter"
    )


# Executive selection
with st.sidebar.expander(
    "👤 Executive Details",
    expanded=False
):

    selected_executive = st.selectbox(
        "Select Executive",
        executive_options,
        key="executive_filter"
    )


# Date filter
with st.sidebar.expander(
    "📅 Date Range",
    expanded=False
):

    selected_dates = st.date_input(
        "Select Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )


# Customer search
with st.sidebar.expander(
    "🔍 Customer Search",
    expanded=False
):

    search = st.text_input(
        "Customer Name",
        placeholder="Search customer...",
        key="customer_search"
    )


# Reset button
st.sidebar.button(
    "↻ Reset All Filters",
    on_click=reset_filters,
    use_container_width=True
)


# =====================================================
# 9. APPLY FILTERS
# =====================================================

filtered_df = df.copy()

# Bank filter
if selected_bank != "All Banks":

    filtered_df = filtered_df[
        filtered_df["Bank Name"] == selected_bank
    ]


# Loan type filter
if selected_loan != "All Loan Types":

    filtered_df = filtered_df[
        filtered_df["Type of Loan"] == selected_loan
    ]


# Status filter
if selected_status != "All Statuses":

    filtered_df = filtered_df[
        filtered_df["Status"] == selected_status
    ]


# Executive filter
if selected_executive != "All Executives":

    filtered_df = filtered_df[
        filtered_df["Executive Name"] == selected_executive
    ]


# Date filter
if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date) &
        (filtered_df["Date"].dt.date <= end_date)
    ]


# Customer search
if search:

    filtered_df = filtered_df[
        filtered_df["Customer Name"].str.contains(
            search,
            case=False,
            na=False,
            regex=False
        )
    ]


# Sidebar record count
st.sidebar.markdown("---")

st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} applications"
)


# =====================================================
# 10. KPI CALCULATIONS
# =====================================================

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


# =====================================================
# 11. KPI DISPLAY
# =====================================================

st.subheader("📊 Portfolio Overview")

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


# =====================================================
# 12. APPLICATION STATUS ANALYSIS
# =====================================================

st.subheader("📌 Application Status Analysis")

col1, col2 = st.columns(2)

with col1:

    status_data = (
        filtered_df["Status"]
        .value_counts()
        .reset_index()
    )

    status_data.columns = [
        "Status",
        "Applications"
    ]

    if not status_data.empty:

        fig1 = px.pie(
            status_data,
            names="Status",
            values="Applications",
            hole=0.48,
            title="Applications by Status",
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig1.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#153653"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    else:

        st.info("No status data available.")


# =====================================================
# 13. LOAN TYPE ANALYSIS
# =====================================================

with col2:

    loan_data = (
        filtered_df.groupby("Type of Loan")["Loan Amount"]
        .sum()
        .reset_index()
        .sort_values("Loan Amount", ascending=False)
    )

    if not loan_data.empty:

        fig2 = px.bar(
            loan_data,
            x="Type of Loan",
            y="Loan Amount",
            color="Type of Loan",
            title="Loan Amount by Loan Type",
            text_auto=".2s"
        )

        fig2.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
            font_color="#153653"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:

        st.info("No loan type data available.")


st.divider()


# =====================================================
# 14. BANK PERFORMANCE
# =====================================================

st.subheader("🏦 Bank Performance")

bank_data = (
    filtered_df.groupby("Bank Name")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Loan Amount", ascending=False)
)

if not bank_data.empty:

    fig3 = px.bar(
        bank_data,
        x="Loan Amount",
        y="Bank Name",
        orientation="h",
        color="Loan Amount",
        title="Loan Amount by Bank",
        text_auto=".2s",
        color_continuous_scale="Blues"
    )

    fig3.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color="#153653",
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

else:

    st.info("No bank data available.")


st.divider()


# =====================================================
# 15. EXECUTIVE PERFORMANCE
# =====================================================

st.subheader("👥 Executive Performance")

executive_data = (
    filtered_df.groupby("Executive Name")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Loan Amount", ascending=False)
)

if not executive_data.empty:

    fig4 = px.bar(
        executive_data,
        x="Executive Name",
        y="Loan Amount",
        title="Loan Amount by Executive",
        color="Loan Amount",
        text_auto=".2s",
        color_continuous_scale="Teal"
    )

    fig4.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color="#153653"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

else:

    st.info("No executive data available.")


st.divider()


# =====================================================
# 16. MONTHLY LOAN TREND
# =====================================================

st.subheader("📈 Monthly Loan Trend")

monthly_data = filtered_df.copy()

monthly_data["Month"] = (
    monthly_data["Date"].dt.to_period("M").astype(str)
)

monthly_data = (
    monthly_data.groupby("Month")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Month")
)

if not monthly_data.empty:

    fig5 = px.line(
        monthly_data,
        x="Month",
        y="Loan Amount",
        markers=True,
        title="Monthly Loan Amount Trend"
    )

    fig5.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig5.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color="#153653",
        xaxis_title="Month",
        yaxis_title="Loan Amount"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

else:

    st.info("No monthly data available.")


st.divider()


# =====================================================
# 17. DETAILED LOAN RECORDS
# =====================================================

st.subheader("📋 Detailed Loan Records")

st.caption(
    f"Total filtered records: {len(filtered_df):,}"
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# =====================================================
# 18. DOWNLOAD FILTERED DATA
# =====================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv_data,
    file_name="filtered_loan_records.csv",
    mime="text/csv",
    use_container_width=True
)


# =====================================================
# 19. FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    "<center style='color:#718096;'>"
    "Loan Portfolio Analytics Dashboard"
    "</center>",
    unsafe_allow_html=True
)
