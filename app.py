
import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# JR FINANCIAL - LOAN PORTFOLIO ANALYTICS
# DESIGN 1: CLEAN & MODERN
# ============================================================

st.set_page_config(
    page_title="JR Financial | Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 1. THEME
# ============================================================

NAVY = "#102A4C"
BLUE = "#2475F5"
ORANGE = "#F59A23"
GREEN = "#18A879"
PURPLE = "#8665E8"
RED = "#D95368"

TEXT = "#172B4D"
MUTED = "#718096"
BORDER = "#E7EDF5"
PAGE_BG = "#F5F8FC"

STATUS_COLORS = {
    "Disbursed": GREEN,
    "Approved": BLUE,
    "Under Review": PURPLE,
    "Pending": ORANGE,
    "Rejected": RED,
}


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background: {PAGE_BG};
        color: {TEXT};
    }}

    .block-container {{
        max-width: 100%;
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        padding-left: 1.8rem;
        padding-right: 1.8rem;
    }}

    [data-testid="stHeader"] {{
        background: {PAGE_BG};
        height: 2.8rem;
    }}

    [data-testid="stDecoration"] {{
        display: none;
    }}

    [data-testid="stSidebar"] {{
        background: {NAVY};
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background: {NAVY};
    }}

    [data-testid="stSidebar"] * {{
        color: #F7FAFF;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        padding: 8px 10px;
        border-radius: 9px;
        transition: background 0.2s ease;
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background: rgba(255,255,255,0.10);
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
        background: {BLUE};
    }}

    [data-testid="stSidebar"] [data-testid="stRadio"] label p {{
        color: white !important;
        font-weight: 600;
    }}

    [data-testid="stSidebar"] [data-testid="stFileUploader"] {{
        background: rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 8px;
    }}

    [data-testid="stSidebar"] [data-testid="stButton"] button {{
        color: white;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 9px;
    }}

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {{
        background: rgba(255,255,255,0.16);
        border-color: white;
    }}

    h1, h2, h3 {{
        color: {NAVY} !important;
        letter-spacing: -0.4px;
    }}

    h1 {{
        font-size: 2rem !important;
        font-weight: 750 !important;
    }}

    h2 {{
        font-size: 1.25rem !important;
        font-weight: 700 !important;
    }}

    h3 {{
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }}

    .jr-brand {{
        text-align: center;
        padding: 10px 5px 22px;
        border-bottom: 1px solid rgba(255,255,255,0.15);
        margin-bottom: 20px;
    }}

    .jr-logo {{
        font-size: 42px;
        font-weight: 850;
        letter-spacing: -5px;
        color: white;
        line-height: 1.1;
    }}

    .jr-logo span {{
        color: {ORANGE};
    }}

    .jr-brand-name {{
        color: white;
        font-size: 20px;
        font-weight: 750;
        margin-top: 5px;
    }}

    .jr-tagline {{
        color: #C6D5E8;
        font-size: 11px;
        margin-top: 3px;
    }}

    .page-subtitle {{
        color: {MUTED};
        font-size: 14px;
        margin-bottom: 18px;
    }}

    .eyebrow {{
        color: {BLUE};
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.7px;
        margin-bottom: 3px;
    }}

    .kpi-card {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 13px;
        padding: 16px;
        min-height: 120px;
        box-shadow: 0 2px 8px rgba(16,42,76,0.035);
    }}

    .kpi-top {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }}

    .kpi-icon {{
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 17px;
        font-weight: 800;
    }}

    .kpi-label {{
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
    }}

    .kpi-value {{
        color: {NAVY};
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}

    .kpi-foot {{
        color: #8995A6;
        font-size: 11px;
        margin-top: 5px;
    }}

    .panel-title {{
        color: {NAVY};
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 3px;
    }}

    .panel-caption {{
        color: {MUTED};
        font-size: 11px;
        margin-bottom: 8px;
    }}

    .insight-row {{
        display: flex;
        gap: 10px;
        align-items: flex-start;
        padding: 11px 0;
        border-bottom: 1px solid #EEF2F7;
        color: {TEXT};
        font-size: 13px;
    }}

    .insight-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {ORANGE};
        margin-top: 5px;
        flex-shrink: 0;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    [data-testid="stPlotlyChart"] {{
        background: white;
        border-radius: 10px;
    }}

    [data-testid="stDownloadButton"] button {{
        border-radius: 9px;
        border: 1px solid {BLUE};
        color: {BLUE};
        background: white;
        font-weight: 650;
    }}

    [data-testid="stDownloadButton"] button:hover {{
        color: white;
        background: {BLUE};
    }}

    div[data-testid="stMetric"] {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 12px 15px;
    }}

    @media (max-width: 900px) {{
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}

        .kpi-value {{
            font-size: 18px;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def money_inr(value):

    value = float(value or 0)

    if abs(value) >= 10000000:
        return f"₹{value / 10000000:,.2f} Cr"

    if abs(value) >= 100000:
        return f"₹{value / 100000:,.2f} L"

    return f"₹{value:,.0f}"


def safe(value):
    return html.escape(str(value))


def clean_loan_data(data):

    data = data.dropna(axis=1, how="all").copy()

    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    required_columns = [
        "Customer Name",
        "Type of Loan",
        "Status",
        "Loan Amount",
        "Bank Name",
        "Executive Name",
        "Date",
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    text_columns = [
        "Customer Name",
        "Type of Loan",
        "Status",
        "Bank Name",
        "Executive Name",
    ]

    for column in text_columns:

        data[column] = (
            data[column]
            .fillna("Not specified")
            .astype(str)
            .str.strip()
            .replace("", "Not specified")
        )

    amount = (
        data["Loan Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("Rs.", "", regex=False)
        .str.replace("Rs", "", regex=False)
        .str.strip()
    )

    data["Loan Amount"] = pd.to_numeric(
        amount,
        errors="coerce"
    )

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce",
        dayfirst=True
    )

    data = data.dropna(
        subset=["Date", "Loan Amount"]
    ).copy()

    data["Loan Amount"] = data["Loan Amount"].clip(lower=0)

    return data


def show_header(title, subtitle):

    st.markdown(
        f"""
        <div class="eyebrow">JR FINANCIAL</div>
        <h1>{safe(title)}</h1>
        <div class="page-subtitle">{safe(subtitle)}</div>
        """,
        unsafe_allow_html=True
    )


def show_panel_title(title, subtitle=""):

    st.markdown(
        f"""
        <div class="panel-title">{safe(title)}</div>
        <div class="panel-caption">{safe(subtitle)}</div>
        """,
        unsafe_allow_html=True
    )


def show_kpi(label, value, icon, color, background, note):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <div class="kpi-icon"
                     style="color:{color};background:{background};">
                    {icon}
                </div>
                <div class="kpi-label">{safe(label)}</div>
            </div>

            <div class="kpi-value">{safe(value)}</div>

            <div class="kpi-foot">{safe(note)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def add_kpis(data):

    total_apps = len(data)

    total_value = data["Loan Amount"].sum()

    disbursed = data[
        data["Status"].str.casefold() == "disbursed"
    ]

    approved = data[
        data["Status"].str.casefold() == "approved"
    ]

    disbursed_value = disbursed["Loan Amount"].sum()

    approval_rate = (
        (len(approved) + len(disbursed)) / total_apps * 100
        if total_apps else 0
    )

    columns = st.columns(4, gap="medium")

    kpis = [
        (
            "Total Applications",
            f"{total_apps:,}",
            "▤",
            BLUE,
            "#EAF2FF",
            "Applications in selected records"
        ),
        (
            "Loan Portfolio",
            money_inr(total_value),
            "₹",
            ORANGE,
            "#FFF3E2",
            "Total application loan value"
        ),
        (
            "Disbursed Amount",
            money_inr(disbursed_value),
            "✓",
            GREEN,
            "#E6F8F1",
            "Value of disbursed applications"
        ),
        (
            "Approval Rate",
            f"{approval_rate:.1f}%",
            "%",
            PURPLE,
            "#F0ECFF",
            "Approved + disbursed applications"
        ),
    ]

    for col, item in zip(columns, kpis):

        with col:
            show_kpi(*item)


def chart_layout(fig, height=320):

    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            color=TEXT,
            size=11
        ),
        margin=dict(
            l=12,
            r=12,
            t=15,
            b=12
        ),
        hoverlabel=dict(
            bgcolor=NAVY,
            bordercolor=NAVY,
            font=dict(color="white")
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EEF2F7",
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EEF2F7",
        zeroline=False
    )

    return fig


def status_data(data):

    return (
        data.groupby("Status", as_index=False)
        .agg(
            Applications=("Customer Name", "size"),
            Loan_Value=("Loan Amount", "sum")
        )
    )


def monthly_chart(data):

    monthly = (
        data.set_index("Date")
        .resample("MS")
        .agg(
            Applications=("Customer Name", "size"),
            Loan_Value=("Loan Amount", "sum")
        )
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["Date"],
            y=monthly["Loan_Value"],
            name="Loan Value",
            mode="lines+markers",
            line=dict(
                color=BLUE,
                width=3
            ),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(36,117,245,0.10)",
            hovertemplate=(
                "%{x|%b %Y}<br>"
                "Loan Value: ₹%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        hovermode="x unified",
        showlegend=False
    )

    fig.update_xaxes(
        showgrid=False,
        tickformat="%b %Y"
    )

    fig.update_yaxes(
        tickprefix="₹",
        tickformat="~s"
    )

    return chart_layout(fig, 330)


def status_chart(data):

    summary = status_data(data)

    fig = px.pie(
        summary,
        names="Status",
        values="Applications",
        hole=0.63,
        color="Status",
        color_discrete_map=STATUS_COLORS
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        marker=dict(
            line=dict(
                color="white",
                width=3
            )
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Applications: %{value}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        annotations=[
            dict(
                text=(
                    f"<b>{len(data):,}</b>"
                    "<br><span style='font-size:11px'>Applications</span>"
                ),
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(
                    size=20,
                    color=NAVY
                )
            )
        ],
        legend=dict(
            orientation="v",
            y=0.5,
            x=1
        )
    )

    return chart_layout(fig, 330)


def horizontal_bar(data, name_column, value_column, color=BLUE, height=320):

    ordered = data.sort_values(
        value_column,
        ascending=True
    )

    fig = px.bar(
        ordered,
        x=value_column,
        y=name_column,
        orientation="h",
        color_discrete_sequence=[color],
        text=ordered[value_column].map(money_inr)
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Loan Value: ₹%{x:,.0f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=height,
        showlegend=False,
        margin=dict(l=8, r=65, t=12, b=10)
    )

    fig.update_xaxes(
        showticklabels=False,
        title=None
    )

    fig.update_yaxes(
        showgrid=False,
        title=None,
        automargin=True
    )

    return chart_layout(fig, height)


def executive_summary(data):

    result = (
        data.groupby("Executive Name", as_index=False)
        .agg(
            Applications=("Customer Name", "size"),
            Loan_Value=("Loan Amount", "sum"),
            Disbursed=(
                "Status",
                lambda x: (x.str.casefold() == "disbursed").sum()
            )
        )
    )

    result["Disbursal Rate"] = (
        result["Disbursed"]
        / result["Applications"]
        * 100
    ).round(1)

    return result.sort_values(
        "Loan_Value",
        ascending=False
    )


def insights(data):

    result = []

    total = len(data)
    total_value = data["Loan Amount"].sum()

    if total == 0:
        return result

    types = (
        data.groupby("Type of Loan")["Loan Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(types):

        share = (
            types.iloc[0] / total_value * 100
            if total_value else 0
        )

        result.append(
            f"{types.index[0]} is the largest loan category, "
            f"representing {share:.1f}% of portfolio value."
        )

    pending = (
        data["Status"].str.casefold() == "pending"
    ).sum()

    review = (
        data["Status"].str.casefold() == "under review"
    ).sum()

    if pending + review:

        result.append(
            f"{pending + review:,} applications are pending "
            "or under review and may need follow-up."
        )

    banks = (
        data.groupby("Bank Name")["Loan Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(banks):

        result.append(
            f"{banks.index[0]} has the highest loan value "
            "among the selected bank records."
        )

    disbursed = (
        data["Status"].str.casefold() == "disbursed"
    ).sum()

    result.append(
        f"{disbursed / total * 100:.1f}% of selected "
        "applications are marked as disbursed."
    )

    return result


# ============================================================
# 4. SIDEBAR AND NAVIGATION
# ============================================================

PAGES = [
    "Summary",
    "Loan Types",
    "Banks",
    "Executives",
    "Records",
    "KPI Metrics"
]

with st.sidebar:

    st.markdown(
        """
        <div class="jr-brand">
            <div class="jr-logo">J<span>R</span></div>
            <div class="jr-brand-name">JR Financial</div>
            <div class="jr-tagline">Grow. Finance. Prosper.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        PAGES,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("**DATA SOURCE**")

    uploaded_file = st.file_uploader(
        "Upload Excel workbook",
        type=["xlsx", "xls"],
        key="jr_upload"
    )

    if uploaded_file is not None:

        st.session_state["jr_uploaded_file"] = (
            uploaded_file.getvalue()
        )

        st.session_state["jr_uploaded_name"] = (
            uploaded_file.name
        )

    if "jr_uploaded_file" in st.session_state:

        source_name = st.session_state.get(
            "jr_uploaded_name",
            "Uploaded workbook"
        )

        source_bytes = st.session_state["jr_uploaded_file"]

        st.caption(f"Loaded: {source_name}")

    else:

        source_path = Path(__file__).with_name(
            "loan_records.xlsx"
        )

        if source_path.exists():

            source_name = source_path.name
            source_bytes = None

            st.caption(f"Using local file: {source_name}")

        else:

            source_name = None
            source_bytes = None

            st.info("Upload an Excel workbook to begin.")

    if st.button(
        "↻ Upload another file",
        use_container_width=True
    ):

        st.session_state.pop("jr_uploaded_file", None)
        st.session_state.pop("jr_uploaded_name", None)
        st.rerun()


# ============================================================
# 5. LOAD DATA
# ============================================================

try:

    if source_bytes is not None:

        from io import BytesIO

        raw_data = pd.read_excel(
            BytesIO(source_bytes)
        )

    elif source_name is not None:

        raw_data = pd.read_excel(
            Path(__file__).with_name("loan_records.xlsx")
        )

    else:

        show_header(
            "Loan Portfolio Analytics",
            "Upload your loan records to explore portfolio performance."
        )

        st.info(
            "Upload an Excel workbook using the left sidebar."
        )

        st.stop()

    df = clean_loan_data(raw_data)

    if df.empty:

        st.error(
            "No valid loan records found. "
            "Please check your Date and Loan Amount columns."
        )

        st.stop()

except Exception as error:

    st.error(f"Unable to load the workbook: {error}")
    st.stop()


# ============================================================
# 6. PAGE-SPECIFIC FILTERS
# ============================================================

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
    "Executive": "Executive Name",
    "Customer": "Customer Name"

}


def reset_page_filters(prefix):

    for key in list(st.session_state.keys()):

        if key.startswith(prefix + "_filter_"):

            del st.session_state[key]


def apply_filters(data, selected_page):

    prefix = selected_page.lower().replace(" ", "_")

    filters = PAGE_FILTERS[selected_page]

    selected_values = {}

    with st.container(border=True):

        st.markdown(
            "**FILTER DATA**"
        )

        columns = st.columns(
            len(filters),
            gap="small"
        )

        for column, filter_name in zip(columns, filters):

            key = (
                f"{prefix}_filter_"
                f"{filter_name.lower().replace(' ', '_')}"
            )

            with column:

                if filter_name == "Date Range":

                    min_date = data["Date"].min().date()
                    max_date = data["Date"].max().date()

                    date_value = st.date_input(
                        "Date range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key=key
                    )

                    if (
                        isinstance(date_value, (tuple, list))
                        and len(date_value) == 2
                    ):

                        selected_values["start_date"] = date_value[0]
                        selected_values["end_date"] = date_value[1]

                    else:

                        selected_values["start_date"] = date_value
                        selected_values["end_date"] = date_value

                else:

                    column_name = FILTER_COLUMNS[filter_name]

                    options = sorted(
                        data[column_name]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )

                    selected_values[filter_name] = st.multiselect(
                        filter_name,
                        options,
                        default=options,
                        key=key,
                        placeholder=f"All {filter_name.lower()}s"
                    )

        reset_col = st.columns([1, 6])[0]

        with reset_col:

            st.button(
                "Reset filters",
                key=f"{prefix}_reset",
                on_click=reset_page_filters,
                args=(prefix,),
                use_container_width=True
            )

    result = data[
        data["Date"].dt.date.between(
            selected_values["start_date"],
            selected_values["end_date"]
        )
    ].copy()

    for filter_name, values in selected_values.items():

        if filter_name in FILTER_COLUMNS:

            result = result[
                result[FILTER_COLUMNS[filter_name]].isin(values)
            ]

    return result


# ============================================================
# 7. PAGE HEADERS
# ============================================================

PAGE_INFO = {

    "Summary": (
        "Loan Portfolio Analytics",
        "A clear view of applications, portfolio value and business performance."
    ),

    "Loan Types": (
        "Loan Type Analysis",
        "Compare application volumes and portfolio value across loan categories."
    ),

    "Banks": (
        "Bank Performance",
        "Review bank-wise application volumes and portfolio value."
    ),

    "Executives": (
        "Executive Performance",
        "Understand team contribution and disbursement performance."
    ),

    "Records": (
        "Loan Records",
        "Search, review and export loan application data."
    ),

    "KPI Metrics": (
        "Portfolio KPI Metrics",
        "Track approval, disbursement and portfolio indicators."
    )

}


title, subtitle = PAGE_INFO[page]

show_header(title, subtitle)

filtered = apply_filters(df, page)

if filtered.empty:

    st.warning(
        "No records match the selected filters. "
        "Please adjust your filters."
    )

    st.stop()


# ============================================================
# 8. COMMON CALCULATIONS
# ============================================================

total_apps = len(filtered)

total_value = filtered["Loan Amount"].sum()

disbursed_df = filtered[
    filtered["Status"].str.casefold() == "disbursed"
]

approved_df = filtered[
    filtered["Status"].str.casefold() == "approved"
]

pending_df = filtered[
    filtered["Status"].str.casefold() == "pending"
]

review_df = filtered[
    filtered["Status"].str.casefold() == "under review"
]

rejected_df = filtered[
    filtered["Status"].str.casefold() == "rejected"
]

disbursed_value = disbursed_df["Loan Amount"].sum()

approval_rate = (
    (len(approved_df) + len(disbursed_df))
    / total_apps * 100
)

disbursal_rate = (
    len(disbursed_df) / total_apps * 100
)


# ============================================================
# 9. SUMMARY PAGE
# ============================================================

if page == "Summary":

    add_kpis(filtered)

    st.markdown("")

    left, right = st.columns(
        [1.7, 1],
        gap="medium"
    )

    with left:

        with st.container(border=True):

            show_panel_title(
                "Portfolio Trend",
                "Monthly loan value across the selected date range"
            )

            st.plotly_chart(
                monthly_chart(filtered),
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                },
                key="summary_monthly"
            )

    with right:

        with st.container(border=True):

            show_panel_title(
                "Loan Status Distribution",
                "Share of applications by status"
            )

            st.plotly_chart(
                status_chart(filtered),
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                },
                key="summary_status"
            )

    left, right = st.columns(
        [1.2, 1],
        gap="medium"
    )

    with left:

        with st.container(border=True):

            show_panel_title(
                "Loan Types",
                "Portfolio value by loan category"
            )

            type_data = (
                filtered.groupby("Type of Loan", as_index=False)
                .agg(
                    Loan_Value=("Loan Amount", "sum"),
                    Applications=("Customer Name", "size")
                )
            )

            st.plotly_chart(
                horizontal_bar(
                    type_data,
                    "Type of Loan",
                    "Loan_Value",
                    BLUE,
                    300
                ),
                use_container_width=True,
                config={"displayModeBar": False},
                key="summary_types"
            )

    with right:

        with st.container(border=True):

            show_panel_title(
                "Top Executives",
                "Ranked by total loan value"
            )

            executive_data = executive_summary(filtered).head(6)

            for rank, row in enumerate(
                executive_data.itertuples(index=False),
                start=1
            ):

                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        justify-content:space-between;
                        padding:11px 2px;
                        border-bottom:1px solid #EEF2F7;
                    ">

                        <div style="
                            display:flex;
                            align-items:center;
                            gap:11px;
                        ">

                            <div style="
                                width:27px;
                                height:27px;
                                border-radius:50%;
                                background:#EAF2FF;
                                color:#2475F5;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                font-size:11px;
                                font-weight:800;
                            ">
                                {rank}
                            </div>

                            <span style="
                                font-size:13px;
                                font-weight:650;
                                color:#172B4D;
                            ">
                                {safe(row[0])}
                            </span>

                        </div>

                        <b style="
                            font-size:13px;
                            color:#102A4C;
                        ">
                            {money_inr(row[2])}
                        </b>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

    left, right = st.columns(
        [1, 1],
        gap="medium"
    )

    with left:

        with st.container(border=True):

            show_panel_title(
                "Bank Performance",
                "Top banks by loan portfolio value"
            )

            bank_data = (
                filtered.groupby("Bank Name", as_index=False)
                .agg(
                    Loan_Value=("Loan Amount", "sum"),
                    Applications=("Customer Name", "size")
                )
                .sort_values("Loan_Value", ascending=False)
                .head(8)
            )

            st.plotly_chart(
                horizontal_bar(
                    bank_data,
                    "Bank Name",
                    "Loan_Value",
                    ORANGE,
                    300
                ),
                use_container_width=True,
                config={"displayModeBar": False},
                key="summary_banks"
            )

    with right:

        with st.container(border=True):

            show_panel_title(
                "Key Insights",
                "Highlights from the selected records"
            )

            for insight in insights(filtered):

                st.markdown(
                    f"""
                    <div class="insight-row">
                        <span class="insight-dot"></span>
                        <span>{safe(insight)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# 10. LOAN TYPES PAGE
# ============================================================

elif page == "Loan Types":

    add_kpis(filtered)

    type_data = (
        filtered.groupby("Type of Loan", as_index=False)
        .agg(
            Applications=("Customer Name", "size"),
            Loan_Value=("Loan Amount", "sum"),
            Average_Loan=("Loan Amount", "mean")
        )
        .sort_values("Loan_Value", ascending=False)
    )

    left, right = st.columns(
        [1.3, 1],
        gap="medium"
    )

    with left:

        with st.container(border=True):

            show_panel_title(
                "Loan Value by Category",
                "Total portfolio value by loan type"
            )

            st.plotly_chart(
                horizontal_bar(
                    type_data,
                    "Type of Loan",
                    "Loan_Value",
                    BLUE,
                    350
                ),
                use_container_width=True,
                config={"displayModeBar": False},
                key="loan_type_value"
            )

    with right:

        with st.container(border=True):

            show_panel_title(
                "Application Mix",
                "Share of applications by loan type"
            )

            fig = px.pie(
                type_data,
                names="Type of Loan",
                values="Applications",
                hole=0.58,
                color_discrete_sequence=[
                    BLUE,
                    ORANGE,
                    GREEN,
                    PURPLE,
                    "#49A7C8",
                    "#D76D91",
                    "#8795A8"
                ]
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent"
            )

            st.plotly_chart(
                chart_layout(fig, 350),
                use_container_width=True,
                config={"displayModeBar": False},
                key="loan_type_mix"
            )

    with st.container(border=True):

        show_panel_title(
            "Loan Type Details",
            "Application count, portfolio value and average loan size"
        )

        table = type_data.rename(
            columns={
                "Type of Loan": "Loan Type",
                "Loan_Value": "Portfolio Value (₹)",
                "Average_Loan": "Average Loan (₹)"
            }
        )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Portfolio Value (₹)": st.column_config.NumberColumn(
                    format="₹%,.0f"
                ),
                "Average Loan (₹)": st.column_config.NumberColumn(
                    format="₹%,.0f"
                )
            }
        )


# ============================================================
# 11. BANKS PAGE
# ============================================================

elif page == "Banks":

    add_kpis(filtered)

    bank_data = (
        filtered.groupby("Bank Name", as_index=False)
        .agg(
            Applications=("Customer Name", "size"),
            Loan_Value=("Loan Amount", "sum"),
            Average_Loan=("Loan Amount", "mean")
        )
        .sort_values("Loan_Value", ascending=False)
    )

    left, right = st.columns(
        [1.4, 1],
        gap="medium"
    )

    with left:

        with st.container(border=True):

            show_panel_title(
                "Bank-wise Portfolio",
                "Total loan value by bank"
            )

            st.plotly_chart(
                horizontal_bar(
                    bank_data,
                    "Bank Name",
                    "Loan_Value",
                    BLUE,
                    370
                ),
                use_container_width=True,
                config={"displayModeBar": False},
                key="bank_portfolio"
            )

    with right:

        with st.container(border=True):

            show_panel_title(
                "Applications by Bank",
                "Share of selected applications"
            )

            fig = px.pie(
                bank_data,
                names="Bank Name",
                values="Applications",
                hole=0.58,
                color_discrete_sequence=[
                    BLUE,
                    ORANGE,
                    GREEN,
                    PURPLE,
                    "#49A7C8",
                    "#D76D91",
                    "#8795A8"
                ]
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent"
            )

            st.plotly_chart(
                chart_layout(fig, 370),
                use_container_width=True,
                config={"displayModeBar": False},
                key="bank_mix"
            )

    with st.container(border=True):

        show_panel_title(
            "Bank Performance Details",
            "Ranked by portfolio value"
        )

        bank_table = bank_data.rename(
            columns={
                "Bank Name": "Bank",
                "Loan_Value": "Portfolio Value (₹)",
                "Average_Loan": "Average Loan (₹)"
            }
        )

        st.dataframe(
            bank_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Portfolio Value (₹)": st.column_config.NumberColumn(
                    format="₹%,.0f"
                ),
                "Average Loan (₹)": st.column_config.NumberColumn(
                    format="₹%,.0f"
                )
            }
        )


# ============================================================
# 12. EXECUTIVES PAGE
# ============================================================

elif page == "Executives":

    add_kpis(filtered)

    executive_data = executive_summary(filtered)

    left, right = st.columns(
        [1.35, 1],
        gap="medium"
    )

    with left:

        with st.container(border=True):

            show_panel_title(
                "Executive Portfolio",
                "Total loan value handled by each executive"
            )

            st.plotly_chart(
                horizontal_bar(
                    executive_data,
                    "Executive Name",
                    "Loan_Value",
                    BLUE,
                    370
                ),
                use_container_width=True,
                config={"displayModeBar": False},
                key="executive_portfolio"
            )

    with right:

        with st.container(border=True):

            show_panel_title(
                "Application Contribution",
                "Number of applications handled"
            )

            contribution = executive_data.sort_values(
                "Applications",
                ascending=False
            )

            fig = px.bar(
                contribution,
                x="Executive Name",
                y="Applications",
                color_discrete_sequence=[ORANGE],
                text="Applications"
            )

            fig.update_traces(
                textposition="outside",
                cliponaxis=False
            )

            fig.update_layout(
                xaxis_tickangle=-35
            )

            st.plotly_chart(
                chart_layout(fig, 370),
                use_container_width=True,
                config={"displayModeBar": False},
                key="executive_contribution"
            )

    with st.container(border=True):

        show_panel_title(
            "Executive Performance Details",
            "Application and disbursement performance"
        )

        executive_table = executive_data.rename(
            columns={
                "Executive Name": "Executive",
                "Loan_Value": "Portfolio Value (₹)",
                "Disbursed": "Disbursed Applications"
            }
        )

        st.dataframe(
            executive_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Portfolio Value (₹)": st.column_config.NumberColumn(
                    format="₹%,.0f"
                ),
                "Disbursal Rate": st.column_config.NumberColumn(
                    format="%.1f%%"
                )
            }
        )


# ============================================================
# 13. RECORDS PAGE
# ============================================================

elif page == "Records":

    add_kpis(filtered)

    with st.container(border=True):

        show_panel_title(
            "Search Loan Records",
            "Search by customer, bank, loan type, status or executive"
        )

        search = st.text_input(
            "Search records",
            placeholder=(
                "Type a customer name, bank, loan category "
                "or executive..."
            ),
            label_visibility="collapsed"
        )

        detail = filtered.copy()

        if search.strip():

            searchable_columns = [
                "Customer Name",
                "Bank Name",
                "Type of Loan",
                "Executive Name",
                "Status"
            ]

            mask = detail[searchable_columns].apply(
                lambda column: column.astype(str).str.contains(
                    search.strip(),
                    case=False,
                    na=False
                )
            ).any(axis=1)

            detail = detail[mask]

        st.caption(
            f"Showing {len(detail):,} of {len(filtered):,} records"
        )

        display = detail.copy()

        display["Date"] = display["Date"].dt.strftime(
            "%d-%b-%Y"
        )

        if "Loan Amount" in display.columns:

            display["Loan Amount"] = (
                display["Loan Amount"].map(money_inr)
            )

        preferred_columns = [
            "Sr. No.",
            "Customer Name",
            "Type of Loan",
            "Status",
            "Loan Amount",
            "Bank Name",
            "Executive Name",
            "Date"
        ]

        columns = [
            column
            for column in preferred_columns
            if column in display.columns
        ]

        st.dataframe(
            display[columns],
            use_container_width=True,
            hide_index=True,
            height=470
        )

        csv_data = detail.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "Download filtered records (CSV)",
            data=csv_data,
            file_name="jr_financial_filtered_records.csv",
            mime="text/csv"
        )


# ============================================================
# 14. KPI METRICS PAGE
# ============================================================

elif page == "KPI Metrics":

    add_kpis(filtered)

    average_loan = filtered["Loan Amount"].mean()

    metric_columns = st.columns(4)

    extra_metrics = [
        ("Average Loan Size", money_inr(average_loan)),
        ("Disbursement Rate", f"{disbursal_rate:.1f}%"),
        ("Pending Applications", f"{len(pending_df):,}"),
        ("Under Review", f"{len(review_df):,}")
    ]

    for column, (label, value) in zip(
        metric_columns,
        extra_metrics
    ):

        with column:

            st.metric(
                label,
                value
            )

    left, right = st.columns(2)

    with left:

        with st.container(border=True):

            show_panel_title(
                "Status Breakdown",
                "Application count by status"
            )

            summary = status_data(filtered)

            fig = px.bar(
                summary,
                x="Status",
                y="Applications",
                color="Status",
                color_discrete_map=STATUS_COLORS,
                text="Applications"
            )

            fig.update_traces(
                textposition="outside",
                cliponaxis=False
            )

            st.plotly_chart(
                chart_layout(fig, 340),
                use_container_width=True,
                config={"displayModeBar": False},
                key="kpi_status"
            )

    with right:

        with st.container(border=True):

            show_panel_title(
                "Portfolio by Status",
                "Loan value associated with each status"
            )

            summary = status_data(filtered)

            fig = px.pie(
                summary,
                names="Status",
                values="Loan_Value",
                hole=0.58,
                color="Status",
                color_discrete_map=STATUS_COLORS
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent"
            )

            st.plotly_chart(
                chart_layout(fig, 340),
                use_container_width=True,
                config={"displayModeBar": False},
                key="kpi_portfolio"
            )

    with st.container(border=True):

        show_panel_title(
            "KPI Definitions",
            "How the dashboard calculates key metrics"
        )

        definitions = [
            (
                "Loan Portfolio",
                "Sum of Loan Amount across all filtered application records."
            ),
            (
                "Disbursed Amount",
                "Sum of Loan Amount where Status is Disbursed."
            ),
            (
                "Approval Rate",
                "Approved plus Disbursed applications divided by total applications."
            ),
            (
                "Disbursement Rate",
                "Disbursed applications divided by total applications."
            ),
            (
                "Average Loan Size",
                "Average Loan Amount across the filtered records."
            )
        ]

        for label, description in definitions:

            st.markdown(
                f"""
                <div class="insight-row">
                    <span class="insight-dot"></span>
                    <span>
                        <b>{safe(label)}:</b>
                        {safe(description)}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# 15. FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        border-top:1px solid #E7EDF5;
        margin-top:25px;
        padding-top:12px;
        display:flex;
        justify-content:space-between;
        gap:12px;
        flex-wrap:wrap;
    ">
        <span style="font-size:11px;color:#8793A4;">
            JR Financial · Loan Portfolio Analytics
        </span>

        <span style="font-size:11px;color:#8793A4;">
            Figures are based on the uploaded loan records and selected filters.
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
