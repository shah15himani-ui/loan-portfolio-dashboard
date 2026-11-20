import io
import re
from html import escape
from random import Random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit import config

GROUND = "#0d2018"
PANEL = "#142a20"
TEXT = "#f2f7eb"
MUTED = "#adc4af"
ACCENT = "#dbf894"
CHART_SURFACE = "#101c16"
CHART_GRID = "#293a32"
CHART_SAGE = "#b8cbbd"
CHART_MUTED_SAGE = "#819689"
CHART_HEIGHT = 320
STATUS_RING_COLORS = ("#52665a", "#677e72", CHART_MUTED_SAGE, "#4a655b", "#75897c")

# Set the native widget palette in memory so the app ships in two files.
THEME = {
    "theme.base": "dark",
    "theme.primaryColor": ACCENT,
    "theme.backgroundColor": GROUND,
    "theme.secondaryBackgroundColor": PANEL,
    "theme.textColor": TEXT,
}
if any(st.get_option(key) != value for key, value in THEME.items()):
    for key, value in THEME.items():
        config.set_option(key, value)
    st.rerun()

st.set_page_config(
    page_title="Loan Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

PAGE_HEADERS = {
    "Upload": ("Loan portfolio", "dashboard", "Upload an Excel workbook to track applications, compare lenders, and see how your portfolio changes over time."),
    "Overview": ("Portfolio", "overview", "Monitor application status, disbursements, and portfolio trends."),
    "Loan Types": ("Loan", "types", "Compare application volumes and portfolio value by loan product."),
    "Banks": ("Bank", "breakdown", "Compare application volumes and portfolio value across lenders."),
    "Executives": ("Executive", "breakdown", "See application volumes and portfolio value by executive."),
    "Records": ("Loan", "records", "Search and export individual applications from the workbook."),
    "KPI Metrics": ("Portfolio", "KPI metrics", "Review disbursement rate, average loan amount, and application counts."),
}

st.html(
    """
    <style>
    .stApp {
        --surface: #142a20;
        --ground: #0d2018;
        --text: #f2f7eb;
        --muted: #adc4af;
        --line: #345442;
        --accent: #dbf894;
        --selected: #284733;
        color-scheme: dark;
        background:
            linear-gradient(96deg, #10241b 6%, #10241bea 28%, #10241b00 88%),
            radial-gradient(circle, #d4ed9e36 1px, transparent 1.6px) 0 0 / 14px 14px,
            radial-gradient(ellipse at 99% -5%, #365834, transparent 68%),
            linear-gradient(150deg, #12291d, #0a1a14 80%);
        color: var(--text);
    }
    .stApp :is([data-testid="stAppViewContainer"], [data-testid="stMain"]) { background: transparent; }
    .stApp [data-testid="stHeader"] { background: #0e2219eb; color: var(--text); }
    .stApp [data-testid="stHeader"] button { color: var(--muted); }
    .stApp [data-testid="stHeader"] button:hover { color: var(--accent); }
    .stApp .block-container {
        max-width: 1360px;
        padding: 3.85rem clamp(1rem, 3.2vw, 2.75rem) 2rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #192e21, #0d2018 78%);
        color: var(--text);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebarContent"] [data-testid="stSidebarUserContent"] { padding-top: 1.2rem; }
    .stApp h2, .stApp h3, .stApp h4 { color: var(--text); letter-spacing: -.027em; }
    .stApp h3 { font-size: 1.14rem; }
    .stApp [data-testid="stCaptionContainer"] { opacity: 1; }
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stCaptionContainer"] p { color: var(--muted); }

    .portfolio-header {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        display: flex;
        flex-wrap: wrap;
        align-items: flex-start;
        justify-content: space-between;
        gap: .7rem 1rem;
        padding: 1.4rem clamp(1.1rem, 3vw, 2rem) 1.55rem;
        border: 1px solid #57744976;
        border-radius: 18px;
        background: radial-gradient(ellipse at 101% 0%, #32532f, transparent 67%), #0d2018;
        color: var(--text);
    }
    .portfolio-header::after {
        position: absolute;
        z-index: -1;
        inset: 0 0 0 auto;
        width: min(43%, 26rem);
        background: radial-gradient(circle, #d4ed9e55 1px, transparent 1.6px) 0 0 / 14px 14px;
        mask-image: linear-gradient(90deg, transparent, #0008);
        content: "";
    }
    .portfolio-header h1 {
        margin: 0 0 .45rem;
        padding: 0;
        color: var(--text);
        font-size: clamp(1.85rem, 3.6vw, 3.05rem);
        line-height: 1.05;
        font-weight: 750;
        letter-spacing: -.038em;
    }
    .portfolio-header .heading-accent { color: var(--accent); }
    .portfolio-header p { max-width: 42rem; margin: 0; color: #d8e5d6; font-size: .95rem; }
    .sample-label {
        padding: .2rem .65rem;
        border: 1px solid #d4ed9e66;
        border-radius: 999px;
        color: #e5f7bb;
        font-size: .8rem;
        font-weight: 650;
        white-space: nowrap;
    }
    [data-testid="stMetric"], [class*="st-key-portfolio-panel-"] {
        background: linear-gradient(151deg, #1b3427, var(--surface) 64%);
        border-color: var(--line);
        border-radius: 16px;
        box-shadow: 0 9px 24px #06130e45;
    }
    [data-testid="stMetric"] { height: 100%; padding: .78rem 1rem; border: 1px solid var(--line); }
    .stApp [data-testid="stMetricLabel"] p { color: var(--muted); }
    .stApp [data-testid="stMetricValue"] { color: var(--accent); font-weight: 680; }
    [data-testid="stFileUploaderDropzone"] { background: var(--ground); border: 1px dashed #5c8466; }
    .stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stFileUploaderDropzone"] { color: var(--text); }
    .stApp :is([data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div) {
        background: var(--ground);
        color: var(--text);
        border-color: var(--line);
    }
    .stApp :is([data-baseweb="input"], [data-baseweb="select"] > div):focus-within { border-color: var(--accent); }
    .stApp button[data-testid="stBaseButton-primary"] { background: var(--accent); border-color: var(--accent); color: var(--ground); }
    .stApp button[data-testid="stBaseButton-primary"]:hover { background: #e9ffb3; border-color: #e9ffb3; }
    .stApp button[data-testid="stBaseButton-secondary"] { background: var(--surface); border-color: var(--line); color: var(--text); }
    .stApp button[data-testid="stBaseButton-secondary"]:hover { background: var(--selected); border-color: var(--accent); color: var(--accent); }
    .stApp button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

    .st-key-portfolio_navigation [role="radiogroup"] { gap: .15rem; }
    .st-key-portfolio_navigation [role="radiogroup"] label { margin: 0; padding: .32rem .5rem; border-radius: 8px; }
    .st-key-portfolio_navigation [role="radiogroup"] label:hover,
    .stApp [role="radiogroup"] label:has(input:checked) { background: var(--selected); }
    .stApp [role="radiogroup"] label:has(input:checked) > div:first-child { background: var(--accent); border-color: var(--accent); }
    .stApp [role="radiogroup"] label:has(input:checked) p { color: var(--accent); font-weight: 650; }
    .st-key-trend_measure [role="radiogroup"] { gap: .4rem; }
    .st-key-trend_measure [role="radiogroup"] label {
        margin: 0;
        padding: .2rem .5rem;
        border: 1px solid var(--line);
        border-radius: 8px;
    }
    .stApp [data-testid="stPlotlyChart"] {
        background: #101c16;
        border: 1px solid #23352b;
        border-radius: 10px;
    }
    .stApp [class*="st-key-portfolio-panel-"]:has(> [data-testid="stElementContainer"] [data-testid="stPlotlyChart"]) {
        min-height: 29rem;
    }
    .stApp [class*="st-key-portfolio-panel-"] > [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) {
        margin-top: auto;
    }
    .stApp .st-key-status_focus { max-width: 14rem; margin-inline: auto; }
    .stApp .st-key-status_focus [data-baseweb="select"] > div {
        background: #101c16;
        border-color: #34483b;
        border-radius: 999px;
    }
    .stApp .st-key-status_focus [data-baseweb="select"] > div:focus-within { border-color: #819689; }
    .loan-type-message {
        padding: 1rem;
        border: 1px dashed var(--line);
        border-radius: 10px;
        background: var(--ground);
        color: var(--muted);
        font-size: .9rem;
        line-height: 1.5;
    }
    .loan-type-message strong { display: block; margin-bottom: .35rem; color: var(--text); }
    @media (max-width: 640px) {
        .stApp .block-container { padding-top: 3.65rem; }
        .portfolio-header { border-radius: 14px; }
    }
    </style>
    """
)

if "data" not in st.session_state:
    st.session_state.data = None
if "page" not in st.session_state:
    st.session_state.page = "Upload"


def portfolio_header(page):
    title, accent, description = PAGE_HEADERS[page]
    tag = '<span class="sample-label">Sample data</span>' if page != "Upload" and st.session_state.get("demo") else ""
    st.html(
        f"""
        <header class="portfolio-header">
            <div>
                <h1>{title} <span class="heading-accent">{accent}</span></h1>
                <p>{description}</p>
            </div>
            {tag}
        </header>
        """
    )

def detect(df, aliases):
    columns = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in df.columns}
    for alias in aliases:
        key = re.sub(r"[^a-z0-9]", "", alias.lower())
        if key in columns:
            return columns[key]
    for alias in aliases:
        key = re.sub(r"[^a-z0-9]", "", alias.lower())
        if len(key) >= 5:
            for normalized, original in columns.items():
                if key in normalized:
                    return original
    return None

