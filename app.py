
import re
import io
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="JR Financial | Loan Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# COLORS
# =========================================================

NAVY = "#14213D"
BLUE = "#315CF5"
BLUE_LIGHT = "#EAF0FF"
PURPLE = "#8057E8"
TEAL = "#25B98A"
ORANGE = "#F5A623"
RED = "#EF6464"
TEXT = "#17233F"
MUTED = "#78849A"
BG = "#F5F7FC"
BORDER = "#E9EDF5"
WHITE = "#FFFFFF"

# =========================================================
# SESSION STATE
# =========================================================

if "loan_data" not in st.session_state:
    st.session_state.loan_data = None

if "active_page" not in st.session_state:
    st.session_state.active_page = "Upload Data"

if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None


# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F5F7FC;
    color: #17233F;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 1600px;
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E9EDF5;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #78849A;
}

[data-testid="stSidebar"] .stRadio label {
    font-size: 14px;
    font-weight: 600;
    padding: 5px 0;
}

[data-testid="stSidebar"] .stRadio > div {
    gap: 8px;
}

.main-heading {
    color: #14213D;
    font-size: 27px;
    line-height: 1.2;
    font-weight: 800;
    margin-bottom: 5px;
}

.main-subheading {
    color: #78849A;
    font-size: 13px;
    margin-bottom: 20px;
}

.brand-name {
    font-size: 22px;
    font-weight: 800;
    color: #14213D;
    letter-spacing: -0.8px;
}

.brand-caption {
    font-size: 10px;
    color: #8792A8;
    letter-spacing: 2px;
    font-weight: 700;
}

.top-label {
    font-size: 10px;
    letter-spacing: 4px;
    color: #315CF5;
    font-weight: 800;
    text-align: center;
}

.hero-title {
    text-align: center;
    color: #14213D;
    font-size: clamp(32px, 4vw, 53px);
    line-height: 1.15;
    letter-spacing: -2px;
    font-weight: 800;
    margin-top: 12px;
    margin-bottom: 8px;
}

.hero-title span {
    color: #315CF5;
}

.hero-subtitle {
    text-align: center;
    color: #78849A;
    font-size: 16px;
    margin-bottom: 28px;
}

.upload-panel {
    background: #FFFFFF;
    border: 1px solid #E7ECF5;
    border-radius: 22px;
    padding: 30px;
    box-shadow: 0 12px 40px rgba(29, 53, 103, 0.07);
}

.upload-icon {
    width: 66px;
    height: 66px;
    border-radius: 19px;
    background: #EAF0FF;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 30px;
    margin: 0 auto 15px auto;
}

.upload-title {
    font-size: 21px;
    font-weight: 800;
    color: #14213D;
    text-align: center;
    margin-bottom: 7px;
}

.upload-description {
    font-size: 13px;
    color: #78849A;
    text-align: center;
    margin-bottom: 20px;
}

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E9EDF5;
    border-radius: 17px;
    padding: 19px 18px;
    min-height: 128px;
    box-shadow: 0 4px 15px rgba(20, 33, 61, 0.035);
}

.kpi-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.kpi-label {
    font-size: 11px;
    font-weight: 700;
    color: #78849A;
    letter-spacing: 0.4px;
}

.kpi-icon {
    height: 37px;
    width: 37px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
}

.kpi-value {
    color: #14213D;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -0.7px;
    margin-bottom: 5px;
}

.kpi-note {
    font-size: 10px;
    color: #8994A8;
}

.panel {
    background: #FFFFFF;
    border: 1px solid #E9EDF5;
    border-radius: 17px;
    padding: 19px;
    box-shadow: 0 4px 15px rgba(20, 33, 61, 0.035);
}

.panel-title {
    font-size: 15px;
    font-weight: 800;
    color: #14213D;
    margin-bottom: 3px;
}

.panel-subtitle {
    font-size: 11px;
    color: #8994A8;
    margin-bottom: 12px;
}

.small-tag {
    display: inline-block;
    background: #EAF0FF;
    color: #315CF5;
    font-size: 10px;
    font-weight: 700;
    padding: 5px 9px;
    border-radius: 20px;
}

