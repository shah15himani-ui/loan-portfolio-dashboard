
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import html

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="JR Financial | Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. THEME AND CSS
# =========================================================

st.markdown("""
<style>
.stApp {
    background: #0B1220;
    color: #E5EAF3;
}

.block-container {
    padding: 2rem 1.5rem 1rem 1.5rem;
    max-width: 100%;
}

header[data-testid="stHeader"] {
    background: #0B1220;
    height: 0;
    min-height: 0;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stAppDeployButton {
    display: none !important;
}

[data-testid="stSidebar"] {
    background: #111D32;
    border-right: 1px solid #24344E;
}

[data-testid="stSidebar"] * {
    color: #DCE5F3;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 7px;
    padding: 8px;
    margin-bottom: 3px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #223451;
}

.brand-box {
    padding: 12px 7px 22px;
    border-bottom: 1px solid #293A54;
    margin-bottom: 20px;
}

.brand-kicker {
    color: #6EA8FE;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
}

.brand-title {
    color: white;
    font-size: 22px;
    font-weight: 800;
    margin-top: 5px;
}

.brand-subtitle {
    color: #91A2BB;
    font-size: 10px;
    margin-top: 3px;
}

.page-title {
    color: #F1F5FB;
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 3px;
}

.page-subtitle {
    color: #8FA1BB;
    font-size: 12px;
    margin-bottom: 15px;
}

.section-label {
    color: #7F96B5;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin: 14px 0 9px 2px;
}

.kpi-card {
    background: #14233B;
    border: 1px solid #263B5A;
    border-radius: 10px;
    padding: 15px;
    min-height: 108px;
}

.kpi-label {
    color: #91A5C1;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .6px;
}

.kpi-value {
    color: #F4F7FC;
    font-size: 24px;
    font-weight: 800;
    margin-top: 9px;
}

.kpi-note {
    color: #55B6A4;
    font-size: 10px;
    margin-top: 5px;
}

.panel-title {
    color: #E7EDF7;
    font-size: 12px;
    font-weight: 750;
    padding: 5px 5px 0;
}

.panel-subtitle {
    color: #8295B1;
    font-size: 9px;
    padding: 2px 5px 0;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #14233B;
    border: 1px solid #263B5A;
    border-radius: 10px;
    padding: 5px;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stTextInput"] label {
    color: #A5B6CE;
    font-size: 11px;
    font-weight: 600;
}

div[data-baseweb="select"] > div {
    background: #14233B;
    border-color: #314766;
    color: #E5EAF3;
}

div[data-testid="stTextInput"] input,
div[data-testid="stDateInput"] input {
    background: #14233B;
    color: #E5EAF3;
    border-color: #314766;
}

.stButton button,
.stDownloadButton button {
    background: #2563EB;
    color: white;
    border: 1px solid #3B82F6;
    border-radius: 7px;
    font-size: 11px;
    font-weight: 700;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #1D4ED8;
    color: white;
}

[data-testid="stDataFrame"] {
    border: 1px solid #263B5A;
    border-radius: 9px;
}

[data-testid="stMetric"] {
    background: #14233B;
    border: 1px solid #263B5A;
    border-radius: 9px;
    padding: 13px;
}

[data-testid="stMetricLabel"] {
    color: #91A5C1;
}

[data-testid="stMetricValue"] {
    color: #F4F7FC;
}

hr {
    border-color: #263B5A;
}

.footer {
    color: #647B99;
    text-align: center;
    font-size: 10px;
    padding: 15px 0 5px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. CONSTANTS
# =========================================================

REQUIRED_COLUMNS = [
    "Customer Name",
    "Type of Loan",
    "Status",
    "Loan Amount",
    "Bank Name",
    "Executive Name",
    "Date"
]

NAVIGATION = [
    "Summary",
    "Loan Types",
    "Banks",
    "Executives",
    "Records",
    "KPI Metrics"
]

CHART_COLORS = [
    "#3B82F6",
    "#14B8A6",
    "#F59E0B",
    "#8B9BB4",
    "#A78BFA",
    "#E879A0",
    "#38BDF8"
]


# =========================================================
# 4. DATA CLEANING
# =========================================================

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

    data = data.dropna(subset=["Loan Amount", "Date"])

    return data.reset_index(drop=True)


# =========================================================
# 5. HELPER FUNCTIONS
# =========================================================

def safe_html(value):
    return html.escape(str(value))


def format_crore(value):
    return f"₹{value / 10000000:.2f} Cr"


def format_money(value):
    return f"₹{value:,.0f}"


def show_kpi(label, value, note):

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{safe_html(label)}</div>
        <div class="kpi-value">{safe_html(value)}</div>
        <div class="kpi-note">{safe_html(note)}</div>
    </div>
    """, unsafe_allow_html=True)