def amount(value):
    if pd.isna(value):
        return 0.0
    if isinstance(value, (float, int)):
        return float(value)
    s = str(value).replace(",", "").replace("₹", "").replace("$", "")
    s = re.sub(r"\b(?:INR|Rs\.?)\b", "", s, flags=re.I)
    match = re.search(r"-?\d+(?:\.\d+)?", s)
    if not match:
        return 0.0
    mult = 10000000 if re.search(r"\b(?:cr|crores?)\b", s, re.I) else 100000 if re.search(r"\b(?:lacs?|lakhs?)\b", s, re.I) else 1
    return float(match.group()) * mult

def money(value):
    if abs(value) >= 1e7:
        return f"₹{value/1e7:,.2f} Cr"
    if abs(value) >= 1e5:
        return f"₹{value/1e5:,.2f} L"
    return f"₹{value:,.0f}"

def clean(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    mapping = {
        "Amount": ["Loan Amount", "Sanction Amount", "Loan Value", "Disbursement Amount", "Finance Amount", "Amount"],
        "Status": ["Loan Status", "Application Status", "Current Status", "Status"],
        "LoanType": ["Loan Type", "Product Type", "Loan Category", "Product", "Category"],
        "Bank": ["Bank Name", "Lender", "Financial Institution", "Bank"],
        "Executive": ["Sales Executive", "Relationship Manager", "Employee Name", "Executive", "BDE", "RM", "Agent"],
        "Date": ["Application Date", "Created Date", "Entry Date", "Loan Date", "Submission Date", "Date"],
    }
    found = {k: detect(df, names) for k, names in mapping.items()}
    df["_Amount"] = df[found["Amount"]].map(amount) if found["Amount"] else 0.0
    for k in ("Status", "LoanType", "Bank", "Executive"):
        df[f"_{k}"] = df[found[k]].fillna("Not specified").astype(str).str.strip() if found[k] else "Not specified"
    if found["Date"]:
        source = df[found["Date"]]
        df["_Date"] = pd.to_datetime(source, errors="coerce", dayfirst=True)
    else:
        df["_Date"] = pd.NaT
    return df, found

def panel(name):
    return st.container(border=True, key=f"portfolio-panel-{name}")


def chart(fig, name, *, height=CHART_HEIGHT):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=12, r=18, t=18, b=22),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=13),
        hoverlabel=dict(bgcolor=GROUND, bordercolor=ACCENT, font_color=TEXT),
    )
    fig.update_xaxes(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID, tickfont=dict(color=MUTED), automargin=True)
    fig.update_yaxes(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID, tickfont=dict(color=MUTED), automargin=True)
    st.plotly_chart(
        fig,
        key=name,
        use_container_width=True,
        theme=None,
        config={"displayModeBar": False},
    )

