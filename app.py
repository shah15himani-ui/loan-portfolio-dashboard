
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ============================================================
# JR FINANCIAL | LOAN PORTFOLIO ANALYTICS
# ============================================================

st.set_page_config(
    page_title="JR Financial | Loan Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# COLORS
# ============================================================

NAVY = "#172B4D"
BLUE = "#4776E6"
TEAL = "#20A68A"
PURPLE = "#8067C7"
AMBER = "#E7A83E"
RED = "#D96C78"
INK = "#202B3C"
MUTED = "#78869A"
BORDER = "#E8EDF4"
BG = "#F5F7FB"

STATUS_COLORS = {
    "Disbursed": TEAL,
    "Approved": BLUE,
    "Under Review": AMBER,
    "Pending": PURPLE,
    "Rejected": RED
}

# ============================================================
# SESSION STATE
# ============================================================

for key, default in {
    "data_bytes": None,
    "sheet_name": None,
    "loaded": False,
    "navigation": "Overview",
}.items():

    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# CUSTOM DESIGN
# ============================================================

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
}}

.stApp {{
    background: {BG};
    color: {INK};
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

.block-container {{
    max-width: 1600px;
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {NAVY} 0%, #203B63 100%);
    border-right: 0;
}}

section[data-testid="stSidebar"] > div {{
    padding: 1.5rem 1rem;
}}

section[data-testid="stSidebar"] * {{
    color: #F7F9FC;
}}

section[data-testid="stSidebar"] [data-testid="stRadio"] > label {{
    color: #AFC0D8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.7px;
}}

section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {{
    gap: 5px;
}}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    padding: 9px 12px;
    border-radius: 9px;
}}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background: rgba(255,255,255,.10);
}}

section[data-testid="stSidebar"] [data-testid="stRadio"] label p {{
    font-size: 13px;
    font-weight: 600;
}}

.brand {{
    color: #FFFFFF;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: 1.1px;
}}

.brand-sub {{
    color: #AFC0D8;
    font-size: 9px;
    letter-spacing: 2px;
    margin-top: 3px;
    margin-bottom: 28px;
}}

.sidebar-note {{
    color: #B9C7D9;
    font-size: 11px;
    line-height: 1.6;
}}

.page-kicker {{
    color: {BLUE};
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 2px 0 7px;
}}

.page-title {{
    color: {NAVY};
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -.7px;
    margin: 0;
}}

.page-subtitle {{
    color: {MUTED};
    font-size: 13px;
    margin: 5px 0 20px;
}}

.section-title {{
    color: {NAVY};
    font-size: 15px;
    font-weight: 800;
    margin: 5px 0 11px;
}}

.kpi {{
    background: #FFFFFF;
    border: 1px solid {BORDER};
    border-radius: 15px;
    padding: 17px 18px;
    min-height: 125px;
    box-shadow: 0 5px 18px rgba(24,45,77,.035);
    position: relative;
    overflow: hidden;
}}

.kpi:after {{
    content: "";
    position: absolute;
    right: -22px;
    top: -30px;
    width: 85px;
    height: 85px;
    border-radius: 50%;
    background: var(--tint);
    opacity: .12;
}}

.kpi-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}}

.kpi-label {{
    color: {MUTED};
    font-size: 11px;
    font-weight: 700;
}}

.kpi-icon {{
    width: 30px;
    height: 30px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--tint);
    color: var(--accent);
    font-size: 15px;
}}

.kpi-value {{
    color: {NAVY};
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -.6px;
    margin-top: 13px;
    line-height: 1.15;
}}

.kpi-note {{
    color: #9AA5B4;
    font-size: 10px;
    margin-top: 7px;
}}

div[data-testid="stPlotlyChart"] {{
    background: #FFFFFF;
    border: 1px solid {BORDER};
    border-radius: 15px;
    padding: 7px;
    box-shadow: 0 5px 18px rgba(24,45,77,.025);
}}