def panel_heading(title, subtitle=""):

    st.markdown(f"""
    <div class="panel-title">{safe_html(title)}</div>
    <div class="panel-subtitle">{safe_html(subtitle)}</div>
    """, unsafe_allow_html=True)


def style_chart(fig, height=260):

    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="#14233B",
        plot_bgcolor="#14233B",
        font=dict(
            family="Arial",
            size=10,
            color="#AFC0D7"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=9, color="#B8C8DC")
        ),
        hoverlabel=dict(
            bgcolor="#0B1220",
            bordercolor="#3B82F6",
            font_color="white"
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#263A56",
        zeroline=False,
        tickfont=dict(size=9, color="#91A5C1")
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=9, color="#B5C5D9")
    )

    return fig


def display_chart(fig, height=260):

    fig = style_chart(fig, height)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )


# =========================================================
# 6. UPLOAD SCREEN
# =========================================================

if "loan_df" not in st.session_state:

    st.markdown("""
    <div style="
        max-width:700px;
        margin:90px auto 25px;
        text-align:center;
    ">
        <div style="
            color:#60A5FA;
            font-size:12px;
            font-weight:800;
            letter-spacing:3px;
        ">
            JR FINANCIAL
        </div>

        <h1 style="
            color:#F1F5FB;
            font-size:36px;
            margin:14px 0;
        ">
            Loan Portfolio Analytics
        </h1>

        <p style="color:#91A5C1;font-size:15px;">
            Enterprise Banking Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):

        st.subheader("Upload Loan Portfolio")

        st.write(
            "Upload your Excel workbook to access the interactive dashboard."
        )

        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=["xlsx"]
        )

        if uploaded_file is not None:

            try:
                raw_data = pd.read_excel(uploaded_file)
                cleaned_data = clean_loan_data(raw_data)

                if cleaned_data.empty:
                    st.error("No valid loan records were found.")

                else:
                    st.session_state["loan_df"] = cleaned_data
                    st.session_state["loan_filename"] = uploaded_file.name
                    st.rerun()

            except Exception as e:
                st.error(f"Upload error: {e}")

    st.stop()


# =========================================================
# 7. LOAD DATA
# =========================================================

df = st.session_state["loan_df"].copy()

df["Month"] = df["Date"].dt.to_period("M")
df["Month Year"] = df["Month"].astype(str)


# =========================================================
# 8. SIDEBAR NAVIGATION
# =========================================================

st.sidebar.markdown("""
<div class="brand-box">
    <div class="brand-kicker">JR FINANCIAL</div>
    <div class="brand-title">Enterprise BI</div>
    <div class="brand-subtitle">LOAN PORTFOLIO MANAGEMENT</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    "<div style='color:#7188A7;font-size:10px;"
    "font-weight:800;letter-spacing:1.5px;"
    "margin-bottom:8px;'>WORKSPACE</div>",
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    NAVIGATION,
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.markdown(
    "<div style='color:#7188A7;font-size:10px;"
    "font-weight:800;letter-spacing:1px;'>DATA SOURCE</div>",
    unsafe_allow_html=True
)

st.sidebar.caption(
    st.session_state.get("loan_filename", "Excel workbook")
)

st.sidebar.caption(f"{len(df):,} records loaded")


# =========================================================
# 9. PAGE-WISE FILTER CONFIGURATION
# =========================================================

# Each page has its own filter list.
# Filter values are stored separately for each page.

PAGE_FILTERS = {
    "Summary": [
        "Date Range",
        "Bank",
        "Loan Type",
        "Status",
        "Executive"
    ],

    "Loan Types": [
        "Date Range",
        "Loan Type",
        "Status",
        "Bank"
    ],

    "Banks": [
        "Date Range",
        "Bank",
        "Loan Type",
        "Status"
    ],

    "Executives": [
        "Date Range",
        "Executive",
        "Loan Type",
        "Status"
    ],

    "Records": [
        "Date Range",
        "Customer",
        "Status",
        "Bank",
        "Loan Type",
        "Executive"
    ],

    "KPI Metrics": [
        "Date Range",
        "Bank",
        "Loan Type",
        "Executive"
    ]
}

FILTER_COLUMNS = {
    "Bank": "Bank Name",
    "Loan Type": "Type of Loan",
    "Status": "Status",
    "Executive": "Executive Name"
}


# =========================================================
# 10. PAGE-SPECIFIC FILTER RESET
# =========================================================

def reset_page_filters(selected_page):

    prefix = selected_page.replace(" ", "_").lower()

    keys = [
        f"{prefix}_date",
        f"{prefix}_bank",
        f"{prefix}_loan_type",
        f"{prefix}_status",
        f"{prefix}_executive",
        f"{prefix}_customer"
    ]

    for key in keys:
        st.session_state.pop(key, None)


# =========================================================
# 11. DYNAMIC FILTER DISPLAY
# =========================================================

def display_page_filters(data, selected_page):

    filters = PAGE_FILTERS[selected_page]

    prefix = selected_page.replace(" ", "_").lower()

    filtered_data = data.copy()

    st.markdown(
        '<div class="section-label">PAGE FILTERS</div>',
        unsafe_allow_html=True
    )

    # Filter widths adapt to the number of filters.
    columns = st.columns(
        [1] * len(filters) + [0.8],
        gap="small"
    )

    for i, filter_name in enumerate(filters):

        with columns[i]:

            if filter_name == "Date Range":

                date_key = f"{prefix}_date"

                selected_dates = st.date_input(
                    "Date Range",
                    value=(
                        data["Date"].min().date(),
                        data["Date"].max().date()
                    ),
                    key=date_key
                )

                if (
                    isinstance(selected_dates, (tuple, list))
                    and len(selected_dates) == 2
                ):

                    start_date, end_date = selected_dates

                    if start_date > end_date:
                        st.error("Invalid date range.")
                        st.stop()

                    filtered_data = filtered_data[
                        (filtered_data["Date"].dt.date >= start_date)
                        & (filtered_data["Date"].dt.date <= end_date)
                    ]

                else:
                    st.info("Select both dates.")
                    st.stop()

            elif filter_name in FILTER_COLUMNS:

                column_name = FILTER_COLUMNS[filter_name]

                key_name = filter_name.lower().replace(" ", "_")
                widget_key = f"{prefix}_{key_name}"

                options = sorted(
                    data[column_name].dropna().unique().tolist()
                )

                options = [f"All {filter_name}s"] + options

                selected_value = st.selectbox(
                    filter_name,
                    options,
                    key=widget_key
                )

                if selected_value != f"All {filter_name}s":

                    filtered_data = filtered_data[
                        filtered_data[column_name] == selected_value
                    ]

            elif filter_name == "Customer":

                search_value = st.text_input(
                    "Search Customer",
                    placeholder="Enter customer name",
                    key=f"{prefix}_customer"
                )

                if search_value.strip():

                    filtered_data = filtered_data[
                        filtered_data["Customer Name"].str.contains(
                            search_value.strip(),
                            case=False,
                            na=False
                        )
                    ]

    with columns[-1]:

        st.markdown(
            "<div style='height:25px'></div>",
            unsafe_allow_html=True
        )

        st.button(
            "Reset",
            key=f"{prefix}_reset",
            use_container_width=True,
            on_click=reset_page_filters,
            args=(selected_page,)
        )

    return filtered_data


# =========================================================
# 12. MAIN PAGE HEADER
# =========================================================

PAGE_TITLES = {
    "Summary": "Loan Portfolio Dashboard",
    "Loan Types": "Loan Type Analysis",
    "Banks": "Bank Performance Dashboard",
    "Executives": "Executive Performance",
    "Records": "Loan Application Records",
    "KPI Metrics": "Portfolio KPI Metrics"
}

PAGE_SUBTITLES = {
    "Summary": "Monitor applications, lending performance and portfolio health.",
    "Loan Types": "Analyse loan categories, volumes and portfolio distribution.",
    "Banks": "Compare bank-wise loan performance and application volumes.",
    "Executives": "Track executive performance and managed loan portfolios.",
    "Records": "Search, review and download individual loan applications.",
    "KPI Metrics": "Monitor key financial and operational performance indicators."
}

st.markdown(
    f'<div class="page-title">{safe_html(PAGE_TITLES[page])}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="page-subtitle">{safe_html(PAGE_SUBTITLES[page])}</div>',
    unsafe_allow_html=True
)


# =========================================================
# 13. DISPLAY FILTERS FOR CURRENT PAGE ONLY
# =========================================================

filtered = display_page_filters(df, page)

if filtered.empty:
    st.warning("No records found for the selected filters.")
    st.stop()


# =========================================================
# 14. CALCULATE METRICS
# =========================================================

total_apps = len(filtered)
total_amount = filtered["Loan Amount"].sum()

disbursed = filtered[
    filtered["Status"].str.lower() == "disbursed"
]

approved = filtered[
    filtered["Status"].str.lower() == "approved"
]

pending = filtered[
    filtered["Status"].str.lower() == "pending"
]

rejected = filtered[
    filtered["Status"].str.lower() == "rejected"
]

under_review = filtered[
    filtered["Status"].str.lower() == "under review"
]

disbursed_amount = disbursed["Loan Amount"].sum()

approval_rate = len(approved) / total_apps * 100

disbursement_rate = len(disbursed) / total_apps * 100

average_loan = filtered["Loan Amount"].mean()

unique_customers = filtered["Customer Name"].nunique()


# =========================================================
# 15. SUMMARY PAGE
# =========================================================

if page == "Summary":

    st.markdown(
        '<div class="section-label">PORTFOLIO OVERVIEW</div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4, gap="small")

    with k1:
        show_kpi(
            "TOTAL APPLICATIONS",
            f"{total_apps:,}",
            "Applications in selected period"
        )

    with k2:
        show_kpi(
            "TOTAL LOAN PORTFOLIO",
            format_crore(total_amount),
            "Total applied loan value"
        )

    with k3:
        show_kpi(
            "DISBURSED AMOUNT",
            format_crore(disbursed_amount),
            "Successfully disbursed"
        )

    with k4:
        show_kpi(
            "PENDING APPLICATIONS",
            f"{len(pending):,}",
            "Awaiting action"
        )

    st.markdown(
        '<div class="section-label">PORTFOLIO HEALTH</div>',
        unsafe_allow_html=True
    )

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.metric("Approved", f"{len(approved):,}")

    with s2:
        st.metric("Rejected", f"{len(rejected):,}")

    with s3:
        st.metric("Under Review", f"{len(under_review):,}")

    with s4:
        st.metric("Approval Rate", f"{approval_rate:.1f}%")

    st.markdown(
        '<div class="section-label">PORTFOLIO PERFORMANCE</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([1.4, 1], gap="small")

    with c1:

        with st.container(border=True):

            panel_heading(
                "Monthly Loan Portfolio Trend",
                "Monthly loan amount"
            )

            monthly = (
                filtered.groupby("Month")["Loan Amount"]
                .sum()
                .reset_index()
                .sort_values("Month")
            )

            monthly["Month"] = monthly["Month"].astype(str)

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=monthly["Month"],
                    y=monthly["Loan Amount"],
                    mode="lines+markers",
                    name="Loan Amount",
                    line=dict(color="#3B82F6", width=3),
                    marker=dict(size=6),
                    fill="tozeroy",
                    fillcolor="rgba(59,130,246,0.12)"
                )
            )

            display_chart(fig, 250)

    with c2:

        with st.container(border=True):

            panel_heading(
                "Application Status Distribution"
            )

            status_data = (
                filtered["Status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = ["Status", "Applications"]

            fig = px.pie(
                status_data,
                names="Status",
                values="Applications",
                hole=0.62,
                color_discrete_sequence=CHART_COLORS
            )

            fig.update_traces(textinfo="percent")

            display_chart(fig, 250)

    c3, c4 = st.columns(2, gap="small")

    with c3:

        with st.container(border=True):

            panel_heading("Loan Type Performance")

            loan_data = (
                filtered.groupby("Type of Loan")["Loan Amount"]
                .sum()
                .nlargest(7)
                .reset_index()
                .sort_values("Loan Amount")
            )

            fig = px.bar(
                loan_data,
                x="Loan Amount",
                y="Type of Loan",
                orientation="h",
                color_discrete_sequence=["#3B82F6"]
            )

            display_chart(fig, 235)

    with c4:

        with st.container(border=True):

            panel_heading("Bank Performance")

            bank_data = (
                filtered.groupby("Bank Name")["Loan Amount"]
                .sum()
                .nlargest(7)
                .reset_index()
                .sort_values("Loan Amount")
            )

            fig = px.bar(
                bank_data,
                x="Loan Amount",
                y="Bank Name",
                orientation="h",
                color_discrete_sequence=["#14B8A6"]
            )

            display_chart(fig, 235)

    c5, c6 = st.columns(2, gap="small")

    with c5:

        with st.container(border=True):

            panel_heading("Executive Performance")

            executive_data = (
                filtered.groupby("Executive Name")["Loan Amount"]
                .sum()
                .nlargest(7)
                .reset_index()
                .sort_values("Loan Amount")
            )

            fig = px.bar(
                executive_data,
                x="Loan Amount",
                y="Executive Name",
                orientation="h",
                color_discrete_sequence=["#F59E0B"]
            )

            display_chart(fig, 235)

    with c6:

        with st.container(border=True):

            panel_heading("Top Customers")

            customer_data = (
                filtered.groupby("Customer Name")["Loan Amount"]
                .sum()
                .nlargest(7)
                .reset_index()
                .sort_values("Loan Amount")
            )

            fig = px.bar(
                customer_data,
                x="Loan Amount",
                y="Customer Name",
                orientation="h",
                color_discrete_sequence=["#8B9BB4"]
            )

            display_chart(fig, 235)


# =========================================================
# 16. LOAN TYPES PAGE
# =========================================================

elif page == "Loan Types":

    st.markdown(
        '<div class="section-label">LOAN CATEGORY OVERVIEW</div>',
        unsafe_allow_html=True
    )

    loan_summary = (
        filtered.groupby("Type of Loan")
        .agg(
            Applications=("Customer Name", "count"),
            Total_Amount=("Loan Amount", "sum"),
            Average_Amount=("Loan Amount", "mean")
        )
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )

    a, b, c = st.columns(3)

    with a:
        show_kpi(
            "LOAN CATEGORIES",
            f"{loan_summary.shape[0]}",
            "Categories in current selection"
        )

    with b:
        show_kpi(
            "TOTAL APPLICATIONS",
            f"{total_apps:,}",
            "Applications in current selection"
        )

    with c:
        show_kpi(
            "TOTAL LOAN VALUE",
            format_crore(total_amount),
            "Combined loan value"
        )

    x1, x2 = st.columns(2)

    with x1:

        with st.container(border=True):

            panel_heading("Loan Amount by Category")

            fig = px.bar(
                loan_summary.sort_values("Total_Amount"),
                x="Total_Amount",
                y="Type of Loan",
                orientation="h",
                color_discrete_sequence=["#3B82F6"]
            )

            display_chart(fig, 330)

    with x2:

        with st.container(border=True):

            panel_heading("Applications by Loan Category")

            fig = px.pie(
                loan_summary,
                names="Type of Loan",
                values="Applications",
                hole=0.55,
                color_discrete_sequence=CHART_COLORS
            )

            display_chart(fig, 330)

    st.markdown("#### Loan Type Details")

    loan_display = loan_summary.copy()

    loan_display["Total_Amount"] = loan_display["Total_Amount"].apply(format_money)
    loan_display["Average_Amount"] = loan_display["Average_Amount"].apply(format_money)

    st.dataframe(
        loan_display,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 17. BANKS PAGE
# =========================================================

elif page == "Banks":

    st.markdown(
        '<div class="section-label">BANK PERFORMANCE OVERVIEW</div>',
        unsafe_allow_html=True
    )

    bank_summary = (
        filtered.groupby("Bank Name")
        .agg(
            Applications=("Customer Name", "count"),
            Total_Amount=("Loan Amount", "sum"),
            Average_Amount=("Loan Amount", "mean")
        )
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )

    a, b, c = st.columns(3)

    with a:
        show_kpi("BANKS", f"{len(bank_summary)}", "Banks in current selection")

    with b:
        show_kpi("APPLICATIONS", f"{total_apps:,}", "Applications")

    with c:
        show_kpi("LOAN PORTFOLIO", format_crore(total_amount), "Total value")

    x1, x2 = st.columns(2)

    with x1:

        with st.container(border=True):

            panel_heading("Bank-wise Loan Portfolio")

            fig = px.bar(
                bank_summary.sort_values("Total_Amount"),
                x="Total_Amount",
                y="Bank Name",
                orientation="h",
                color_discrete_sequence=["#3B82F6"]
            )

            display_chart(fig, 340)

    with x2:

        with st.container(border=True):

            panel_heading("Applications by Bank")

            fig = px.pie(
                bank_summary,
                names="Bank Name",
                values="Applications",
                hole=0.55,
                color_discrete_sequence=CHART_COLORS
            )

            display_chart(fig, 340)

    st.markdown("#### Bank Performance Details")

    bank_display = bank_summary.copy()

    bank_display["Total_Amount"] = bank_display["Total_Amount"].apply(format_money)
    bank_display["Average_Amount"] = bank_display["Average_Amount"].apply(format_money)

    st.dataframe(
        bank_display,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 18. EXECUTIVES PAGE
# =========================================================

elif page == "Executives":

    st.markdown(
        '<div class="section-label">EXECUTIVE PERFORMANCE OVERVIEW</div>',
        unsafe_allow_html=True
    )

    executive_summary = (
        filtered.groupby("Executive Name")
        .agg(
            Applications=("Customer Name", "count"),
            Total_Amount=("Loan Amount", "sum"),
            Average_Amount=("Loan Amount", "mean")
        )
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )

    a, b, c = st.columns(3)

    with a:
        show_kpi(
            "EXECUTIVES",
            f"{len(executive_summary)}",
            "Executives in current selection"
        )

    with b:
        show_kpi(
            "APPLICATIONS",
            f"{total_apps:,}",
            "Applications managed"
        )

    with c:
        show_kpi(
            "TOTAL LOAN VALUE",
            format_crore(total_amount),
            "Combined loan value"
        )

    x1, x2 = st.columns(2)

    with x1:

        with st.container(border=True):

            panel_heading("Executive Loan Portfolio")

            fig = px.bar(
                executive_summary.sort_values("Total_Amount"),
                x="Total_Amount",
                y="Executive Name",
                orientation="h",
                color_discrete_sequence=["#14B8A6"]
            )

            display_chart(fig, 340)

    with x2:

        with st.container(border=True):

            panel_heading("Applications Managed")

            fig = px.bar(
                executive_summary.sort_values("Applications"),
                x="Applications",
                y="Executive Name",
                orientation="h",
                color_discrete_sequence=["#F59E0B"]
            )

            display_chart(fig, 340)

    st.markdown("#### Executive Performance Details")

    executive_display = executive_summary.copy()

    executive_display["Total_Amount"] = executive_display["Total_Amount"].apply(format_money)
    executive_display["Average_Amount"] = executive_display["Average_Amount"].apply(format_money)

    st.dataframe(
        executive_display,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 19. RECORDS PAGE
# =========================================================

elif page == "Records":

    st.markdown(
        '<div class="section-label">LOAN APPLICATION DATABASE</div>',
        unsafe_allow_html=True
    )

    st.markdown("#### Detailed Loan Records")

    display_df = filtered.copy()

    display_df["Date"] = display_df["Date"].dt.strftime("%d-%b-%Y")

    st.caption(f"{len(display_df):,} records found")

    st.dataframe(
        display_df,
        use_container_width=True,
        height=480,
        hide_index=True
    )

    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Filtered Records",
        data=csv_data,
        file_name="JR_Financial_Loan_Records.csv",
        mime="text/csv"
    )


# =========================================================
# 20. KPI METRICS PAGE
# =========================================================

elif page == "KPI Metrics":

    st.markdown(
        '<div class="section-label">KEY PERFORMANCE INDICATORS</div>',
        unsafe_allow_html=True
    )

    a, b, c, d = st.columns(4)

    with a:
        show_kpi("TOTAL APPLICATIONS", f"{total_apps:,}", "Filtered applications")

    with b:
        show_kpi("APPROVAL RATE", f"{approval_rate:.1f}%", "Approved / total")

    with c:
        show_kpi("DISBURSEMENT RATE", f"{disbursement_rate:.1f}%", "Disbursed / total")

    with d:
        show_kpi("AVERAGE LOAN", format_money(average_loan), "Average loan amount")

    st.markdown(
        '<div class="section-label">APPLICATION STATUS METRICS</div>',
        unsafe_allow_html=True
    )

    status_metrics = pd.DataFrame({
        "Status": [
            "Approved",
            "Disbursed",
            "Pending",
            "Rejected",
            "Under Review"
        ],
        "Applications": [
            len(approved),
            len(disbursed),
            len(pending),
            len(rejected),
            len(under_review)
        ]
    })

    with st.container(border=True):

        panel_heading(
            "Application Status Comparison",
            "Number of applications by status"
        )

        fig = px.bar(
            status_metrics,
            x="Status",
            y="Applications",
            color="Status",
            color_discrete_sequence=CHART_COLORS
        )

        fig.update_layout(showlegend=False)

        display_chart(fig, 330)

    st.markdown(
        '<div class="section-label">FINANCIAL METRICS</div>',
        unsafe_allow_html=True
    )

    x1, x2, x3 = st.columns(3)

    with x1:
        st.metric("Total Loan Amount", format_crore(total_amount))

    with x2:
        st.metric("Disbursed Amount", format_crore(disbursed_amount))

    with x3:
        st.metric("Unique Customers", f"{unique_customers:,}")


# =========================================================
# 21. FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    JR FINANCIAL | ENTERPRISE LOAN PORTFOLIO ANALYTICS
</div>
""", unsafe_allow_html=True)