def summary(data, key):
    return data.groupby(key, dropna=False).agg(Applications=("_Amount", "size"), Portfolio=("_Amount", "sum")).reset_index().sort_values("Applications", ascending=False)


def ranked_bar(rows, dimension, measure="Applications"):
    rows = rows.assign(Amount=rows["Portfolio"].map(money))
    fig = px.bar(
        rows.sort_values(measure, kind="stable"),
        x=measure,
        y=dimension,
        orientation="h",
        color_discrete_sequence=[CHART_SAGE],
        custom_data=["Amount", "Applications"],
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>%{customdata[1]:,} applications<br>Portfolio %{customdata[0]}<extra></extra>",
    )
    fig.update_layout(bargap=0.36, barcornerradius="50%")
    fig.update_yaxes(title=None, showgrid=False, ticklabelposition="outside", ticklabelstandoff=12)
    if measure == "Portfolio":
        fig.update_xaxes(title="Portfolio value", tickprefix="₹")
    else:
        fig.update_xaxes(title="Applications", tickformat=",d")
    return fig


def label_application_bars(fig, total, share_of):
    counts = fig.data[0].x
    fig.update_traces(
        text=[f"{count:,} · {count / total:.1%}" for count in counts],
        textposition="auto",
        textangle=0,
        textfont=dict(size=12),
        insidetextfont=dict(color=GROUND),
        outsidetextfont=dict(color=TEXT),
        cliponaxis=False,
        width=.42 if len(counts) == 1 else None,
        hovertemplate=(
            "<b>%{y}</b><br>%{text} " + share_of
            + "<br>Portfolio %{customdata[0]}<extra></extra>"
        ),
    )
    largest_count = max(counts)
    fig.update_xaxes(range=[0, largest_count * 1.28], dtick=1 if largest_count <= 7 else None)