div[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 12px;
    overflow: hidden;
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {{
    border-radius: 9px;
    border-color: {BORDER};
}}

.stButton button,
.stDownloadButton button {{
    border-radius: 9px;
    font-weight: 700;
}}

.stButton button[kind="primary"] {{
    background: {BLUE};
    border-color: {BLUE};
}}

.footer {{
    text-align: center;
    color: #A5AFBC;
    font-size: 10px;
    padding-top: 28px;
}}

@media(max-width:800px) {{
    .block-container {{
        padding: 1rem .8rem 2rem;
    }}

    .page-title {{
        font-size: 23px;
    }}

    .kpi-value {{
        font-size: 21px;
    }}
}}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_col(df, aliases):

    aliases = {
        x.lower().strip().replace("_", " ")
        for x in aliases
    }

    for col in df.columns:

        normalized = (
            str(col)
            .lower()
            .strip()
            .replace("_", " ")
        )

        if normalized in aliases:
            return col

    return None


def detect_columns(df):

    return {
        "amount": find_col(
            df,
            [
                "loan amount",
                "amount",
                "loan value",
                "sanction amount",
                "disbursed amount"
            ]
        ),

        "status": find_col(
            df,
            [
                "status",
                "application status",
                "loan status"
            ]
        ),

        "type": find_col(
            df,
            [
                "loan type",
                "type of loan",
                "loan category",
                "product type"
            ]
        ),

        "bank": find_col(
            df,
            [
                "bank",
                "bank name",
                "lender",
                "financial institution"
            ]
        ),

        "executive": find_col(
            df,
            [
                "executive",
                "executive name",
                "sales executive",
                "relationship manager",
                "rm name"
            ]
        ),

        "date": find_col(
            df,
            [
                "date",
                "application date",
                "created date",
                "login date",
                "disbursement date"
            ]
        ),

        "customer": find_col(
            df,
            [
                "customer name",
                "applicant name",
                "client name",
                "name"
            ]
        )
    }


def clean_data(df):

    df = df.copy()

    df = df.dropna(
        axis=0,
        how="all"
    ).dropna(
        axis=1,
        how="all"
    )

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    df = df.loc[
        :,
        ~pd.Index(df.columns).str.contains(
            r"^Unnamed",
            case=False
        )
    ]

    cols = detect_columns(df)

    if cols["amount"]:

        df[cols["amount"]] = pd.to_numeric(
            df[cols["amount"]]
            .astype(str)
            .str.replace(r"[₹,$,]", "", regex=True)
            .str.replace(" ", "", regex=False),
            errors="coerce"
        ).fillna(0)

    if cols["date"]:

        df[cols["date"]] = pd.to_datetime(
            df[cols["date"]],
            errors="coerce",
            dayfirst=True
        )

    if cols["status"]:

        df[cols["status"]] = (
            df[cols["status"]]
            .fillna("Not Available")
            .astype(str)
            .str.strip()
            .str.title()
        )

    return df


def inr(value):

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    if value >= 1e7:
        return f"₹{value / 1e7:.2f} Cr"

    if value >= 1e5:
        return f"₹{value / 1e5:.2f} L"

    return f"₹{value:,.0f}"


def header(title, subtitle):

    st.markdown(
        f"""
        <div class="page-kicker">
            JR FINANCIAL / PORTFOLIO INTELLIGENCE
        </div>

        <div class="page-title">
            {title}
        </div>

        <div class="page-subtitle">
            {subtitle}
        </div>
        """,
        unsafe_allow_html=True
    )


def section(title):

    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True
    )


def kpi(label, value, note, icon, accent):

    st.markdown(
        f"""
        <div class="kpi"
             style="--accent:{accent};--tint:{accent};">

            <div class="kpi-top">
                <div class="kpi-label">{label}</div>
                <div class="kpi-icon">{icon}</div>
            </div>

            <div class="kpi-value">{value}</div>

            <div class="kpi-note">{note}</div>

        </div>
        """,
        unsafe_allow_html=True
    )


