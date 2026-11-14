
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    .main-header {
        background: linear-gradient(110deg, #172B4D, #2563EB);
        padding: 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 25px;
    }

    .main-header h1 {
        color: white;
        font-size: 32px;
        margin: 0;
    }

    .main-header p {
        color: #DBEAFE;
        margin-top: 8px;
        margin-bottom: 0;
    }

    .kpi-card {
        background: white;
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        min-height: 125px;
    }

    .kpi-title {
        color: #64748B;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .kpi-value {
        color: #172B4D;
        font-size: 27px;
        font-weight: 700;
    }

    .section-title {
        color: #172B4D;
        font-size: 19px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .upload-box {
        background: white;
        padding: 35px;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        text-align: center;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
    }

    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# DATA CLEANING FUNCTION
# =====================================================

REQUIRED_COLUMNS = [
    "Customer Name",
    "Type of Loan",
    "Status",
    "Loan Amount",
    "Bank Name",
    "Executive Name",
    "Date"
]


def clean_loan_data(data):

    data = data.copy()

    # Remove completely empty rows and columns
    data = data.dropna(how="all")
    data = data.dropna(axis=1, how="all")

    # Clean column names
    data.columns = data.columns.astype(str).str.strip()

    # Validate required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # Clean text columns
    text_columns = [
        "Customer Name",
        "Type of Loan",
        "Status",
        "Bank Name",
        "Executive Name"
    ]

    for col in text_columns:
        data[col] = (
            data[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Clean loan amount
    data["Loan Amount"] = (
        data["Loan Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("Rs.", "", regex=False)
        .str.replace("Rs", "", regex=False)
        .str.strip()
    )

    data["Loan Amount"] = pd.to_numeric(
        data["Loan Amount"],
        errors="coerce"
    )

    # Convert dates
    data["Date"] = pd.to_datetime(
        data["Date"],
        dayfirst=True,
        errors="coerce"
    )

    # Remove invalid records
    data = data.dropna(
        subset=["Loan Amount", "Date"]
    )

    return data.reset_index(drop=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def format_crore(value):
    return f"₹{value / 10000000:.2f} Cr"


def create_kpi_card(title, value):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_heading(title):

    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True
    )


def chart_layout(fig, height=350):

    fig.update_layout(
        height=height,
        margin=dict(l=15, r=15, t=35, b=15),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            color="#334155"
        ),
        legend_title_text=""
    )

    return fig


# =====================================================
# LANDING PAGE / FILE UPLOAD
# =====================================================

if "loan_df" not in st.session_state:

    st.markdown("""
        <div style="
            max-width:750px;
            margin:100px auto 25px auto;
            text-align:center;
        ">
            <div style="
                color:#2563EB;
                font-size:13px;
                font-weight:700;
                letter-spacing:2px;
                margin-bottom:12px;
            ">
                LOAN PORTFOLIO MANAGEMENT
            </div>

            <h1 style="
                font-size:38px;
                color:#172B4D;
                margin-bottom:12px;
            ">
                Loan Portfolio Analytics
            </h1>

            <p style="
                color:#64748B;
                font-size:16px;
            ">
                Upload your loan records to explore portfolio
                performance, application status and trends.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="upload-box">',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload your Excel file",
        type=["xlsx"],
        key="landing_upload"
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    if uploaded_file is not None:

        try:
            raw_df = pd.read_excel(uploaded_file)
            cleaned_df = clean_loan_data(raw_df)

            if cleaned_df.empty:
                st.error("The uploaded file has no valid loan records.")
            else:
                st.session_state["loan_df"] = cleaned_df
                st.session_state["loan_filename"] = uploaded_file.name
                st.rerun()

        except Exception as e:
            st.error(f"Unable to process file: {e}")

    st.stop()


# =====================================================
# LOAD DASHBOARD DATA
# =====================================================

df = st.session_state["loan_df"].copy()

df["Year"] = df["Date"].dt.year
df["Month Sort"] = df["Date"].dt.to_period("M")
df["Month Year"] = df["Month Sort"].astype(str)


# =====================================================
# SIDEBAR BRANDING
# =====================================================

st.sidebar.markdown("""
<div style="padding:10px 0 20px 0;">
    <div style="
        color:#2563EB;
        font-size:12px;
        font-weight:700;
        letter-spacing:2px;
    ">
        LOAN PORTFOLIO
    </div>
    <div style="
        color:#172B4D;
        font-size:22px;
        font-weight:800;
    ">
        Analytics Dashboard
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.caption(
    f"File: {st.session_state.get('loan_filename', 'Uploaded file')}"
)

st.sidebar.divider()


# =====================================================
# SIDEBAR BUTTON ACTIONS
# =====================================================

def reset_filters():

    keys = [
        "bank_filter",
        "loan_filter",
        "status_filter",
        "executive_filter",
        "customer_search",
        "date_filter"
    ]

    for key in keys:
        st.session_state.pop(key, None)


if st.sidebar.button(
    "↺ Reset Filters",
    use_container_width=True
):
    reset_filters()
    st.rerun()


if st.sidebar.button(
    "⬆ Upload Another File",
    use_container_width=True
):
    for key in [
        "loan_df",
        "loan_filename",
        "landing_upload"
    ]:
        st.session_state.pop(key, None)

    reset_filters()
    st.rerun()


st.sidebar.divider()


# =====================================================
# SIDEBAR FILTER WIDGETS
# IMPORTANT: THESE ARE STREAMLIT WIDGETS,
# NOT HTML OR MARKDOWN CODE.
# =====================================================

st.sidebar.subheader("Filter Records")

bank_options = (
    ["All Banks"]
    + sorted(df["Bank Name"].dropna().unique().tolist())
)

loan_options = (
    ["All Loan Types"]
    + sorted(df["Type of Loan"].dropna().unique().tolist())
)

status_options = (
    ["All Statuses"]
    + sorted(df["Status"].dropna().unique().tolist())
)

executive_options = (
    ["All Executives"]
    + sorted(df["Executive Name"].dropna().unique().tolist())
)


bank_filter = st.sidebar.selectbox(
    "Bank Name",
    bank_options,
    key="bank_filter"
)

loan_filter = st.sidebar.selectbox(
    "Type of Loan",
    loan_options,
    key="loan_filter"
)

status_filter = st.sidebar.selectbox(
    "Application Status",
    status_options,
    key="status_filter"
)

executive_filter = st.sidebar.selectbox(
    "Executive Name",
    executive_options,
    key="executive_filter"
)


date_filter = st.sidebar.date_input(
    "Date Range",
    value=(
        df["Date"].min().date(),
        df["Date"].max().date()
    ),
    key="date_filter"
)


customer_search = st.sidebar.text_input(
    "Search Customer",
    placeholder="Enter customer name...",
    key="customer_search"
)


# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = df.copy()

if bank_filter != "All Banks":
    filtered_df = filtered_df[
        filtered_df["Bank Name"] == bank_filter
    ]

if loan_filter != "All Loan Types":
    filtered_df = filtered_df[
        filtered_df["Type of Loan"] == loan_filter
    ]

if status_filter != "All Statuses":
    filtered_df = filtered_df[
        filtered_df["Status"] == status_filter
    ]

if executive_filter != "All Executives":
    filtered_df = filtered_df[
        filtered_df["Executive Name"] == executive_filter
    ]

if isinstance(date_filter, (tuple, list)) and len(date_filter) == 2:

    start_date, end_date = date_filter

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        & (filtered_df["Date"].dt.date <= end_date)
    ]

if customer_search.strip():

    filtered_df = filtered_df[
        filtered_df["Customer Name"].str.contains(
            customer_search.strip(),
            case=False,
            na=False
        )
    ]


# =====================================================
# MAIN DASHBOARD HEADER
# =====================================================

st.markdown("""
<div class="main-header">
    <h1>Loan Portfolio Analytics</h1>
    <p>
        Monitor loan applications, portfolio value,
        bank performance and business trends.
    </p>
</div>
""", unsafe_allow_html=True)


# =====================================================
# EMPTY FILTER RESULT
# =====================================================

if filtered_df.empty:

    st.warning(
        "No records found for the selected filters. "
        "Please change your filter selections."
    )

    st.stop()


# =====================================================
# KPI CALCULATIONS
# =====================================================

total_applications = len(filtered_df)

total_loan_amount = filtered_df["Loan Amount"].sum()

disbursed_df = filtered_df[
    filtered_df["Status"].str.lower() == "disbursed"
]

disbursed_amount = disbursed_df["Loan Amount"].sum()

pending_applications = filtered_df[
    filtered_df["Status"].str.lower() == "pending"
].shape[0]


# =====================================================
# KPI CARDS
# =====================================================

st.subheader("Portfolio Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    create_kpi_card(
        "Total Applications",
        f"{total_applications:,}"
    )

with kpi2:
    create_kpi_card(
        "Total Loan Amount",
        format_crore(total_loan_amount)
    )

with kpi3:
    create_kpi_card(
        "Disbursed Amount",
        format_crore(disbursed_amount)
    )

with kpi4:
    create_kpi_card(
        "Pending Applications",
        f"{pending_applications:,}"
    )


st.divider()


# =====================================================
# ROW 1: STATUS AND LOAN TYPE
# =====================================================

col1, col2 = st.columns(2)

with col1:

    section_heading("Application Status")

    status_data = (
        filtered_df["Status"]
        .value_counts()
        .reset_index()
    )

    status_data.columns = ["Status", "Applications"]

    fig_status = px.pie(
        status_data,
        names="Status",
        values="Applications",
        hole=0.58,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_status.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    st.plotly_chart(
        chart_layout(fig_status),
        use_container_width=True
    )


with col2:

    section_heading("Loan Type Distribution")

    loan_data = (
        filtered_df.groupby("Type of Loan")["Loan Amount"]
        .sum()
        .reset_index()
        .sort_values("Loan Amount", ascending=True)
    )

    fig_loan = px.bar(
        loan_data,
        x="Loan Amount",
        y="Type of Loan",
        orientation="h",
        text_auto=".2s",
        color="Loan Amount",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(
        chart_layout(fig_loan),
        use_container_width=True
    )


# =====================================================
# ROW 2: BANK AND EXECUTIVE PERFORMANCE
# =====================================================

col3, col4 = st.columns(2)

with col3:

    section_heading("Bank Performance")

    bank_data = (
        filtered_df.groupby("Bank Name")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Loan_Amount", ascending=True)
    )

    fig_bank = px.bar(
        bank_data,
        x="Loan_Amount",
        y="Bank Name",
        orientation="h",
        text_auto=".2s",
        color="Loan_Amount",
        color_continuous_scale="Blues"
    )

    fig_bank.update_layout(
        xaxis_title="Loan Amount",
        yaxis_title=""
    )

    st.plotly_chart(
        chart_layout(fig_bank, 420),
        use_container_width=True
    )


with col4:

    section_heading("Executive Performance")

    executive_data = (
        filtered_df.groupby("Executive Name")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Loan_Amount", ascending=True)
    )

    fig_executive = px.bar(
        executive_data,
        x="Loan_Amount",
        y="Executive Name",
        orientation="h",
        text_auto=".2s",
        color="Loan_Amount",
        color_continuous_scale="Tealgrn"
    )

    fig_executive.update_layout(
        xaxis_title="Loan Amount",
        yaxis_title=""
    )

    st.plotly_chart(
        chart_layout(fig_executive, 420),
        use_container_width=True
    )


# =====================================================
# ROW 3: MONTHLY LOAN TREND
# =====================================================

section_heading("Monthly Loan Disbursement / Application Trend")

monthly_data = (
    filtered_df.groupby("Month Sort")
    .agg(
        Loan_Amount=("Loan Amount", "sum"),
        Applications=("Customer Name", "count")
    )
    .reset_index()
    .sort_values("Month Sort")
)

monthly_data["Month Year"] = (
    monthly_data["Month Sort"].astype(str)
)

fig_monthly = px.line(
    monthly_data,
    x="Month Year",
    y="Loan_Amount",
    markers=True,
    text="Loan_Amount"
)

fig_monthly.update_traces(
    line=dict(width=3),
    marker=dict(size=8)
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Loan Amount"
)

st.plotly_chart(
    chart_layout(fig_monthly, 400),
    use_container_width=True
)


# =====================================================
# TOP 10 CUSTOMERS
# =====================================================

section_heading("Top 10 Customers by Loan Amount")

top_customers = (
    filtered_df.groupby("Customer Name")["Loan Amount"]
    .sum()
    .nlargest(10)
    .reset_index()
    .sort_values("Loan Amount", ascending=True)
)

fig_customers = px.bar(
    top_customers,
    x="Loan Amount",
    y="Customer Name",
    orientation="h",
    text_auto=".2s",
    color="Loan Amount",
    color_continuous_scale="Blues"
)

fig_customers.update_layout(
    xaxis_title="Loan Amount",
    yaxis_title=""
)

st.plotly_chart(
    chart_layout(fig_customers, 400),
    use_container_width=True
)


# =====================================================
# DETAILED LOAN RECORDS
# =====================================================

section_heading("Detailed Loan Records")

display_columns = [
    "Sr. No.",
    "Customer Name",
    "Type of Loan",
    "Status",
    "Loan Amount",
    "Bank Name",
    "Executive Name",
    "Date"
]

available_columns = [
    col for col in display_columns
    if col in filtered_df.columns
]

display_df = filtered_df[available_columns].copy()

if "Date" in display_df.columns:
    display_df["Date"] = display_df["Date"].dt.strftime(
        "%d-%b-%Y"
    )

if "Loan Amount" in display_df.columns:
    display_df["Loan Amount"] = display_df["Loan Amount"].apply(
        lambda x: f"₹{x:,.2f}"
    )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =====================================================
# DOWNLOAD FILTERED DATA
# =====================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Records",
    data=csv_data,
    file_name="loan_portfolio_filtered_data.csv",
    mime="text/csv",
    use_container_width=False
)


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    color:#94A3B8;
    font-size:12px;
    padding:15px;
">
    Loan Portfolio Analytics Dashboard
    <br>
    Built with Streamlit and Python
</div>
""", unsafe_allow_html=True)