def loan_amount_chart(data):
    amounts = data["_Amount"]
    valid = data.loc[amounts.gt(0) & amounts.lt(float("inf"))]
    if valid.empty:
        st.info("This view has no recorded positive loan amounts to compare.")
        return

    bands = ["Under ₹5L", "₹5L to under ₹10L", "₹10L to under ₹25L", "₹25L to under ₹50L", "₹50L and up"]
    amount_band = pd.cut(
        valid["_Amount"],
        bins=[0, 500_000, 1_000_000, 2_500_000, 5_000_000, float("inf")],
        labels=bands,
        right=False,
    )
    rows = (
        summary(valid.assign(AmountBand=amount_band.astype(str)), "AmountBand")
        .set_index("AmountBand")
        .reindex(bands, fill_value=0)
        .reset_index()
    )
    st.caption(f"Shares use the {len(valid):,} of {len(data):,} applications with a positive loan amount.")
    fig = ranked_bar(rows, "AmountBand")
    fig.update_yaxes(categoryorder="array", categoryarray=bands[::-1])
    label_application_bars(fig, len(valid), "of applications with positive amounts")
    for band in rows.loc[rows["Applications"].eq(0), "AmountBand"]:
        fig.add_annotation(x=0, y=band, text="0", xanchor="left", xshift=5, showarrow=False, font=dict(color=MUTED))
    chart(fig, "loan-amount-bands")


def loan_type_chart(data):
    total = len(data)
    if total == 0:
        st.info("No applications in this view.")
        return

    application_count = f"{total:,} {'application' if total == 1 else 'applications'}"
    loan_types = data["_LoanType"].str.strip()
    has_loan_type = loan_types.ne("") & loan_types.str.casefold().ne("not specified")
    classified = int(has_loan_type.sum())
    if classified == 0:
        if st.session_state.found.get("LoanType") is None:
            guidance = "The worksheet has no recognized loan-type column. Add a Loan Type, Product Type, or Loan Category column."
        else:
            guidance = "The loan-type column has no usable values for these applications. Fill in the loan types in the worksheet."
        st.html(
            f"""
            <div class="loan-type-message" role="status">
                <strong>No loan types to compare</strong>
                {application_count} without a loan type. {guidance}
            </div>
            """
        )
        return

    missing = total - classified
    caption = f"Shares are based on all {application_count} in this view."
    if missing:
        caption += f" {missing:,} without a loan type."
    st.caption(caption)

    rows = summary(data.loc[has_loan_type], "_LoanType").head(20)
    fig = ranked_bar(rows, "_LoanType")
    label_application_bars(fig, total, "of all applications")
    chart(fig, "application-breakdown")