def base_layout(fig, height=350):

    fig.update_layout(
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",

        font=dict(
            family="DM Sans, Arial",
            color=INK,
            size=11
        ),

        margin=dict(
            l=20,
            r=25,
            t=35,
            b=25
        ),

        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_color=INK
        ),

        legend=dict(
            font=dict(
                size=10,
                color=MUTED
            )
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor=BORDER
    )

    fig.update_yaxes(
        gridcolor="#EEF1F6",
        zeroline=False
    )

    return fig


# ============================================================
# CONCENTRIC DOUBLE-RING PIE CHART
# ============================================================

def status_donut(data, cols):

    status_col = cols["status"]
    amount_col = cols["amount"]

    if not status_col:

        st.info(
            "Add a Status column to display the application status chart."
        )

        return

    temp = data.copy()

    temp["_status"] = (
        temp[status_col]
        .fillna("Not Available")
        .astype(str)
        .str.strip()
        .replace("", "Not Available")
    )

    order = (
        temp["_status"]
        .value_counts()
        .index.tolist()
    )

    fallback = [
        NAVY,
        BLUE,
        PURPLE,
        TEAL,
        AMBER,
        RED
    ]

    colors = [
        STATUS_COLORS.get(
            status,
            fallback[i % len(fallback)]
        )
        for i, status in enumerate(order)
    ]

    counts = (
        temp["_status"]
        .value_counts()
        .reindex(order)
    )

    fig = go.Figure()

    # OUTER RING: APPLICATION COUNT

    fig.add_trace(
        go.Pie(
            labels=order,
            values=counts.values,
            name="Applications",
            hole=.68,
            sort=False,

            marker=dict(
                colors=colors,
                line=dict(
                    color="#FFFFFF",
                    width=3
                )
            ),

            textposition="inside",
            texttemplate="%{percent}",

            hovertemplate=(
                "<b>%{label}</b><br>"
                "Applications: %{value:,}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),

            domain=dict(
                x=[.05, .95],
                y=[.02, .98]
            )
        )
    )

    # INNER RING: LOAN AMOUNT

    if amount_col:

        amounts = pd.to_numeric(
            temp[amount_col],
            errors="coerce"
        ).fillna(0)

        temp["_amount"] = amounts

        by_status = (
            temp.groupby("_status")["_amount"]
            .sum()
            .reindex(order, fill_value=0)
        )

        if by_status.sum() > 0:

            fig.add_trace(
                go.Pie(
                    labels=order,
                    values=by_status.values,
                    name="Loan Amount",
                    hole=.40,
                    sort=False,

                    marker=dict(
                        colors=colors,
                        line=dict(
                            color="#FFFFFF",
                            width=3
                        )
                    ),

                    textinfo="none",

                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Loan amount: ₹%{value:,.0f}<br>"
                        "Share: %{percent}"
                        "<extra></extra>"
                    ),

                    domain=dict(
                        x=[.25, .75],
                        y=[.22, .78]
                    ),

                    showlegend=False
                )
            )

    # CENTRE LABEL

    fig.add_annotation(
        x=.5,
        y=.5,

        text=(
            f"<b>{len(data):,}</b><br>"
            f"<span style='font-size:10px;color:{MUTED}'>"
            "APPLICATIONS</span>"
        ),

        showarrow=False,

        font=dict(
            size=22,
            color=NAVY
        )
    )

    fig.update_layout(
        height=365,
        paper_bgcolor="#FFFFFF",

        margin=dict(
            l=8,
            r=8,
            t=8,
            b=42
        ),

        legend=dict(
            orientation="h",
            y=-.10,
            x=.5,
            xanchor="center",
            font=dict(size=10)
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ============================================================
# BAR CHART
# ============================================================

def bar_chart(
    data,
    group_col,
    amount_col,
    title,
    color=BLUE,
    top=10
):

    if not group_col:

        st.info(
            f"A column for {title.lower()} was not detected."
        )

        return

    temp = data.copy()

    temp[group_col] = (
        temp[group_col]
        .fillna("Not Available")
        .astype(str)
    )

    if amount_col:

        temp[amount_col] = pd.to_numeric(
            temp[amount_col],
            errors="coerce"
        ).fillna(0)

        summary = (
            temp.groupby(group_col)[amount_col]
            .sum()
            .nlargest(top)
            .sort_values()
            .reset_index()
        )

        value_col = amount_col

    else:

        summary = (
            temp[group_col]
            .value_counts()
            .head(top)
            .sort_values()
            .rename_axis(group_col)
            .reset_index(name="Applications")
        )

        value_col = "Applications"

    fig = px.bar(
        summary,
        x=value_col,
        y=group_col,
        orientation="h",
        text=value_col,
        color_discrete_sequence=[color]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0
    )

    fig.update_layout(
        title=title,
        showlegend=False,
        xaxis_title=(
            "Loan amount"
            if amount_col
            else "Applications"
        ),
        yaxis_title=""
    )

    st.plotly_chart(
        base_layout(
            fig,
            max(320, len(summary) * 38)
        ),
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ============================================================
# MONTHLY TREND
# ============================================================

def monthly_trend(data, cols):

    date_col = cols["date"]

    if not date_col:

        st.info(
            "A date column was not detected for the monthly trend."
        )

        return

    temp = data.dropna(
        subset=[date_col]
    ).copy()

    if temp.empty:

        st.info(
            "No valid dates are available for the monthly trend."
        )

        return

    temp["Month"] = (
        temp[date_col]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    if cols["amount"]:

        summary = (
            temp.groupby("Month")[cols["amount"]]
            .sum()
            .reset_index()
        )

        value_col = cols["amount"]
        title = "Monthly loan value"

    else:

        summary = (
            temp.groupby("Month")
            .size()
            .reset_index(name="Applications")
        )

        value_col = "Applications"
        title = "Monthly applications"

    fig = px.area(
        summary,
        x="Month",
        y=value_col,
        markers=True,
        color_discrete_sequence=[BLUE]
    )

    fig.update_traces(
        line_width=3,
        fill="tozeroy",
        fillcolor="rgba(71,118,230,.10)"
    )

    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title=(
            "Loan amount"
            if cols["amount"]
            else "Applications"
        ),
        showlegend=False
    )

    st.plotly_chart(
        base_layout(fig, 340),
        use_container_width=True,
        config={"displayModeBar": False}
    )


# ============================================================
# DATE FILTER
# ============================================================

def apply_date_filter(
    data,
    cols,
    key="date_range"
):

    date_col = cols["date"]

    if not date_col:

        st.info(
            "No date column was detected. Showing all records."
        )

        return data.copy()

    dates = pd.to_datetime(
        data[date_col],
        errors="coerce"
    ).dropna()

    if dates.empty:

        st.info(
            "No valid dates were found. Showing all records."
        )

        return data.copy()

    start = dates.min().date()
    end = dates.max().date()

    selected = st.date_input(
        "Date range",
        value=(start, end),
        min_value=start,
        max_value=end,
        key=key,
        format="DD/MM/YYYY"
    )

    if (
        isinstance(selected, (tuple, list))
        and len(selected) == 2
    ):

        s, e = selected

        values = pd.to_datetime(
            data[date_col],
            errors="coerce"
        ).dt.date

        return data[
            values.between(s, e)
        ].copy()

    return data.copy()


# ============================================================
# KPI CARDS
# ============================================================

def add_kpis(data, cols):

    amount_col = cols["amount"]
    status_col = cols["status"]

    total = len(data)

    amount = (
        pd.to_numeric(
            data[amount_col],
            errors="coerce"
        ).fillna(0).sum()
        if amount_col
        else 0
    )

    status = (
        data[status_col]
        .astype(str)
        .str.strip()
        .str.lower()
        if status_col
        else pd.Series(dtype=str)
    )

    disbursed = (
        int(status.eq("disbursed").sum())
        if status_col
        else 0
    )

    pending = (
        int(status.eq("pending").sum())
        if status_col
        else 0
    )

    cards = st.columns(
        4,
        gap="medium"
    )

    with cards[0]:

        kpi(
            "Total applications",
            f"{total:,}",
            "Records in current selection",
            "▤",
            BLUE
        )

    with cards[1]:

        kpi(
            "Portfolio value",
            inr(amount),
            "Combined loan amount",
            "₹",
            PURPLE
        )

    with cards[2]:

        kpi(
            "Disbursed",
            f"{disbursed:,}",
            "Successfully disbursed cases",
            "✓",
            TEAL
        )

    with cards[3]:

        kpi(
            "Pending",
            f"{pending:,}",
            "Awaiting further action",
            "◷",
            AMBER
        )


# ============================================================
# UPLOAD SCREEN
# ============================================================

if not st.session_state.loaded:

    st.markdown(
        f"""
        <div style='text-align:center;padding:35px 0 18px;'>

            <div style='font-size:12px;font-weight:800;
                        letter-spacing:3px;color:{BLUE};'>
                JR FINANCIAL
            </div>

            <div style='font-size:34px;font-weight:800;
                        color:{NAVY};margin-top:9px;'>
                Loan Portfolio Analytics
            </div>

            <div style='font-size:14px;color:{MUTED};
                        margin-top:7px;'>
                A clear view of your lending performance.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    _, center, _ = st.columns([1, 1.5, 1])

    with center:

        with st.container(border=True):

            st.subheader(
                "Upload your portfolio workbook"
            )

            st.caption(
                "Choose an Excel workbook to build your live dashboard."
            )

            uploaded = st.file_uploader(
                "Excel file",
                type=["xlsx", "xls"],
                label_visibility="collapsed"
            )

            if uploaded:

                raw = uploaded.getvalue()

                try:

                    book = pd.ExcelFile(
                        BytesIO(raw)
                    )

                    sheet = st.selectbox(
                        "Worksheet",
                        book.sheet_names
                    )

                    preview = pd.read_excel(
                        BytesIO(raw),
                        sheet_name=sheet
                    )

                    st.success(
                        f"Loaded {len(preview):,} rows and "
                        f"{len(preview.columns):,} columns."
                    )

                    st.dataframe(
                        preview.head(5),
                        use_container_width=True,
                        hide_index=True
                    )

                    if st.button(
                        "Open dashboard →",
                        type="primary",
                        use_container_width=True
                    ):

                        st.session_state.data_bytes = raw
                        st.session_state.sheet_name = sheet
                        st.session_state.loaded = True

                        st.rerun()

                except Exception as exc:

                    st.error(
                        f"Could not read this workbook: {exc}"
                    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:

    raw_df = pd.read_excel(
        BytesIO(st.session_state.data_bytes),
        sheet_name=st.session_state.sheet_name
    )

    df = clean_data(raw_df)

except Exception as exc:

    st.error(
        f"Unable to load the selected worksheet: {exc}"
    )

    if st.button("Back to upload"):

        st.session_state.loaded = False
        st.rerun()

    st.stop()


if df.empty:

    st.error(
        "The selected worksheet does not contain any records."
    )

    st.stop()


cols = detect_columns(df)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">JR FINANCIAL</div>
        <div class="brand-sub">PORTFOLIO INTELLIGENCE</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "WORKSPACE",
        [
            "Overview",
            "Loan Types",
            "Banks",
            "Executives",
            "Records",
            "KPI Metrics"
        ],
        key="navigation"
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div class="sidebar-note">
            Workbook loaded<br>
            <b>{len(df):,} records</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "Replace workbook",
        use_container_width=True
    ):

        st.session_state.loaded = False
        st.session_state.data_bytes = None
        st.session_state.sheet_name = None

        st.rerun()

    st.markdown("---")

    st.markdown(
        """
        <div class="sidebar-note">
            JR Financial<br>
            Loan Portfolio Analytics
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# OVERVIEW PAGE
# ============================================================

if page == "Overview":

    # Only one filter on the Overview page.
    filtered = apply_date_filter(
        df,
        cols,
        "overview_date_range"
    )

    add_kpis(
        filtered,
        cols
    )

    st.write("")

    left, right = st.columns(
        [1, 1],
        gap="large"
    )

    with left:

        section("Portfolio status")

        status_donut(
            filtered,
            cols
        )

    with right:

        section("Loan portfolio by type")

        bar_chart(
            filtered,
            cols["type"],
            cols["amount"],
            "Top loan categories",
            PURPLE
        )

    section("Portfolio movement")

    monthly_trend(
        filtered,
        cols
    )

    if cols["bank"]:

        section("Leading banking partners")

        bar_chart(
            filtered,
            cols["bank"],
            cols["amount"],
            "Top banks by portfolio value",
            TEAL,
            top=8
        )


# ============================================================
# LOAN TYPES PAGE
# ============================================================

elif page == "Loan Types":

    header(
        "Loan type analysis",
        "Understand which products contribute to your portfolio."
    )

    if not cols["type"]:

        st.warning(
            "A Loan Type column was not detected in this workbook."
        )

    else:

        filtered = df.copy()

        bar_chart(
            filtered,
            cols["type"],
            cols["amount"],
            "Portfolio by loan type",
            BLUE,
            top=15
        )

        if cols["status"]:

            temp = filtered.copy()

            temp[cols["type"]] = (
                temp[cols["type"]]
                .fillna("Not Available")
            )

            temp[cols["status"]] = (
                temp[cols["status"]]
                .fillna("Not Available")
            )

            grouped = (
                temp.groupby(
                    [cols["type"], cols["status"]]
                )
                .size()
                .reset_index(name="Applications")
            )

            fig = px.bar(
                grouped,
                x=cols["type"],
                y="Applications",
                color=cols["status"],
                barmode="stack",
                color_discrete_map=STATUS_COLORS
            )

            fig.update_layout(
                title="Application status by loan type",
                xaxis_title="",
                yaxis_title="Applications"
            )

            st.plotly_chart(
                base_layout(fig, 390),
                use_container_width=True,
                config={"displayModeBar": False}
            )


# ============================================================
# BANKS PAGE
# ============================================================

elif page == "Banks":

    header(
        "Bank performance",
        "Compare lending partners by application volume and loan value."
    )

    if not cols["bank"]:

        st.warning(
            "A Bank Name column was not detected in this workbook."
        )

    else:

        bar_chart(
            df,
            cols["bank"],
            cols["amount"],
            "Top banks by portfolio value",
            BLUE,
            top=15
        )

        if cols["status"]:

            temp = df.copy()

            temp[cols["bank"]] = (
                temp[cols["bank"]]
                .fillna("Not Available")
            )

            temp[cols["status"]] = (
                temp[cols["status"]]
                .fillna("Not Available")
            )

            grouped = (
                temp.groupby(
                    [cols["bank"], cols["status"]]
                )
                .size()
                .reset_index(name="Applications")
            )

            fig = px.bar(
                grouped,
                x=cols["bank"],
                y="Applications",
                color=cols["status"],
                barmode="stack",
                color_discrete_map=STATUS_COLORS
            )

            fig.update_layout(
                title="Application status by bank",
                xaxis_title="",
                yaxis_title="Applications"
            )

            st.plotly_chart(
                base_layout(fig, 390),
                use_container_width=True,
                config={"displayModeBar": False}
            )


# ============================================================
# EXECUTIVES PAGE
# ============================================================

elif page == "Executives":

    header(
        "Executive performance",
        "Review individual contribution and portfolio outcomes."
    )

    if not cols["executive"]:

        st.warning(
            "An Executive Name column was not detected in this workbook."
        )

    else:

        bar_chart(
            df,
            cols["executive"],
            cols["amount"],
            "Top executives by portfolio value",
            PURPLE,
            top=15
        )

        if cols["status"]:

            temp = df.copy()

            temp[cols["executive"]] = (
                temp[cols["executive"]]
                .fillna("Not Available")
            )

            temp[cols["status"]] = (
                temp[cols["status"]]
                .fillna("Not Available")
            )

            grouped = (
                temp.groupby(
                    [cols["executive"], cols["status"]]
                )
                .size()
                .reset_index(name="Applications")
            )

            fig = px.bar(
                grouped,
                x=cols["executive"],
                y="Applications",
                color=cols["status"],
                barmode="stack",
                color_discrete_map=STATUS_COLORS
            )

            fig.update_layout(
                title="Executive application outcomes",
                xaxis_title="",
                yaxis_title="Applications"
            )

            st.plotly_chart(
                base_layout(fig, 390),
                use_container_width=True,
                config={"displayModeBar": False}
            )


# ============================================================
# RECORDS PAGE
# ============================================================

elif page == "Records":

    header(
        "Loan records",
        "Search, inspect and export the underlying portfolio data."
    )

    search = st.text_input(
        "Search all columns",
        placeholder="Enter a customer, bank, status or keyword..."
    )

    view = df.copy()

    if search:

        mask = (
            view.astype(str)
            .apply(
                lambda col: col.str.contains(
                    search,
                    case=False,
                    na=False,
                    regex=False
                )
            )
            .any(axis=1)
        )

        view = view[mask]

    st.caption(
        f"{len(view):,} records"
    )

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        height=520
    )

    st.download_button(
        "Download filtered records as CSV",
        view.to_csv(index=False).encode("utf-8-sig"),
        file_name="jr_financial_loan_records.csv",
        mime="text/csv"
    )


# ============================================================
# KPI METRICS PAGE
# ============================================================

elif page == "KPI Metrics":

    header(
        "Portfolio KPI metrics",
        "A focused view of application outcomes and portfolio quality."
    )

    add_kpis(
        df,
        cols
    )

    if cols["status"]:

        status = (
            df[cols["status"]]
            .fillna("Not Available")
            .astype(str)
            .str.strip()
            .str.title()
        )

        total = len(df)

        disbursed = int(
            status.eq("Disbursed").sum()
        )

        approved = int(
            status.eq("Approved").sum()
        )

        rejected = int(
            status.eq("Rejected").sum()
        )

        a, b, c = st.columns(
            3,
            gap="medium"
        )

        with a:

            kpi(
                "Disbursement rate",
                f"{disbursed / total * 100:.1f}%" if total else "0.0%",
                "Disbursed / all applications",
                "✓",
                TEAL
            )

        with b:

            kpi(
                "Approval rate",
                f"{approved / total * 100:.1f}%" if total else "0.0%",
                "Approved / all applications",
                "↗",
                BLUE
            )

        with c:

            kpi(
                "Rejection rate",
                f"{rejected / total * 100:.1f}%" if total else "0.0%",
                "Rejected / all applications",
                "×",
                RED
            )

        breakdown = (
            status.value_counts()
            .rename_axis("Status")
            .reset_index(name="Applications")
        )

        fig = px.bar(
            breakdown,
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

        fig.update_layout(
            title="Application status breakdown",
            showlegend=False
        )

        st.plotly_chart(
            base_layout(fig, 360),
            use_container_width=True,
            config={"displayModeBar": False}
        )

    if cols["type"] and cols["amount"]:

        temp = (
            df.groupby(cols["type"])[cols["amount"]]
            .agg(
                Applications="count",
                Total_Amount="sum",
                Average_Amount="mean"
            )
            .reset_index()
        )

        temp["Total Loan Amount"] = (
            temp["Total_Amount"].apply(inr)
        )

        temp["Average Loan Amount"] = (
            temp["Average_Amount"].apply(inr)
        )

        st.dataframe(
            temp[
                [
                    cols["type"],
                    "Applications",
                    "Total Loan Amount",
                    "Average Loan Amount"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        JR FINANCIAL · LOAN PORTFOLIO ANALYTICS
    </div>
    """,
    unsafe_allow_html=True
)