.upload-feature {
    background: #F7F9FF;
    border: 1px solid #E8EDFA;
    padding: 15px;
    border-radius: 13px;
    min-height: 95px;
}

.upload-feature-title {
    font-size: 12px;
    color: #14213D;
    font-weight: 700;
    margin-bottom: 5px;
}

.upload-feature-text {
    font-size: 10px;
    color: #78849A;
    line-height: 1.5;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E9EDF5;
    border-radius: 13px;
    padding: 14px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #E9EDF5;
    border-radius: 12px;
}

.stButton button {
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}

.stDownloadButton button {
    border-radius: 9px;
    font-weight: 700;
}

hr {
    border-color: #E9EDF5;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def find_column(df, aliases):
    normalized = {
        re.sub(r"[^a-z0-9]", "", str(col).lower()): col
        for col in df.columns
    }

    for alias in aliases:
        key = re.sub(r"[^a-z0-9]", "", alias.lower())
        if key in normalized:
            return normalized[key]

    for alias in aliases:
        key = re.sub(r"[^a-z0-9]", "", alias.lower())
        for normalized_col, original_col in normalized.items():
            if key and key in normalized_col:
                return original_col

    return None


def parse_amount(value):
    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()
    value = value.replace(",", "").replace("₹", "").replace("$", "")
    value = value.replace("INR", "").replace("Rs.", "").replace("Rs", "")

    multiplier = 1

    if re.search(r"\b(crore|crores|cr)\b", value, re.I):
        multiplier = 10000000
    elif re.search(r"\b(lakh|lakhs|lac|lacs)\b", value, re.I):
        multiplier = 100000
    elif re.search(r"\bk\b", value, re.I):
        multiplier = 1000

    number = re.search(r"-?\d+\.?\d*", value)

    if not number:
        return 0.0

    return float(number.group()) * multiplier


def format_currency(value):
    value = float(value)

    if abs(value) >= 10000000:
        return f"₹{value / 10000000:,.2f} Cr"
    if abs(value) >= 100000:
        return f"₹{value / 100000:,.2f} L"
    if abs(value) >= 1000:
        return f"₹{value / 1000:,.1f} K"

    return f"₹{value:,.0f}"


def kpi_card(label, value, note, icon, icon_bg):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon" style="background:{icon_bg};">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def panel_heading(title, subtitle=""):
    st.markdown(f"""
    <div class="panel-title">{title}</div>
    <div class="panel-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


def apply_chart_style(fig, height=330):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter",
            color=NAVY,
            size=11
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )
    return fig


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

    df["_Amount"] = (
        df[amount_col].apply(parse_amount)
        if amount_col else 0.0
    )

    df["_Status"] = (
        df[status_col].fillna("Unknown").astype(str).str.strip()
        if status_col else "Unknown"
    )

    df["_LoanType"] = (
        df[loan_type_col].fillna("Not specified").astype(str)
        if loan_type_col else "Not specified"
    )

    df["_Bank"] = (
        df[bank_col].fillna("Not specified").astype(str)
        if bank_col else "Not specified"
    )

    df["_Executive"] = (
        df[executive_col].fillna("Not specified").astype(str)
        if executive_col else "Not specified"
    )

    df["_Customer"] = (
        df[customer_col].fillna("Not specified").astype(str)
        if customer_col else "Not specified"
    )

    df["_Date"] = (
        pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
        if date_col else pd.NaT
    )

    return df


def status_counts(data):
    status = data["_Status"].astype(str).str.lower().str.strip()

    disbursed = status.str.contains(
        r"disburs|paid|completed", regex=True, na=False
    )
    pending = status.str.contains(
        r"pending|under review|in progress|processing",
        regex=True, na=False
    )
    approved = status.str.contains(
        r"approv|sanction", regex=True, na=False
    )
    rejected = status.str.contains(
        r"reject|declin", regex=True, na=False
    )

    return disbursed, pending, approved, rejected


# =========================================================
# UPLOAD LANDING PAGE
# =========================================================


def upload_landing_page():

    st.markdown(
        '<div class="top-label">JR FINANCIAL</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-title">Loan Portfolio <span>Dashboard</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Upload your Excel workbook to get started.'
        '</div>',
        unsafe_allow_html=True
    )

    # Centered upload section
    _, center, _ = st.columns([1, 1.5, 1])

    with center:

        st.markdown('<div class="upload-panel">', unsafe_allow_html=True)

        st.markdown(
            '<div class="upload-icon">📁</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="upload-title">Upload Excel File</div>',
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Choose your Excel workbook",
            type=["xlsx", "xls"],
            key="landing_excel_upload",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:

            try:
                file_bytes = uploaded_file.getvalue()
                excel_file = pd.ExcelFile(io.BytesIO(file_bytes))

                sheet = st.selectbox(
                    "Select worksheet",
                    excel_file.sheet_names,
                    key="landing_sheet"
                )

                preview_df = pd.read_excel(
                    io.BytesIO(file_bytes),
                    sheet_name=sheet
                )

                st.success(
                    f"File uploaded successfully: {len(preview_df):,} rows"
                )

                with st.expander("Preview Excel data"):
                    st.dataframe(
                        preview_df.head(8),
                        use_container_width=True,
                        hide_index=True
                    )

                if st.button(
                    "Open Dashboard →",
                    type="primary",
                    use_container_width=True
                ):
                    if preview_df.empty:
                        st.error("The selected worksheet is empty.")
                    else:
                        st.session_state.loan_data = process_data(preview_df)
                        st.session_state.active_page = "Overview"
                        st.rerun()

            except Exception as error:
                st.error(f"Unable to read Excel file: {error}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="
        text-align:center;
        color:#A0A9B9;
        font-size:10px;
        margin-top:30px;
    ">
        JR FINANCIAL • LOAN PORTFOLIO ANALYTICS
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    st.sidebar.markdown("""
    <div style="padding:8px 5px 22px 5px;">
        <div style="font-size:22px;font-weight:800;color:#14213D;">
            JR Financial
        </div>
        <div style="
            color:#8792A8;
            font-size:9px;
            letter-spacing:2px;
            font-weight:700;
            margin-top:3px;
        ">
            LOAN ANALYTICS
        </div>
    </div>
    """, unsafe_allow_html=True)

    pages = [
        "Overview",
        "Loan Types",
        "Banks",
        "Executives",
        "Records",
        "KPI Metrics"
    ]

    selected = st.sidebar.radio(
        "WORKSPACE",
        pages,
        index=pages.index(st.session_state.active_page)
        if st.session_state.active_page in pages else 0,
        label_visibility="visible"
    )

    st.session_state.active_page = selected

    st.sidebar.markdown("---")

    if st.sidebar.button("＋ Upload New Data", use_container_width=True):
        st.session_state.active_page = "Upload Data"
        st.rerun()

    st.sidebar.markdown("---")

    st.sidebar.caption("JR Financial Analytics")
    st.sidebar.caption("Loan Portfolio Workspace")


# =========================================================
# GLOBAL DATE FILTER
# =========================================================

def get_filtered_data(df):

    result = df.copy()

    if df["_Date"].notna().any():

        valid_dates = df["_Date"].dropna()
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        st.markdown("")

        date_col, info_col = st.columns([1, 3])

        with date_col:
            selected = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="global_date_range"
            )

        if isinstance(selected, tuple) and len(selected) == 2:
            start, end = selected

            result = result[
                result["_Date"].notna()
                & (result["_Date"].dt.date >= start)
                & (result["_Date"].dt.date <= end)
            ]

        with info_col:
            st.markdown(
                f'<div style="padding-top:30px;color:#8994A8;font-size:11px;">'
                f'Showing {len(result):,} records in the selected period'
                f'</div>',
                unsafe_allow_html=True
            )

    else:
        st.caption(
            "Date filter unavailable because no date column was detected."
        )

    return result


# =========================================================
# DASHBOARD KPI SECTION
# =========================================================

def render_kpis(data):

    total = len(data)
    portfolio = data["_Amount"].sum()

    disbursed, pending, approved, rejected = status_counts(data)

    disbursed_count = int(disbursed.sum())
    pending_count = int(pending.sum())

    disbursed_value = data.loc[disbursed, "_Amount"].sum()

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        kpi_card(
            "TOTAL APPLICATIONS",
            f"{total:,}",
            "Applications in selected period",
            "▣",
            "#EAF0FF"
        )

    with c2:
        kpi_card(
            "PORTFOLIO VALUE",
            format_currency(portfolio),
            "Total recorded loan amount",
            "₹",
            "#E9F8F2"
        )

    with c3:
        kpi_card(
            "DISBURSED",
            f"{disbursed_count:,}",
            format_currency(disbursed_value) + " disbursed value",
            "✓",
            "#E5F8F0"
        )

    with c4:
        kpi_card(
            "PENDING",
            f"{pending_count:,}",
            "Applications awaiting completion",
            "◷",
            "#FFF5E5"
        )


# =========================================================
# OVERVIEW PAGE
# =========================================================

def overview_page(data):

    st.markdown(
        '<div class="main-heading">Dashboard Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subheading">'
        'Here is what is happening with your loan portfolio.'
        '</div>',
        unsafe_allow_html=True
    )

    data = get_filtered_data(data)

    render_kpis(data)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.35], gap="medium")

    # Status donut
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        panel_heading(
            "Application Status",
            "Distribution of applications by current status"
        )

        if not data.empty:

            counts = data["_Status"].value_counts().reset_index()
            counts.columns = ["Status", "Applications"]

            colors_map = {
                "disbursed": TEAL,
                "pending": ORANGE,
                "approved": BLUE,
                "rejected": RED
            }

            colors = [
                next(
                    (color for key, color in colors_map.items()
                     if key in str(status).lower()),
                    PURPLE
                )
                for status in counts["Status"]
            ]

            fig = go.Figure(go.Pie(
                labels=counts["Status"],
                values=counts["Applications"],
                hole=0.68,
                marker=dict(
                    colors=colors,
                    line=dict(color="white", width=4)
                ),
                textinfo="percent",
                textposition="inside",
                sort=False
            ))

            fig.update_layout(
                height=300,
                showlegend=True,
                margin=dict(l=5, r=5, t=10, b=5),
                paper_bgcolor="white",
                annotations=[dict(
                    text=f"<b>{len(data):,}</b><br><span style='font-size:10px'>Applications</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=20, color=NAVY)
                )]
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No records for this date range.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Portfolio by status
    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        panel_heading(
            "Portfolio by Status",
            "Loan amount grouped by application status"
        )

        if not data.empty:

            summary = (
                data.groupby("_Status")["_Amount"]
                .sum()
                .reset_index()
                .sort_values("_Amount", ascending=True)
            )

            fig = px.bar(
                summary,
                x="_Amount",
                y="_Status",
                orientation="h",
                text_auto=".2s",
                color="_Status",
                color_discrete_sequence=[
                    BLUE, TEAL, PURPLE, ORANGE, RED
                ]
            )

            fig.update_layout(
                height=300,
                margin=dict(l=5, r=5, t=10, b=5),
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=False,
                xaxis_title="Loan amount",
                yaxis_title=""
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No records for this date range.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Monthly trend
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    panel_heading(
        "Portfolio Activity",
        "Monthly loan application and portfolio value trend"
    )

    monthly_data = data.dropna(subset=["_Date"]).copy()

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

        fig.add_trace(go.Bar(
            x=monthly["Month"],
            y=monthly["Applications"],
            name="Applications",
            marker_color="#C9D7FF",
            yaxis="y"
        ))

        fig.add_trace(go.Scatter(
            x=monthly["Month"],
            y=monthly["Portfolio_Value"],
            name="Portfolio Value",
            mode="lines+markers",
            line=dict(color=BLUE, width=3),
            yaxis="y2"
        ))

        fig.update_layout(
            height=330,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Month",
            yaxis=dict(title="Applications"),
            yaxis2=dict(
                title="Portfolio Value",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(orientation="h", y=1.12)
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("A valid date column is required for monthly trends.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Loan types and banks
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        panel_heading("Loan Type Analysis", "Applications by loan category")

        loan_summary = (
            data.groupby("_LoanType")
            .size()
            .reset_index(name="Applications")
            .sort_values("Applications", ascending=False)
            .head(8)
        )

        fig = px.bar(
            loan_summary,
            x="Applications",
            y="_LoanType",
            orientation="h",
            text="Applications",
            color_discrete_sequence=[PURPLE]
        )

        fig.update_layout(
            height=310,
            yaxis=dict(autorange="reversed"),
            xaxis_title="Applications",
            yaxis_title="",
            margin=dict(l=5, r=5, t=10, b=5)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        panel_heading("Bank Performance", "Top banks by application volume")

        bank_summary = (
            data.groupby("_Bank")
            .size()
            .reset_index(name="Applications")
            .sort_values("Applications", ascending=False)
            .head(8)
        )

        fig = px.bar(
            bank_summary,
            x="Applications",
            y="_Bank",
            orientation="h",
            text="Applications",
            color_discrete_sequence=[TEAL]
        )

        fig.update_layout(
            height=310,
            yaxis=dict(autorange="reversed"),
            xaxis_title="Applications",
            yaxis_title="",
            margin=dict(l=5, r=5, t=10, b=5)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent records
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    panel_heading(
        "Recent Applications",
        "Latest available records from your workbook"
    )

    recent = data.sort_values(
        "_Date", ascending=False, na_position="last"
    ).head(8)

    display = recent.drop(
        columns=[
            "_Amount", "_Status", "_LoanType",
            "_Bank", "_Executive", "_Customer", "_Date"
        ],
        errors="ignore"
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# LOAN TYPES PAGE
# =========================================================

def loan_types_page(data):

    st.markdown(
        '<div class="main-heading">Loan Type Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subheading">Understand the distribution of your loan products.</div>',
        unsafe_allow_html=True
    )

    data = get_filtered_data(data)

    summary = (
        data.groupby("_LoanType")
        .agg(
            Applications=("_Amount", "count"),
            Portfolio_Value=("_Amount", "sum")
        )
        .reset_index()
        .sort_values("Applications", ascending=False)
    )

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            summary,
            x="_LoanType",
            y="Applications",
            color_discrete_sequence=[BLUE],
            text="Applications"
        )
        fig.update_layout(xaxis_title="Loan Type", yaxis_title="Applications")
        st.plotly_chart(apply_chart_style(fig), use_container_width=True)

    with c2:
        fig = px.pie(
            summary,
            names="_LoanType",
            values="Portfolio_Value",
            hole=0.58
        )
        st.plotly_chart(apply_chart_style(fig), use_container_width=True)

    st.markdown("### Loan Type Summary")
    st.dataframe(summary, use_container_width=True, hide_index=True)


# =========================================================
# BANKS PAGE
# =========================================================

def banks_page(data):

    st.markdown(
        '<div class="main-heading">Bank Performance</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subheading">Compare banks by application volume and portfolio value.</div>',
        unsafe_allow_html=True
    )

    data = get_filtered_data(data)

    summary = (
        data.groupby("_Bank")
        .agg(
            Applications=("_Amount", "count"),
            Portfolio_Value=("_Amount", "sum")
        )
        .reset_index()
        .sort_values("Portfolio_Value", ascending=False)
    )

    fig = px.bar(
        summary.head(15),
        x="Portfolio_Value",
        y="_Bank",
        orientation="h",
        color="Portfolio_Value",
        color_continuous_scale=["#C9D7FF", BLUE],
        text_auto=".2s"
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        xaxis_title="Portfolio Value",
        yaxis_title=""
    )

    st.plotly_chart(
        apply_chart_style(fig, 450),
        use_container_width=True
    )

    st.dataframe(summary, use_container_width=True, hide_index=True)


# =========================================================
# EXECUTIVES PAGE
# =========================================================

def executives_page(data):

    st.markdown(
        '<div class="main-heading">Executive Performance</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subheading">Review application performance across executives.</div>',
        unsafe_allow_html=True
    )

    data = get_filtered_data(data)

    summary = (
        data.groupby("_Executive")
        .agg(
            Applications=("_Amount", "count"),
            Portfolio_Value=("_Amount", "sum")
        )
        .reset_index()
        .sort_values("Applications", ascending=False)
    )

    fig = px.bar(
        summary.head(15),
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
        apply_chart_style(fig, 400),
        use_container_width=True
    )

    st.dataframe(summary, use_container_width=True, hide_index=True)


# =========================================================
# RECORDS PAGE
# =========================================================

def records_page(data):

    st.markdown(
        '<div class="main-heading">Loan Records</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subheading">Search, review and export loan application records.</div>',
        unsafe_allow_html=True
    )

    data = get_filtered_data(data)

    search = st.text_input(
        "Search records",
        placeholder="Search customer, bank, executive, status or loan type..."
    )

    records = data.copy()

    if search:
        mask = records.astype(str).apply(
            lambda col: col.str.contains(
                search, case=False, na=False
            )
        ).any(axis=1)

        records = records[mask]

    st.caption(f"{len(records):,} matching records")

    display = records.drop(
        columns=[
            "_Amount", "_Status", "_LoanType",
            "_Bank", "_Executive", "_Customer", "_Date"
        ],
        errors="ignore"
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    csv = records.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        data=csv,
        file_name="jr_financial_loan_records.csv",
        mime="text/csv"
    )


# =========================================================
# KPI PAGE
# =========================================================

def kpi_page(data):

    st.markdown(
        '<div class="main-heading">KPI Metrics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subheading">Key performance indicators for your portfolio.</div>',
        unsafe_allow_html=True
    )

    data = get_filtered_data(data)

    total = len(data)
    portfolio = data["_Amount"].sum()

    disbursed, pending, approved, rejected = status_counts(data)

    disbursed_count = int(disbursed.sum())
    pending_count = int(pending.sum())
    approved_count = int(approved.sum())
    rejected_count = int(rejected.sum())

    disbursement_rate = (
        disbursed_count / total * 100 if total else 0
    )

    average_amount = (
        data["_Amount"].mean() if total else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Disbursement Rate", f"{disbursement_rate:.1f}%")

    with c2:
        st.metric("Average Loan Amount", format_currency(average_amount))

    with c3:
        st.metric("Total Portfolio", format_currency(portfolio))

    summary = pd.DataFrame({
        "Metric": [
            "Total Applications",
            "Disbursed",
            "Pending",
            "Approved",
            "Rejected"
        ],
        "Count": [
            total,
            disbursed_count,
            pending_count,
            approved_count,
            rejected_count
        ]
    })

    st.markdown("### Application KPI Breakdown")

    fig = px.bar(
        summary,
        x="Metric",
        y="Count",
        color="Metric",
        text="Count"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        apply_chart_style(fig, 350),
        use_container_width=True
    )

    st.dataframe(summary, use_container_width=True, hide_index=True)


# =========================================================
# MAIN APP ROUTING
# =========================================================

# First visit: Upload Data is the landing page.
# No dashboard or sidebar is shown until data is loaded.

if (
    st.session_state.loan_data is None
    or st.session_state.active_page == "Upload Data"
):
    upload_landing_page()

else:

    render_sidebar()

    current_data = st.session_state.loan_data.copy()
    selected_page = st.session_state.active_page

    if selected_page == "Overview":
        overview_page(current_data)

    elif selected_page == "Loan Types":
        loan_types_page(current_data)

    elif selected_page == "Banks":
        banks_page(current_data)

    elif selected_page == "Executives":
        executives_page(current_data)

    elif selected_page == "Records":
        records_page(current_data)

    elif selected_page == "KPI Metrics":
        kpi_page(current_data)