def monthly_trend(data):
    st.subheader("Monthly portfolio trend")
    dated = data.dropna(subset=["_Date"]).copy()
    if dated.empty:
        st.info("No application dates are available for this view.")
        return

    measure = st.radio(
        "Trend metric",
        ["Portfolio value", "Applications"],
        horizontal=True,
        label_visibility="collapsed",
        key="trend_measure",
    )
    dated["Month"] = dated["_Date"].dt.to_period("M").dt.to_timestamp()
    monthly = summary(dated, "Month").sort_values("Month")
    if measure == "Portfolio value":
        column, tick_options = "Portfolio", {"tickprefix": "₹"}
        hover_values = monthly[column].map(money)
    else:
        column, tick_options = "Applications", {"tickformat": ",d"}
        hover_values = monthly[column].map(lambda value: f"{value:,} applications")
        if monthly[column].max() <= 5:
            tick_options["dtick"] = 1

    has_comparison = len(monthly) > 1
    fig = go.Figure(go.Scatter(
        x=monthly["Month"],
        y=monthly[column],
        name=measure,
        mode="lines" if has_comparison else "markers",
        line=dict(color=CHART_SAGE, width=1.8, shape="spline", smoothing=.75),
        marker=dict(size=7, color=CHART_SAGE),
        fill="tozeroy" if has_comparison else None,
        fillgradient=dict(
            type="vertical",
            colorscale=[[0, "rgba(184,203,189,0.02)"], [1, "rgba(184,203,189,0.17)"]],
        ),
        customdata=hover_values,
        hovertemplate="Monthly: %{customdata}<extra></extra>",
    ))
    if has_comparison:
        # Keep the three-calendar-month window even when a month has no records.
        values = monthly.set_index("Month")[column].asfreq("MS")
        average = values.rolling(3, min_periods=1).mean().reindex(monthly["Month"])
        average_hover = average.map(money if measure == "Portfolio value" else lambda value: f"{value:,.1f} applications")
        fig.add_scatter(
            x=monthly["Month"],
            y=average,
            name="3-month average",
            mode="lines",
            line=dict(color=CHART_MUTED_SAGE, width=1.4, dash="dot", shape="spline", smoothing=.75),
            customdata=average_hover,
            hovertemplate="3-month average: %{customdata}<extra></extra>",
        )
    fig.update_layout(
        hovermode="x unified",
        hoverdistance=-1,
        showlegend=has_comparison,
        legend=dict(orientation="h", x=0, xanchor="left", y=1.025, yanchor="bottom", font=dict(size=11)),
    )
    month_padding = pd.Timedelta(days=9)
    first_month, last_month = monthly["Month"].iloc[0], monthly["Month"].iloc[-1]
    fig.update_xaxes(
        title=None,
        tickformat="%b" if first_month.year == last_month.year else "%b %y",
        hoverformat="%b %Y",
        showgrid=True,
        range=[first_month - month_padding, last_month + month_padding],
        dtick="M1" if not has_comparison else None,
    )
    fig.update_yaxes(title=None, showgrid=True, rangemode="tozero", **tick_options)
    chart(fig, "monthly-portfolio-trend")


