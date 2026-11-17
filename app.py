
import streamlit as st
import pandas as pd
import plotly.express as px
import html

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

st.html("""
<style>
.stApp {
    background-color: #F4F7FC;
}

.block-container {
    padding-top: 0.7rem;
    padding-bottom: 0.3rem;
    padding-left: 1.3rem;
    padding-right: 1.3rem;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E5EAF2;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
}

.dashboard-header {
    background: linear-gradient(110deg, #172B4D, #2563EB);
    padding: 14px 20px;
    border-radius: 12px;
    margin-bottom: 8px;
}

.dashboard-header h1 {
    color: white;
    font-size: 25px;
    margin: 0;
    font-weight: 750;
}

.dashboard-header p {
    color: #DCE8FF;
    font-size: 11px;
    margin: 4px 0 0 0;
}

.kpi-card {
    background: white;
    border: 1px solid #E5EAF2;
    border-radius: 10px;
    padding: 12px 15px;
    min-height: 78px;
    box-shadow: 0 2px 6px rgba(15,35,70,0.035);
}

.kpi-label {
    color: #64748B;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 7px;
}

.kpi-value {
    color: #172B4D;
    font-size: 23px;
    font-weight: 750;
    line-height: 1.1;
}

.chart-heading {
    color: #172B4D;
    font-size: 13px;
    font-weight: 700;
    margin: 0 0 2px 3px;
}

.table-heading {
    color: #172B4D;
    font-size: 14px;
    font-weight: 750;
    margin: 4px 0;
}

.stButton button {
    border-radius: 7px;
    font-weight: 600;
}

[data-testid="stDataFrame"] {
    border: 1px solid #E5EAF2;
    border-radius: 8px;
}

[data-testid="stPlotlyChart"] {
    margin-bottom: -5px;
}

footer {
    visibility: hidden;
}
</style>
""")


# =====================================================
# REQUIRED COLUMNS
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


# =====================================================
# DATA CLEANING
# =====================================================

def clean_loan_data(data):

    data = data.copy()

    data = data.dropna(how="all")
    data = data.dropna(axis=1, how="all")

    data.columns = data.columns.astype(str).str.strip()

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

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

    data["Date"] = pd.to_datetime(
        data["Date"],
        dayfirst=True,
        errors="coerce"
    )

    data = data.dropna(
        subset=["Loan Amount", "Date"]
    )

    return data.reset_index(drop=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def format_crore(value):
    return f"₹{value / 10000000:.2f} Cr"


def create_kpi_card(label, value):

    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))

    st.html(f"""
    <div class="kpi-card">
        <div class="kpi-label">{safe_label}</div>
        <div class="kpi-value">{safe_value}</div>
    </div>
    """)


def chart_title(title):

    st.html(
        f'<div class="chart-heading">{html.escape(title)}</div>'
    )


def chart_style(fig, height=185):

    fig.update_layout(
        height=height,
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=9,
            color="#475569"
        ),
        legend=dict(
            font=dict(size=8),
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="center",
            x=0.5
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EDF1F7",
        zeroline=False,
        tickfont=dict(size=8)
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=8)
    )

    return fig


def show_chart(fig, height=185):

    st.plotly_chart(
        chart_style(fig, height),
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )


# =====================================================
# LANDING PAGE / EXCEL UPLOAD
# =====================================================

if "loan_df" not in st.session_state:

    # Use st.html() to render HTML directly.
    # Do not put this HTML inside st.markdown().

    st.html("""
    <div style="
        max-width:700px;
        margin:85px auto 30px auto;
        text-align:center;
    ">

        <div style="
            color:#2563EB;
            font-size:12px;
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
            font-weight:750;
        ">
            Loan Portfolio Analytics
        </h1>

        <p style="
            color:#64748B;
            font-size:16px;
            line-height:1.6;
        ">
            Upload your loan records to explore portfolio
            performance, application status and trends.
        </p>

    </div>

    <div style="
        max-width:650px;
        margin:0 auto;
        background:#FFFFFF;
        border:1px solid #E5EAF2;
        border-radius:14px;
        padding:25px;
        box-shadow:0 3px 12px rgba(15,35,70,0.04);
    ">

        <div style="
            color:#172B4D;
            font-size:16px;
            font-weight:700;
            margin-bottom:5px;
        ">
            Upload your loan data
        </div>

        <div style="
            color:#64748B;
            font-size:13px;
        ">
            Select your Excel workbook (.xlsx) to open the dashboard.
        </div>

    </div>
    """)

    uploaded_file = st.file_uploader(
        "Choose Excel File",
        type=["xlsx"],
        key="landing_upload"
    )

    if uploaded_file is not None:

        try:

            raw_df = pd.read_excel(uploaded_file)

            cleaned_df = clean_loan_data(raw_df)

            if cleaned_df.empty:

                st.error("No valid loan records found.")

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

df["Month Sort"] = df["Date"].dt.to_period("M")
df["Month Year"] = df["Month Sort"].astype(str)


# =====================================================
# SIDEBAR BRANDING
# =====================================================

st.sidebar.html("""
<div style="padding:5px 0 12px 0;">

    <div style="
        color:#2563EB;
        font-size:11px;
        font-weight:700;
        letter-spacing:2px;
    ">
        LOAN PORTFOLIO
    </div>

    <div style="
        color:#172B4D;
        font-size:21px;
        font-weight:800;
    ">
        Analytics Dashboard
    </div>

</div>
""")

