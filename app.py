
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import re

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="JR Financial | Loan Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# THEME
# =========================================================

NAVY = "#14213D"
BLUE = "#2563EB"
LIGHT_BLUE = "#EFF6FF"
TEAL = "#0D9488"
PURPLE = "#7C3AED"
ORANGE = "#F59E0B"
RED = "#DC2626"
GREY = "#64748B"
LIGHT_BG = "#F5F7FB"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background: #14213D;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-size: 14px;
        padding: 5px 0;
    }

    .main-title {
        color: #14213D;
        font-size: 27px;
        font-weight: 800;
        margin-bottom: 3px;
    }

    .sub-title {
        color: #64748B;
        font-size: 13px;
        margin-bottom: 22px;
    }

    .kpi-card {
        background: white;
        border: 1px solid #E8EDF5;
        border-radius: 15px;
        padding: 19px;
        min-height: 125px;
        box-shadow: 0 3px 12px rgba(20,33,61,0.04);
    }

    .kpi-label {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .kpi-value {
        color: #14213D;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .kpi-note {
        color: #94A3B8;
        font-size: 11px;
    }

    .section-heading {
        color: #14213D;
        font-size: 17px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .upload-box {
        background: white;
        border: 1px solid #E8EDF5;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 18px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E8EDF5;
        padding: 15px;
        border-radius: 12px;
    }

    .stButton button {
        border-radius: 8px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #E8EDF5;
        border-radius: 10px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def find_column(df, aliases):
    normalized = {
        re.sub(r'[^a-z0-9]', '', str(col).lower()): col
        for col in df.columns
    }

    for alias in aliases:
        key = re.sub(r'[^a-z0-9]', '', alias.lower())
        if key in normalized:
            return normalized[key]

    for alias in aliases:
        key = re.sub(r'[^a-z0-9]', '', alias.lower())
        for normalized_col, original_col in normalized.items():
            if key and key in normalized_col:
                return original_col

    return None


def parse_amount(value):
    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    text = text.replace(",", "").replace("₹", "").replace("$", "")
    text = text.replace("INR", "").replace("Rs.", "").replace("Rs", "")
    text = text.strip()

    multiplier = 1

    if re.search(r'\b(crore|crores|cr)\b', text, re.I):
        multiplier = 10000000
    elif re.search(r'\b(lakh|lakhs|lac|lacs)\b', text, re.I):
        multiplier = 100000
    elif re.search(r'\b(k)\b', text, re.I):
        multiplier = 1000

    number = re.search(r'-?\d+\.?\d*', text)

    if not number:
        return 0.0

    return float(number.group()) * multiplier


def format_currency(value):
    value = float(value)

    if abs(value) >= 10000000:
        return f"₹{value / 10000000:,.2f} Cr"
    elif abs(value) >= 100000:
        return f"₹{value / 100000:,.2f} L"
    elif abs(value) >= 1000:
        return f"₹{value / 1000:,.1f} K"

    return f"₹{value:,.0f}"


def make_kpi(label, value, note):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_title(title):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )


def chart_layout(fig, height=350):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=35, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter", color=NAVY, size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )
    return fig


# =========================================================
# DATA PROCESSING
# =========================================================

def process_data(df):

    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    amount_col = find_column(df, [
        "Loan Amount", "Amount", "Sanction Amount",
        "Loan Value", "Disbursement Amount",
        "Finance Amount", "Portfolio Amount"
    ])

    status_col = find_column(df, [
        "Status", "Loan Status", "Application Status",
        "Current Status"
    ])

    loan_type_col = find_column(df, [
        "Loan Type", "Product Type", "Loan Category",
        "Product", "Category"
    ])

    bank_col = find_column(df, [
        "Bank", "Bank Name", "Lender",
        "Financial Institution"
    ])

    executive_col = find_column(df, [
        "Executive", "Sales Executive", "RM",
        "Relationship Manager", "Employee Name",
        "BDE", "Agent"
    ])

    date_col = find_column(df, [
        "Date", "Application Date", "Created Date",
        "Entry Date", "Loan Date", "Submission Date"
    ])

    customer_col = find_column(df, [
        "Customer", "Customer Name", "Applicant Name",
        "Client Name", "Name"
    ])

    if amount_col:
        df["_Amount"] = df[amount_col].apply(parse_amount)
    else:
        df["_Amount"] = 0.0

    if status_col:
        df["_Status"] = (
            df[status_col].fillna("Unknown").astype(str).str.strip()
        )
    else:
        df["_Status"] = "Unknown"

    if loan_type_col:
        df["_LoanType"] = (
            df[loan_type_col].fillna("Not specified").astype(str)
        )
    else:
        df["_LoanType"] = "Not specified"

    if bank_col:
        df["_Bank"] = (
            df[bank_col].fillna("Not specified").astype(str)
        )
    else:
        df["_Bank"] = "Not specified"

    if executive_col:
        df["_Executive"] = (
            df[executive_col].fillna("Not specified").astype(str)
        )
    else:
        df["_Executive"] = "Not specified"

    if customer_col:
        df["_Customer"] = (
            df[customer_col].fillna("Not specified").astype(str)
        )
    else:
        df["_Customer"] = "Not specified"

    if date_col:
        df["_Date"] = pd.to_datetime(
            df[date_col], errors="coerce", dayfirst=True
        )
    else:
        df["_Date"] = pd.NaT

    return df


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.markdown("""
<div style="padding:15px 5px 25px 5px;">
    <div style="font-size:24px;font-weight:800;">
        JR FINANCIAL
    </div>
    <div style="font-size:11px;color:#CBD5E1;">
        LOAN PORTFOLIO ANALYTICS
    </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Loan Types",
        "Banks",
        "Executives",
        "Records",
        "KPI Metrics",
        "Upload Data"
    ],
    label_visibility="visible"
)

st.sidebar.markdown("---")
st.sidebar.caption("JR Financial Analytics")


# =========================================================
# FILE UPLOAD
# =========================================================

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

if page == "Upload Data":

    st.markdown(
        '<div class="main-title">Upload Data</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-title">Import your loan portfolio Excel workbook.</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="upload-box">', unsafe_allow_html=True)

    st.markdown("### 📁 Upload Excel Workbook")
    st.write("Select an Excel file containing your loan portfolio data.")

    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=["xlsx", "xls"],
        key="loan_excel_upload"
    )

    if uploaded_file is not None:

        try:
            excel_file = pd.ExcelFile(uploaded_file)

            sheet_name = st.selectbox(
                "Select worksheet",
                excel_file.sheet_names
            )

            raw_df = pd.read_excel(
                uploaded_file,
                sheet_name=sheet_name
            )

            if raw_df.empty:
                st.warning("The selected worksheet is empty.")
            else:
                st.success(
                    f"File loaded successfully: {len(raw_df):,} rows "
                    f"and {len(raw_df.columns)} columns."
                )

                st.markdown("#### Data Preview")
                st.dataframe(
                    raw_df.head(10),
                    use_container_width=True,
                    hide_index=True
                )

                if st.button(
                    "Load Data into Dashboard",
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.uploaded_df = process_data(raw_df)
                    st.success("Your data is ready!")
                    st.rerun()

        except Exception as e:
            st.error(f"Unable to read the Excel file: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.uploaded_df is not None:
        st.info(
            f"Dashboard data is currently loaded with "
            f"{len(st.session_state.uploaded_df):,} records."
        )

    st.stop()


# =========================================================
# CHECK DATA
# =========================================================

if st.session_state.uploaded_df is None:

    st.markdown(
        '<div class="main-title">Welcome to JR Financial</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Loan Portfolio Analytics Dashboard</div>',
        unsafe_allow_html=True
    )

    st.info(
        "No data has been uploaded yet. Open **Upload Data** "
        "from the sidebar to import your Excel workbook."
    )

    if st.button("Go to Upload Data", type="primary"):
        st.session_state.uploaded_df = None
        st.rerun()

    st.stop()


# =========================================================
# LOAD DATA
# =========================================================

df = st.session_state.uploaded_df.copy()

# =========================================================
# DATE FILTER
# =========================================================

filtered_df = df.copy()

if df["_Date"].notna().any():

    valid_dates = df["_Date"].dropna()

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    st.markdown("### Date Range")

    selected_dates = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered_df = df[
            df["_Date"].notna()
            & (df["_Date"].dt.date >= start_date)
            & (df["_Date"].dt.date <= end_date)
        ]

else:
    st.caption("Date filter unavailable: no valid date column was detected.")


# =========================================================
# COMMON METRICS
# =========================================================

total_applications = len(filtered_df)
portfolio_value = filtered_df["_Amount"].sum()

normalized_status = (
    filtered_df["_Status"].astype(str).str.lower().str.strip()
)

disbursed_mask = normalized_status.str.contains(
    r"disburs|paid|completed", regex=True, na=False
)

pending_mask = normalized_status.str.contains(
    r"pending|under review|in progress|processing", regex=True, na=False
)

approved_mask = normalized_status.str.contains(
    r"approv|sanction", regex=True, na=False
)

rejected_mask = normalized_status.str.contains(
    r"reject|declin", regex=True, na=False
)

disbursed_count = int(disbursed_mask.sum())
pending_count = int(pending_mask.sum())
approved_count = int(approved_mask.sum())
rejected_count = int(rejected_mask.sum())

disbursed_value = filtered_df.loc[
    disbursed_mask, "_Amount"
].sum()

pending_value = filtered_df.loc[
    pending_mask, "_Amount"
].sum()

disbursed_percentage = (
    disbursed_count / total_applications * 100
    if total_applications else 0
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">Loan Portfolio Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Monitor applications, portfolio value and business performance.</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Showing {len(filtered_df):,} records out of {len(df):,} total records."
)


# =========================================================
# KPI CARDS
# =========================================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    make_kpi(
        "TOTAL APPLICATIONS",
        f"{total_applications:,}",
        "Applications in selected period"
    )

with k2:
    make_kpi(
        "PORTFOLIO VALUE",
        format_currency(portfolio_value),
        "Total loan amount"
    )

with k3:
    make_kpi(
        "DISBURSED",
        f"{disbursed_count:,}",
        format_currency(disbursed_value) + " disbursed value"
    )

with k4:
    make_kpi(
        "PENDING",
        f"{pending_count:,}",
        format_currency(pending_value) + " pending value"
    )


# =========================================================
# OVERVIEW
# =========================================================

if page == "Overview":

    left, right = st.columns([1.05, 1.4])

    with left:

        section_title("Application Status")

        if not filtered_df.empty:

            status_counts = (
                filtered_df["_Status"]
                .value_counts()
                .reset_index()
            )

            status_counts.columns = ["Status", "Applications"]

            status_colors = {
                "Disbursed": TEAL,
                "Pending": ORANGE,
                "Approved": BLUE,
                "Rejected": RED
            }

            colors = [
                status_colors.get(status, PURPLE)
                for status in status_counts["Status"]
            ]

            fig = go.Figure()

            fig.add_trace(go.Pie(
                labels=status_counts["Status"],
                values=status_counts["Applications"],
                hole=0.60,
                sort=False,
                marker=dict(colors=colors),
                textinfo="percent",
                textposition="inside",
                name="Applications",
                domain=dict(x=[0, 1], y=[0, 1])
            ))

            fig.update_layout(
                showlegend=True,
                annotations=[dict(
                    text=f"<b>{total_applications:,}</b><br><span style='font-size:11px'>Applications</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=20, color=NAVY)
                )]
            )

            st.plotly_chart(
                chart_layout(fig, 350),
                use_container_width=True
            )

        else:
            st.info("No data available.")

    with right:

        section_title("Portfolio by Status")

        if not filtered_df.empty:

            status_amount = (
                filtered_df.groupby("_Status")["_Amount"]
                .sum()
                .reset_index()
                .sort_values("_Amount", ascending=True)
            )

            fig = px.bar(
                status_amount,
                x="_Amount",
                y="_Status",
                orientation="h",
                text_auto=".2s",
                color="_Amount",
                color_continuous_scale=["#BFDBFE", BLUE]
            )

            fig.update_layout(
                coloraxis_showscale=False,
                xaxis_title="Loan Amount",
                yaxis_title=""
            )

            st.plotly_chart(
                chart_layout(fig, 350),
                use_container_width=True
            )

        else:
            st.info("No data available.")

    # MONTHLY TREND

    section_title("Monthly Portfolio Trend")

    monthly_data = filtered_df.dropna(subset=["_Date"]).copy()

    if not monthly_data.empty:

        monthly_data["Month"] = (
            monthly_data["_Date"].dt.to_period("M").astype(str)
        )

        monthly = (
            monthly_data.groupby("Month")
            .agg(
                Applications=("_Amount", "count"),
                Portfolio_Value=("_Amount", "sum")
            )
            .reset_index()
        )

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=monthly["Month"],
            y=monthly["Portfolio_Value"],
            mode="lines+markers",
            name="Portfolio Value",
            fill="tozeroy",
            line=dict(color=BLUE, width=3),
            fillcolor="rgba(37,99,235,0.10)"
        ))

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Portfolio Value",
            hovermode="x unified"
        )

        st.plotly_chart(
            chart_layout(fig, 330),
            use_container_width=True
        )

    else:
        st.info("Monthly trend requires a valid date column.")

    # TOP LOAN TYPES AND BANKS

    col1, col2 = st.columns(2)

    with col1:

        section_title("Top Loan Types")

        loan_data = (
            filtered_df.groupby("_LoanType")
            .size()
            .reset_index(name="Applications")
            .sort_values("Applications", ascending=False)
            .head(8)
        )

        fig = px.bar(
            loan_data,
            x="Applications",
            y="_LoanType",
            orientation="h",
            color_discrete_sequence=[PURPLE],
            text="Applications"
        )

        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            xaxis_title="Applications",
            yaxis_title=""
        )

        st.plotly_chart(
            chart_layout(fig, 330),
            use_container_width=True
        )

    with col2:

        section_title("Top Banks")

        bank_data = (
            filtered_df.groupby("_Bank")
            .size()
            .reset_index(name="Applications")
            .sort_values("Applications", ascending=False)
            .head(8)
        )

        fig = px.bar(
            bank_data,
            x="Applications",
            y="_Bank",
            orientation="h",
            color_discrete_sequence=[TEAL],
            text="Applications"
        )

        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            xaxis_title="Applications",
            yaxis_title=""
        )

        st.plotly_chart(
            chart_layout(fig, 330),
            use_container_width=True
        )


# =========================================================
# LOAN TYPES
# =========================================================

elif page == "Loan Types":

    section_title("Loan Type Analysis")

    loan_summary = (
        filtered_df.groupby("_LoanType")
        .agg(
            Applications=("_Amount", "count"),
            Portfolio_Value=("_Amount", "sum")
        )
        .reset_index()
        .sort_values("Portfolio_Value", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            loan_summary,
            x="_LoanType",
            y="Applications",
            color_discrete_sequence=[BLUE],
            text="Applications"
        )
        fig.update_layout(xaxis_title="Loan Type", yaxis_title="Applications")
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    with col2:
        fig = px.pie(
            loan_summary,
            names="_LoanType",
            values="Portfolio_Value",
            hole=0.55
        )
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    st.dataframe(
        loan_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# BANKS
# =========================================================

elif page == "Banks":

    section_title("Bank Performance")

    bank_summary = (
        filtered_df.groupby("_Bank")
        .agg(
            Applications=("_Amount", "count"),
            Portfolio_Value=("_Amount", "sum")
        )
        .reset_index()
        .sort_values("Portfolio_Value", ascending=False)
    )

    fig = px.bar(
        bank_summary.head(15),
        x="Portfolio_Value",
        y="_Bank",
        orientation="h",
        color="Portfolio_Value",
        color_continuous_scale=["#BFDBFE", BLUE],
        text_auto=".2s"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False
    )

    st.plotly_chart(
        chart_layout(fig, 450),
        use_container_width=True
    )

    st.dataframe(
        bank_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# EXECUTIVES
# =========================================================

elif page == "Executives":

    section_title("Executive Performance")

    executive_summary = (
        filtered_df.groupby("_Executive")
        .agg(
            Applications=("_Amount", "count"),
            Portfolio_Value=("_Amount", "sum")
        )
        .reset_index()
        .sort_values("Applications", ascending=False)
    )

    fig = px.bar(
        executive_summary.head(15),
        x="_Executive",
        y="Applications",
        color_discrete_sequence=[PURPLE],
        text="Applications"
    )

    fig.update_layout(
        xaxis_title="Executive",
        yaxis_title="Applications"
    )

    st.plotly_chart(
        chart_layout(fig, 400),
        use_container_width=True
    )

    st.dataframe(
        executive_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# RECORDS
# =========================================================

elif page == "Records":

    section_title("Loan Application Records")

    search = st.text_input(
        "Search records",
        placeholder="Search customer, bank, status or loan type..."
    )

    records = filtered_df.copy()

    if search:
        mask = records.astype(str).apply(
            lambda column: column.str.contains(
                search, case=False, na=False
            )
        ).any(axis=1)

        records = records[mask]

    st.caption(f"{len(records):,} matching records")

    display_df = records.drop(
        columns=["_Amount", "_Status", "_LoanType",
                 "_Bank", "_Executive", "_Customer", "_Date"],
        errors="ignore"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    csv = records.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Records as CSV",
        data=csv,
        file_name="jr_financial_loan_records.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# KPI METRICS
# =========================================================

elif page == "KPI Metrics":

    section_title("Portfolio KPI Metrics")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Disbursement Rate",
            f"{disbursed_percentage:.1f}%"
        )

    with metric2:
        st.metric(
            "Average Loan Amount",
            format_currency(
                filtered_df["_Amount"].mean()
                if total_applications else 0
            )
        )

    with metric3:
        st.metric(
            "Total Loan Amount",
            format_currency(portfolio_value)
        )

    status_kpis = pd.DataFrame({
        "Metric": [
            "Total Applications",
            "Disbursed",
            "Pending",
            "Approved",
            "Rejected"
        ],
        "Count": [
            total_applications,
            disbursed_count,
            pending_count,
            approved_count,
            rejected_count
        ]
    })

    st.dataframe(
        status_kpis,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        status_kpis,
        x="Metric",
        y="Count",
        color="Metric",
        text="Count"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        chart_layout(fig, 350),
        use_container_width=True
    )