def status_chart(data):
    st.subheader("Application status")
    counts = data["_Status"].replace("", "Not specified").value_counts()
    if counts.empty:
        st.info("No records in this date range.")
        return

    statuses = counts.index.tolist()
    if st.session_state.get("status_focus") not in statuses:
        st.session_state.status_focus = statuses[0]
    selected = st.selectbox(
        "Status to highlight",
        statuses,
        key="status_focus",
        label_visibility="collapsed",
    )
    colors = [
        CHART_SAGE if status == selected else STATUS_RING_COLORS[index % len(STATUS_RING_COLORS)]
        for index, status in enumerate(statuses)
    ]
    fig = px.pie(names=statuses, values=counts.tolist(), hole=.84)
    fig.update_traces(
        sort=False,
        rotation=16,
        direction="clockwise",
        textinfo="none",
        marker=dict(colors=colors, line=dict(color=CHART_SURFACE, width=4 if len(statuses) > 1 else 0)),
        hovertemplate="<b>%{label}</b><br>%{value:,} applications<br>%{percent} of total<extra></extra>",
    )
    fig.update_layout(showlegend=False)

    percentage = f"{100 * counts[selected] / counts.sum():.1f}".removesuffix(".0")
    center_label = selected if len(selected) <= 21 else f"{selected[:20].rstrip()}…"
    fig.add_annotation(
        text=f"<b>{percentage}%</b>",
        x=.5,
        y=.5,
        yshift=9,
        showarrow=False,
        font=dict(size=32, color=CHART_SAGE),
    )
    fig.add_annotation(
        text=escape(center_label),
        x=.5,
        y=.5,
        yshift=-20,
        showarrow=False,
        font=dict(size=13, color=MUTED),
    )
    chart(fig, "application-status")


def open_portfolio(raw, *, demo=False):
    st.session_state.data, st.session_state.found = clean(raw)
    st.session_state.demo = demo
    st.session_state.page = "Overview"
    st.session_state.portfolio_navigation = "Overview"
    st.rerun()


def sample_portfolio():
    rng = Random(42)
    statuses = ["Disbursed"] * 156 + ["Pending"] * 64 + ["Other"] * 28
    dates = pd.date_range("2026-01-01", "2026-06-30")
    return pd.DataFrame(
        {
            "Application ID": f"DEMO-{index:03}",
            "Loan Amount": rng.randrange(250_000, 1_260_000, 10_000),
            "Loan Status": status,
            "Loan Type": rng.choice(("Home Loan", "Business Loan", "Loan Against Property", "Personal Loan")),
            "Bank Name": rng.choice(("Lender A", "Lender B", "Lender C", "Lender D")),
            "Sales Executive": rng.choice(("Executive A", "Executive B", "Executive C", "Executive D")),
            "Application Date": rng.choice(dates),
        }
        for index, status in enumerate(statuses, start=1)
    )


def upload():
    portfolio_header("Upload")
    upload_area, sample_area = st.columns([1.7, 1])
    with upload_area, panel("upload"):
        st.subheader("Upload your workbook")
        st.caption("Select an Excel file, then choose the worksheet with your loan applications.")
        file = st.file_uploader("Excel workbook", type=["xlsx", "xls"], label_visibility="collapsed")
        if file is not None:
            try:
                with pd.ExcelFile(io.BytesIO(file.getvalue())) as workbook:
                    sheet = st.selectbox("Worksheet", workbook.sheet_names)
                    raw = workbook.parse(sheet)
                st.caption(f"{len(raw):,} rows · {len(raw.columns)} columns")
                if st.button("Open dashboard", type="primary", use_container_width=True):
                    if raw.empty:
                        st.error("The selected worksheet is empty.")
                    else:
                        open_portfolio(raw)
            except Exception as exc:
                st.error(f"Unable to read workbook: {exc}")

    with sample_area, panel("sample"):
        st.subheader("Explore a sample portfolio")
        st.caption("Try the dashboard with 248 fictional loan applications.")
        if st.button("View sample dashboard", use_container_width=True):
            open_portfolio(sample_portfolio(), demo=True)

if st.session_state.data is None or st.session_state.page == "Upload":
    upload()
    st.stop()

st.sidebar.markdown("## Loan portfolio")
pages = ["Overview", "Loan Types", "Banks", "Executives", "Records", "KPI Metrics"]
page = st.sidebar.radio("Navigation", pages, key="portfolio_navigation")
st.session_state.page = page
if st.sidebar.button("Upload new data", use_container_width=True):
    st.session_state.page = "Upload"
    st.rerun()

