
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO
import html

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="JR Financial | Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. SESSION STATE
# =========================================================

DEFAULTS = {
    "dashboard_entered": False,
    "loan_data_bytes": None,
    "loan_sheet": None,
    "main_navigation": "Summary"
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# 3. THEME COLORS
# =========================================================

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
    "Under Review": ORANGE,
    "Pending": PURPLE,
    "Rejected": RED
}

# =========================================================
# 4. GLOBAL CSS
# =========================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {PAGE_BG};
    }}

    [data-testid="stHeader"] {{
        background: transparent;
        height: 3rem;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
        border-right: 1px solid #233F61;
    }}

    section[data-testid="stSidebar"] * {{
        color: white;
    }}

    section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
        padding: 9px 10px;
        border-radius: 8px;
    }}

    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background-color: #24466D;
    }}

    .brand {{
        font-size: 25px;
        font-weight: 800;
        letter-spacing: 1px;
        color: white;
        margin-bottom: 3px;
    }}

    .brand-sub {{
        font-size: 10px;
        letter-spacing: 2px;
        color: #B8C9DD;
        margin-bottom: 20px;
    }}

    .page-eyebrow {{
        color: {BLUE};
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 7px;
    }}

    .page-title {{
        color: {TEXT};
        font-size: 32px;
        line-height: 1.2;
        font-weight: 800;
        margin: 0 0 7px 0;
    }}

    .page-description {{
        color: {MUTED};
        font-size: 14px;
        margin-bottom: 24px;
    }}

    .kpi-card {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px 19px;
        min-height: 118px;
        box-shadow: 0 3px 12px rgba(16, 42, 76, 0.035);
    }}

    .kpi-label {{
        color: {MUTED};
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
    }}

    .kpi-value {{
        color: {TEXT};
        font-size: 25px;
        font-weight: 800;
        line-height: 1.2;
    }}

    .kpi-note {{
        color: {MUTED};
        font-size: 11px;
        margin-top: 8px;
    }}

    .panel-title {{
        color: {TEXT};
        font-size: 17px;
        font-weight: 800;
        margin: 4px 0 12px 0;
    }}

    .filter-panel {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0 20px 0;
    }}

    div[data-testid="stPlotlyChart"] {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 8px;
    }}

    div[data-testid="stDataFrame"] {{
        background: #FFFFFF;
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}

    .upload-card {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(16, 42, 76, 0.04);
    }}

    .footer {{
        color: #94A3B8;
        font-size: 11px;
        text-align: center;
        padding: 25px 0 5px 0;
    }}

    button[kind="primary"] {{
        background-color: {BLUE};
        border-color: {BLUE};
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 5. HELPER FUNCTIONS
# =========================================================

def safe(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def money_inr(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        value = 0

    if value >= 10000000:
        return f"₹{value / 10000000:.2f} Cr"

    if value >= 100000:
        return f"₹{value / 100000:.2f} L"

    return f"₹{value:,.0f}"


def clean_loan_data(data):

    df = data.copy()

    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")

    df.columns = [str(col).strip() for col in df.columns]

    df = df.loc[
        :,
        ~df.columns.str.contains(
            r"^Unnamed",
            case=False,
            na=False
        )
    ]

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    amount_col = find_column(
        df,
        ["loan amount", "amount", "loan value"]
    )

    date_col = find_column(
        df,
        ["date", "application date", "disbursement date"]
    )

    status_col = find_column(df, ["status"])

    if amount_col:

        df[amount_col] = (
            df[amount_col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.strip()
        )

        df[amount_col] = pd.to_numeric(
            df[amount_col],
            errors="coerce"
        ).fillna(0)

    if date_col:
        df[date_col] = pd.to_datetime(
            df[date_col],
            errors="coerce",
            dayfirst=True
        )

    if status_col:
        df[status_col] = (
            df[status_col]
            .astype(str)
            .str.strip()
            .str.title()
        )

    return df


def find_column(df, possible_names):

    for col in df.columns:

        normalized = (
            col.lower()
            .strip()
            .replace("_", " ")
        )

        if normalized in possible_names:
            return col

    return None


def get_loan_columns(df):

    return {
        "amount": find_column(
            df,
            ["loan amount", "amount", "loan value"]
        ),
        "status": find_column(
            df,
            ["status"]
        ),
        "type": find_column(
            df,
            ["type of loan", "loan type", "loan category"]
        ),
        "bank": find_column(
            df,
            ["bank name", "bank"]
        ),
        "executive": find_column(
            df,
            ["executive name", "executive", "sales executive"]
        ),
        "date": find_column(
            df,
            ["date", "application date", "disbursement date"]
        ),
        "customer": find_column(
            df,
            ["customer name", "applicant name", "name"]
        )
    }


def show_header(title, description, eyebrow="JR FINANCIAL"):

    st.markdown(
        f"""
        <div class="page-eyebrow">
            {html.escape(eyebrow)}
        </div>

        <div class="page-title">
            {html.escape(title)}
        </div>

        <div class="page-description">
            {html.escape(description)}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_panel_title(title):

    st.markdown(
        f'<div class="panel-title">{html.escape(title)}</div>',
        unsafe_allow_html=True
    )


def show_kpi(label, value, note=""):

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                {html.escape(str(label))}
            </div>

            <div class="kpi-value">
                {html.escape(str(value))}
            </div>

            <div class="kpi-note">
                {html.escape(str(note))}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def chart_layout(fig, height=340):

    fig.update_layout(
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            color=TEXT,
            size=12
        ),
        margin=dict(
            l=20,
            r=30,
            t=40,
            b=25
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_color=TEXT
        )
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
        zeroline=False
    )

    fig.update_yaxes(
        gridcolor="#EDF1F6",
        zeroline=False
    )

    return fig


# =========================================================
# 6. DATA LOADING
# =========================================================

def get_data():

    uploaded_bytes = st.session_state.get("loan_data_bytes")

    if not uploaded_bytes:
        return None

    try:

        sheet = st.session_state.get("loan_sheet")

        df = pd.read_excel(
            BytesIO(uploaded_bytes),
            sheet_name=sheet
        )

        return clean_loan_data(df)

    except Exception as error:

        st.error(f"Unable to load workbook: {error}")
        return None


# =========================================================
# 7. LANDING PAGE - UPLOAD FILE
# =========================================================

if not st.session_state["dashboard_entered"]:

    # Centered landing page
    st.markdown(
        """
        <div style="
            max-width:850px;
            margin:55px auto 15px auto;
            text-align:center;
        ">

            <div style="
                color:#2475F5;
                font-size:13px;
                font-weight:800;
                letter-spacing:3px;
            ">
                JR FINANCIAL
            </div>

            <h1 style="
                color:#102A4C;
                font-size:38px;
                font-weight:800;
                margin:12px 0;
            ">
                Loan Portfolio Analytics
            </h1>

            <p style="
                color:#718096;
                font-size:15px;
                margin-bottom:30px;
            ">
                Turn your loan records into meaningful insights.
                Upload your Excel workbook to get started.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    _, center, _ = st.columns([1, 2, 1])

    with center:

        st.markdown(
            """
            <div class="upload-card">

                <div style="
                    font-size:35px;
                    text-align:center;
                    margin-bottom:10px;
                ">
                    📊
                </div>

                <h3 style="
                    color:#102A4C;
                    text-align:center;
                    margin-bottom:5px;
                ">
                    Upload your Excel file
                </h3>

                <p style="
                    color:#718096;
                    font-size:13px;
                    text-align:center;
                ">
                    Select your loan portfolio workbook
                    to access your dashboard.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Choose Excel workbook",
            type=["xlsx", "xls"],
            key="landing_uploader"
        )

        if uploaded_file is not None:

            file_bytes = uploaded_file.getvalue()

            try:

                excel = pd.ExcelFile(
                    BytesIO(file_bytes)
                )

                selected_sheet = st.selectbox(
                    "Select worksheet",
                    excel.sheet_names,
                    key="landing_sheet"
                )

                preview = pd.read_excel(
                    BytesIO(file_bytes),
                    sheet_name=selected_sheet
                )

                st.success(
                    f"File selected: {uploaded_file.name}"
                )

                st.caption(
                    f"{len(preview):,} rows · "
                    f"{len(preview.columns):,} columns"
                )

                show_panel_title("Data Preview")

                st.dataframe(
                    preview.head(5),
                    use_container_width=True,
                    hide_index=True
                )

                st.write("")

                if st.button(
                    "Enter Dashboard →",
                    type="primary",
                    use_container_width=True
                ):

                    st.session_state["loan_data_bytes"] = file_bytes
                    st.session_state["loan_sheet"] = selected_sheet
                    st.session_state["dashboard_entered"] = True

                    st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to read this Excel file: {error}"
                )

        st.markdown(
            """
            <div class="footer">
                JR Financial · Loan Portfolio Analytics
            </div>
            """,
            unsafe_allow_html=True
        )

    st.stop()


# =========================================================
# 8. LOAD DASHBOARD DATA
# =========================================================

df = get_data()

if df is None or df.empty:

    st.error(
        "The uploaded workbook could not be loaded or contains no data."
    )

    if st.button("Return to Upload Page"):

        st.session_state["dashboard_entered"] = False
        st.session_state["loan_data_bytes"] = None
        st.session_state["loan_sheet"] = None

        st.rerun()

    st.stop()


columns = get_loan_columns(df)

amount_col = columns["amount"]
status_col = columns["status"]
type_col = columns["type"]
bank_col = columns["bank"]
executive_col = columns["executive"]
date_col = columns["date"]
customer_col = columns["customer"]


# =========================================================
# 9. SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">JR FINANCIAL</div>
        <div class="brand-sub">LOAN PORTFOLIO ANALYTICS</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Summary",
            "Loan Types",
            "Banks",
            "Executives",
            "Records",
            "KPI Metrics"
        ],
        key="main_navigation"
    )

    st.markdown("---")

    st.caption(
        f"Loaded: {len(df):,} records"
    )

    if st.button(
        "Upload Another File",
        use_container_width=True
    ):

        st.session_state["dashboard_entered"] = False
        st.session_state["loan_data_bytes"] = None
        st.session_state["loan_sheet"] = None

        st.rerun()

    st.markdown("---")

    st.caption("JR Financial | Analytics")


# =========================================================
# 10. PAGE FILTER FUNCTION
# =========================================================

def apply_page_filters(
    original_df,
    page_name,
    filter_fields,
    columns
):

    filtered = original_df.copy()

    if not filter_fields:
        return filtered

    st.markdown(
        '<div class="filter-panel">',
        unsafe_allow_html=True
    )

    show_panel_title("Filter Data")

    # Dropdowns are separated into three columns per row.
    for start in range(0, len(filter_fields), 3):

        current_fields = filter_fields[start:start + 3]

        filter_cols = st.columns(
            3,
            gap="large"
        )

        for index, field_key in enumerate(current_fields):

            col_name = columns.get(field_key)

            if not col_name or col_name not in filtered.columns:
                continue

            with filter_cols[index]:

                options = sorted(
                    filtered[col_name]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                selected = st.multiselect(
                    field_key.replace("_", " ").title(),
                    options=options,
                    default=options,
                    key=f"{page_name}_{field_key}_dropdown"
                )

                if selected:

                    filtered = filtered[
                        filtered[col_name]
                        .astype(str)
                        .isin(selected)
                    ]

                else:

                    filtered = filtered.iloc[0:0]

    # Date range control
    if "date" in filter_fields and columns.get("date"):

        date_col_filter = columns["date"]

        valid_dates = filtered[date_col_filter].dropna()

        if not valid_dates.empty:

            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key=f"{page_name}_date_range"
            )

            if isinstance(date_range, tuple) and len(date_range) == 2:

                start_date, end_date = date_range

                filtered = filtered[
                    filtered[date_col_filter].dt.date.between(
                        start_date,
                        end_date
                    )
                ]

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    return filtered


# =========================================================
# 11. KPI FUNCTION
# =========================================================

def add_kpis(data, columns):

    amount = columns["amount"]
    status = columns["status"]

    total_records = len(data)

    total_amount = (
        data[amount].sum()
        if amount else 0
    )

    disbursed_count = 0
    pending_count = 0

    if status:

        status_values = data[status].astype(str).str.lower()

        disbursed_count = int(
            (status_values == "disbursed").sum()
        )

        pending_count = int(
            (status_values == "pending").sum()
        )

    kpi_cols = st.columns(
        4,
        gap="medium"
    )

    with kpi_cols[0]:

        show_kpi(
            "Total Applications",
            f"{total_records:,}",
            "Applications in selected data"
        )

    with kpi_cols[1]:

        show_kpi(
            "Total Loan Amount",
            money_inr(total_amount),
            "Total portfolio value"
        )

    with kpi_cols[2]:

        show_kpi(
            "Disbursed Applications",
            f"{disbursed_count:,}",
            "Successfully disbursed"
        )

    with kpi_cols[3]:

        show_kpi(
            "Pending Applications",
            f"{pending_count:,}",
            "Awaiting decision"
        )


# =========================================================
# 12. CHART FUNCTIONS
# =========================================================

def status_chart(data, status_column):

    status_df = (
        data[status_column]
        .fillna("Not Available")
        .astype(str)
        .value_counts()
        .reset_index()
    )

    status_df.columns = [
        "Status",
        "Applications"
    ]

    fig = px.pie(
        status_df,
        names="Status",
        values="Applications",
        hole=0.62,
        color="Status",
        color_discrete_map=STATUS_COLORS
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "%{label}<br>"
            "Applications: %{value}"
            "<extra></extra>"
        )
    )

    return chart_layout(fig, 360)


def loan_type_chart(data, type_column, amount_column):

    if amount_column:

        chart_df = (
            data.groupby(type_column, dropna=False)[amount_column]
            .sum()
            .reset_index()
            .sort_values(amount_column, ascending=True)
        )

        value_col = amount_column

    else:

        chart_df = (
            data[type_column]
            .fillna("Not Available")
            .value_counts()
            .reset_index()
        )

        chart_df.columns = [
            type_column,
            "Applications"
        ]

        value_col = "Applications"

    fig = px.bar(
        chart_df,
        x=value_col,
        y=type_column,
        orientation="h",
        text=value_col,
        color_discrete_sequence=[BLUE]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Loan Amount" if amount_column else "Applications",
        yaxis_title="Loan Type"
    )

    return chart_layout(
        fig,
        max(350, len(chart_df) * 42)
    )


def monthly_chart(data, date_column, amount_column):

    chart_df = data.dropna(
        subset=[date_column]
    ).copy()

    if chart_df.empty:

        st.info("No valid dates available.")
        return

    chart_df["Month"] = (
        chart_df[date_column]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    if amount_column:

        monthly = (
            chart_df.groupby("Month")[amount_column]
            .sum()
            .reset_index()
        )

        value_col = amount_column
        chart_title = "Monthly Loan Amount"

    else:

        monthly = (
            chart_df.groupby("Month")
            .size()
            .reset_index(name="Applications")
        )

        value_col = "Applications"
        chart_title = "Monthly Applications"

    fig = px.bar(
        monthly,
        x="Month",
        y=value_col,
        text=value_col,
        color_discrete_sequence=[BLUE]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        title=chart_title,
        xaxis_title="Month",
        yaxis_title=value_col,
        showlegend=False
    )

    st.plotly_chart(
        chart_layout(fig, 370),
        use_container_width=True
    )


def ranking_chart(data, group_column, amount_column, title):

    if amount_column:

        ranking = (
            data.groupby(group_column)[amount_column]
            .sum()
            .nlargest(10)
            .sort_values()
            .reset_index()
        )

        value_col = amount_column

    else:

        ranking = (
            data[group_column]
            .value_counts()
            .head(10)
            .sort_values()
            .reset_index()
        )

        ranking.columns = [
            group_column,
            "Applications"
        ]

        value_col = "Applications"

    fig = px.bar(
        ranking,
        x=value_col,
        y=group_column,
        orientation="h",
        text=value_col,
        color_discrete_sequence=[ORANGE]
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        title=title,
        showlegend=False
    )

    st.plotly_chart(
        chart_layout(
            fig,
            max(350, len(ranking) * 42)
        ),
        use_container_width=True
    )


# =========================================================
# 13. SUMMARY PAGE
# =========================================================

if page == "Summary":

    show_header(
        "Loan Portfolio Overview",
        "Monitor applications, loan value and portfolio performance."
    )

    filter_fields = [
        key for key in ["type", "status", "date"]
        if columns.get(key)
    ]

    filtered_df = apply_page_filters(
        df,
        "summary",
        filter_fields,
        columns
    )

    add_kpis(filtered_df, columns)

    st.write("")

    left, right = st.columns(
        [1, 1],
        gap="large"
    )

    with left:

        if status_col:

            show_panel_title("Application Status")

            st.plotly_chart(
                status_chart(filtered_df, status_col),
                use_container_width=True
            )

    with right:

        if type_col:

            show_panel_title("Loan Portfolio by Type")

            fig = loan_type_chart(
                filtered_df,
                type_col,
                amount_col
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    if date_col:

        show_panel_title("Monthly Portfolio Trend")

        monthly_chart(
            filtered_df,
            date_col,
            amount_col
        )

    if bank_col:

        show_panel_title("Bank-wise Portfolio")

        ranking_chart(
            filtered_df,
            bank_col,
            amount_col,
            "Top Banks by Loan Amount"
        )


# =========================================================
# 14. LOAN TYPES PAGE
# =========================================================

elif page == "Loan Types":

    show_header(
        "Loan Type Analysis",
        "Understand the performance and distribution of each loan category."
    )

    if not type_col:

        st.warning("Loan Type column not found.")
        st.stop()

    filter_fields = [
        key for key in ["type", "status", "date"]
        if columns.get(key)
    ]

    filtered_df = apply_page_filters(
        df,
        "loan_types",
        filter_fields,
        columns
    )

    add_kpis(filtered_df, columns)

    st.write("")

    show_panel_title("Loan Type Distribution")

    fig = loan_type_chart(
        filtered_df,
        type_col,
        amount_col
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if status_col:

        show_panel_title("Status by Loan Type")

        status_type = (
            filtered_df.groupby(
                [type_col, status_col]
            )
            .size()
            .reset_index(name="Applications")
        )

        fig = px.bar(
            status_type,
            x=type_col,
            y="Applications",
            color=status_col,
            barmode="stack",
            color_discrete_map=STATUS_COLORS
        )

        fig.update_layout(
            xaxis_title="Loan Type",
            yaxis_title="Applications"
        )

        st.plotly_chart(
            chart_layout(fig, 400),
            use_container_width=True
        )


# =========================================================
# 15. BANKS PAGE
# =========================================================

elif page == "Banks":

    show_header(
        "Bank Performance",
        "Compare lending partners by applications and loan value."
    )

    if not bank_col:

        st.warning("Bank Name column not found.")
        st.stop()

    filter_fields = [
        key for key in ["bank", "type", "status", "date"]
        if columns.get(key)
    ]

    filtered_df = apply_page_filters(
        df,
        "banks",
        filter_fields,
        columns
    )

    add_kpis(filtered_df, columns)

    st.write("")

    show_panel_title("Bank-wise Loan Portfolio")

    ranking_chart(
        filtered_df,
        bank_col,
        amount_col,
        "Top Banks by Loan Amount"
    )

    if status_col:

        show_panel_title("Bank-wise Application Status")

        bank_status = (
            filtered_df.groupby(
                [bank_col, status_col]
            )
            .size()
            .reset_index(name="Applications")
        )

        fig = px.bar(
            bank_status,
            x=bank_col,
            y="Applications",
            color=status_col,
            barmode="stack",
            color_discrete_map=STATUS_COLORS
        )

        fig.update_layout(
            xaxis_title="Bank",
            yaxis_title="Applications"
        )

        st.plotly_chart(
            chart_layout(fig, 420),
            use_container_width=True
        )


# =========================================================
# 16. EXECUTIVES PAGE
# =========================================================

elif page == "Executives":

    show_header(
        "Executive Performance",
        "Track individual executive performance and application outcomes."
    )

    if not executive_col:

        st.warning("Executive Name column not found.")
        st.stop()

    filter_fields = [
        key for key in ["executive", "type", "status", "date"]
        if columns.get(key)
    ]

    filtered_df = apply_page_filters(
        df,
        "executives",
        filter_fields,
        columns
    )

    add_kpis(filtered_df, columns)

    st.write("")

    show_panel_title("Executive-wise Performance")

    ranking_chart(
        filtered_df,
        executive_col,
        amount_col,
        "Top Executives by Loan Amount"
    )

    if status_col:

        show_panel_title("Executive-wise Application Status")

        executive_status = (
            filtered_df.groupby(
                [executive_col, status_col]
            )
            .size()
            .reset_index(name="Applications")
        )

        fig = px.bar(
            executive_status,
            x=executive_col,
            y="Applications",
            color=status_col,
            barmode="stack",
            color_discrete_map=STATUS_COLORS
        )

        fig.update_layout(
            xaxis_title="Executive",
            yaxis_title="Applications"
        )

        st.plotly_chart(
            chart_layout(fig, 420),
            use_container_width=True
        )


# =========================================================
# 17. RECORDS PAGE
# =========================================================

elif page == "Records":

    show_header(
        "Loan Records",
        "Search, filter, review and export individual loan applications."
    )

    filter_fields = [
        key for key in [
            "type",
            "status",
            "bank",
            "executive",
            "date"
        ]
        if columns.get(key)
    ]

    filtered_df = apply_page_filters(
        df,
        "records",
        filter_fields,
        columns
    )

    search_text = st.text_input(
        "Search Records",
        placeholder="Search customer, bank, executive or loan details...",
        key="records_search"
    )

    if search_text:

        search_mask = filtered_df.astype(str).apply(
            lambda col: col.str.contains(
                search_text,
                case=False,
                na=False,
                regex=False
            )
        ).any(axis=1)

        filtered_df = filtered_df[search_mask]

    st.markdown(
        f"**{len(filtered_df):,} records found**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=520
    )

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "Download Filtered Records (CSV)",
        data=csv_data,
        file_name="jr_financial_loan_records.csv",
        mime="text/csv",
        use_container_width=True
    )


# =========================================================
# 18. KPI METRICS PAGE
# =========================================================

elif page == "KPI Metrics":

    show_header(
        "KPI Metrics",
        "Review key portfolio indicators and application performance."
    )

    filter_fields = [
        key for key in [
            "type",
            "status",
            "bank",
            "executive",
            "date"
        ]
        if columns.get(key)
    ]

    filtered_df = apply_page_filters(
        df,
        "kpi_metrics",
        filter_fields,
        columns
    )

    add_kpis(filtered_df, columns)

    st.write("")

    if status_col:

        status_counts = (
            filtered_df[status_col]
            .fillna("Not Available")
            .value_counts()
        )

        total = len(filtered_df)

        disbursed = int(
            status_counts.get("Disbursed", 0)
        )

        approved = int(
            status_counts.get("Approved", 0)
        )

        rejected = int(
            status_counts.get("Rejected", 0)
        )

        disbursement_rate = (
            disbursed / total * 100
            if total else 0
        )

        approval_rate = (
            approved / total * 100
            if total else 0
        )

        rejection_rate = (
            rejected / total * 100
            if total else 0
        )

        metric_cols = st.columns(
            3,
            gap="medium"
        )

        with metric_cols[0]:

            show_kpi(
                "Disbursement Rate",
                f"{disbursement_rate:.1f}%",
                "Disbursed / total applications"
            )

        with metric_cols[1]:

            show_kpi(
                "Approval Rate",
                f"{approval_rate:.1f}%",
                "Approved / total applications"
            )

        with metric_cols[2]:

            show_kpi(
                "Rejection Rate",
                f"{rejection_rate:.1f}%",
                "Rejected / total applications"
            )

        st.write("")

        show_panel_title("Application Status Breakdown")

        status_breakdown = (
            status_counts
            .rename_axis("Status")
            .reset_index(name="Applications")
        )

        fig = px.bar(
            status_breakdown,
            x="Status",
            y="Applications",
            color="Status",
            color_discrete_map=STATUS_COLORS,
            text="Applications"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            chart_layout(fig, 370),
            use_container_width=True
        )

    if amount_col and type_col:

        show_panel_title("Loan Amount by Category")

        category_metrics = (
            filtered_df.groupby(type_col)[amount_col]
            .agg(["count", "sum", "mean"])
            .reset_index()
        )

        category_metrics.columns = [
            "Loan Type",
            "Applications",
            "Total Loan Amount",
            "Average Loan Amount"
        ]

        category_metrics["Total Loan Amount"] = (
            category_metrics["Total Loan Amount"].apply(money_inr)
        )

        category_metrics["Average Loan Amount"] = (
            category_metrics["Average Loan Amount"].apply(money_inr)
        )

        st.dataframe(
            category_metrics,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# 19. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        JR Financial · Loan Portfolio Analytics
    </div>
    """,
    unsafe_allow_html=True
)