st.sidebar.caption(
    f"File: {st.session_state.get('loan_filename', 'Uploaded file')}"
)

st.sidebar.divider()


# =====================================================
# SIDEBAR BUTTONS
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
st.sidebar.subheader("Filter Records")


# =====================================================
# FILTER OPTIONS
# =====================================================

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


# =====================================================
# ACTUAL STREAMLIT FILTER WIDGETS
# =====================================================

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
# DASHBOARD HEADER
# =====================================================

st.html("""
<div class="dashboard-header">

    <h1>Loan Portfolio Analytics</h1>

    <p>
        Portfolio overview, performance and application insights
    </p>

</div>
""")


# =====================================================
# EMPTY DATA CHECK
# =====================================================

if filtered_df.empty:

    st.warning(
        "No records found for the selected filters. "
        "Please adjust your filter selections."
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

pending_applications = len(
    filtered_df[
        filtered_df["Status"].str.lower() == "pending"
    ]
)


# =====================================================
# KPI CARDS
# =====================================================

k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    create_kpi_card(
        "TOTAL APPLICATIONS",
        f"{total_applications:,}"
    )

with k2:
    create_kpi_card(
        "TOTAL LOAN AMOUNT",
        format_crore(total_loan_amount)
    )

with k3:
    create_kpi_card(
        "DISBURSED AMOUNT",
        format_crore(disbursed_amount)
    )

with k4:
    create_kpi_card(
        "PENDING APPLICATIONS",
        f"{pending_applications:,}"
    )


# =====================================================
# CHART ROW 1
# =====================================================

c1, c2, c3 = st.columns(3, gap="small")


# 1. APPLICATION STATUS

with c1:

    with st.container(border=True):

        chart_title("Application Status")

        status_data = (
            filtered_df["Status"]
            .value_counts()
            .reset_index()
        )

        status_data.columns = [
            "Status",
            "Applications"
        ]

        fig_status = px.pie(
            status_data,
            names="Status",
            values="Applications",
            hole=0.55,
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig_status.update_traces(
            textposition="inside",
            textinfo="percent",
            textfont_size=9
        )

        show_chart(fig_status)


# 2. LOAN TYPE DISTRIBUTION

with c2:

    with st.container(border=True):

        chart_title("Loan Type Distribution")

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
            color="Loan Amount",
            color_continuous_scale="Blues"
        )

        fig_loan.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title=""
        )

        show_chart(fig_loan)


# 3. BANK PERFORMANCE

with c3:

    with st.container(border=True):

        chart_title("Bank Performance")

        bank_data = (
            filtered_df.groupby("Bank Name")["Loan Amount"]
            .sum()
            .reset_index()
            .sort_values("Loan Amount", ascending=True)
        )

        fig_bank = px.bar(
            bank_data,
            x="Loan Amount",
            y="Bank Name",
            orientation="h",
            color="Loan Amount",
            color_continuous_scale="Blues"
        )

        fig_bank.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title=""
        )

        show_chart(fig_bank)


# =====================================================
# CHART ROW 2
# =====================================================

c4, c5, c6 = st.columns(3, gap="small")


# 4. EXECUTIVE PERFORMANCE

with c4:

    with st.container(border=True):

        chart_title("Executive Performance")

        executive_data = (
            filtered_df.groupby("Executive Name")["Loan Amount"]
            .sum()
            .reset_index()
            .sort_values("Loan Amount", ascending=True)
        )

        fig_executive = px.bar(
            executive_data,
            x="Loan Amount",
            y="Executive Name",
            orientation="h",
            color="Loan Amount",
            color_continuous_scale="Tealgrn"
        )

        fig_executive.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title=""
        )

        show_chart(fig_executive)


# 5. MONTHLY LOAN TREND

with c5:

    with st.container(border=True):

        chart_title("Monthly Loan Trend")

        monthly_data = (
            filtered_df.groupby("Month Sort")
            .agg(
                Loan_Amount=("Loan Amount", "sum")
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
            markers=True
        )

        fig_monthly.update_traces(
            line=dict(width=2),
            marker=dict(size=5)
        )

        fig_monthly.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title=""
        )

        show_chart(fig_monthly)


# 6. TOP 10 CUSTOMERS

with c6:

    with st.container(border=True):

        chart_title("Top 10 Customers")

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
            color="Loan Amount",
            color_continuous_scale="Blues"
        )

        fig_customers.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title=""
        )

        show_chart(fig_customers)


# =====================================================
# LOAN RECORDS TABLE
# =====================================================

st.html("""
<div class="table-heading">
    Loan Records
</div>
""")

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

    display_df["Date"] = (
        display_df["Date"].dt.strftime("%d-%b-%Y")
    )

if "Loan Amount" in display_df.columns:

    display_df["Loan Amount"] = (
        display_df["Loan Amount"].apply(
            lambda x: f"₹{x:,.0f}"
        )
    )

st.dataframe(
    display_df,
    use_container_width=True,
    height=160,
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
    mime="text/csv"
)


# =====================================================
# FOOTER
# =====================================================

st.html("""
<div style="
    text-align:center;
    color:#94A3B8;
    font-size:11px;
    padding:5px;
">
    Loan Portfolio Analytics Dashboard
</div>
""")