data = st.session_state.data.copy()
portfolio_header(page)
if page == "Overview":
    if data["_Date"].notna().any():
        date_filter, _ = st.columns([1, 2])
        valid = data["_Date"].dropna()
        first_date, last_date = valid.min().date(), valid.max().date()
        dates = date_filter.date_input(
            "Application date range",
            value=(first_date, last_date),
            min_value=first_date,
            max_value=last_date,
            format="DD/MM/YYYY",
        )
        if isinstance(dates, (tuple, list)) and len(dates) == 2:
            data = data[data["_Date"].dt.date.between(dates[0], dates[1])]
    st.caption(f"Showing {len(data):,} of {len(st.session_state.data):,} records")

status = data["_Status"].str.lower()
disbursed = status.str.contains("disburs", na=False)
pending = status.str.contains("pending|processing|under review|in progress", regex=True, na=False)
if page == "Overview":
    a, b, c, d = st.columns(4)
    a.metric("Applications", f"{len(data):,}")
    b.metric("Portfolio Value", money(data["_Amount"].sum()))
    c.metric("Disbursed", f"{disbursed.sum():,}")
    d.metric("Pending", f"{pending.sum():,}")
    left, right = st.columns(2)
    with left, panel("trend"):
        monthly_trend(data)
    with right, panel("status"):
        status_chart(data)

    portfolio_status_panel, loan_amount_panel = st.columns(2)
    with portfolio_status_panel, panel("portfolio-status"):
        st.subheader("Portfolio value by status")
        by_status = summary(data, "_Status")
        if by_status.empty:
            st.info("No records in this date range.")
        else:
            chart(ranked_bar(by_status, "_Status", "Portfolio"), "portfolio-by-status")

    with loan_amount_panel, panel("loan-amount-bands"):
        st.subheader("Loan amount bands")
        loan_amount_chart(data)
    banks_panel, _ = st.columns([2, 2])
    with banks_panel, panel("top-banks"):
        st.subheader("Top banks")
        rows = summary(data, "_Bank").head(8)
        if rows.empty:
            st.info("No data to display.")
        else:
            chart(ranked_bar(rows, "_Bank"), "top-banks", height=270)
elif page in ["Loan Types", "Banks", "Executives"]:
    dimension, label = {"Loan Types": ("_LoanType", "Loan type"), "Banks": ("_Bank", "Bank"), "Executives": ("_Executive", "Executive")}[page]
    rows = summary(data, dimension)
    chart_column, totals_column = st.columns(2)
    with chart_column, panel("breakdown-chart"):
        st.subheader(f"Applications by {label.lower()}")
        if page == "Loan Types":
            loan_type_chart(data)
        elif rows.empty:
            st.info("No data to display.")
        else:
            chart(ranked_bar(rows.head(20), dimension), "application-breakdown")
    with totals_column, panel("breakdown-table"):
        st.subheader(f"{label} totals")
        st.dataframe(rows.rename(columns={dimension: label}), use_container_width=True, hide_index=True)
elif page == "Records":
    with panel("records"):
        search = st.text_input("Search records", placeholder="Search any column")
        display = data.drop(columns=[c for c in data.columns if c.startswith("_")], errors="ignore")
        if search:
            mask = display.astype(str).apply(lambda col: col.str.contains(search, case=False, regex=False, na=False)).any(axis=1)
            display = display[mask]
        st.caption(f"{len(display):,} matching records")
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", display.to_csv(index=False).encode("utf-8-sig"), file_name="loan_records.csv", mime="text/csv")
elif page == "KPI Metrics":
    total = len(data)
    a, b, c = st.columns(3)
    a.metric("Disbursement Rate", f"{100*disbursed.sum()/total:.1f}%" if total else "0.0%")
    b.metric("Average Loan Amount", money(data["_Amount"].mean()) if total else money(0))
    c.metric("Total Portfolio", money(data["_Amount"].sum()))
    with panel("kpi-table"):
        st.subheader("Application totals")
        st.dataframe(pd.DataFrame({"Metric": ["Total Applications", "Disbursed", "Pending"], "Count": [total, int(disbursed.sum()), int(pending.sum())]}), hide_index=True, use_container_width=True)
