import io
import re
from random import Random

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="JR Financial | Loan Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PINE = "#28674c"
INK = "#172820"
MUTED = "#506356"
LINE = "#dce5d8"
PAPER = "#fcfdf9"
STATUS_COLORS = {"Disbursed": PINE, "Pending": "#a5c75f", "Other": "#ccd9c8"}
PALETTE = [PINE, "#a5c75f", "#c28a44", "#72969b", "#a988a4"]

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(ellipse at 94% 0, #e0ebd9, transparent 37rem), #f0f4ed;
        color: #172820;
    }
    [data-testid="stHeader"] { background: #f0f4edf2; }
    .block-container { max-width: 1360px; padding-top: 4rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #fcfdf9; border-right: 1px solid #dce5d8; }
    .stApp h2, .stApp h3, .stApp h4 { color: #172820; letter-spacing: -.028em; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: #506356; }

    .jr-hero {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        margin-bottom: 1rem;
        padding: clamp(1.75rem, 4vw, 3.6rem);
        border-radius: 26px;
        background: radial-gradient(ellipse at 100% 8%, #304a29, transparent 61%), #0d2018;
        box-shadow: 0 14px 36px #102a171f;
        color: #f6f8ee;
    }
    .jr-hero::after {
        position: absolute;
        z-index: -1;
        inset: 0 0 0 auto;
        width: min(43%, 26rem);
        background: radial-gradient(circle, #d4ed9e55 1px, transparent 1.6px) 0 0 / 14px 14px;
        mask-image: linear-gradient(90deg, transparent, #0008);
        content: "";
    }
    .jr-brand { display: flex; align-items: center; gap: .7rem; font-size: 1rem; font-weight: 650; }
    .jr-monogram {
        display: inline-grid;
        width: 2.35rem;
        height: 2.35rem;
        place-items: center;
        border-radius: .65rem;
        background: #dbf894;
        color: #172820;
        font: bold 1.12rem Georgia, serif;
        letter-spacing: -.06em;
    }
    .jr-hero h1 {
        margin: .85rem 0 .65rem;
        padding: 0;
        color: #f6f8ee;
        font-size: clamp(2.5rem, 6vw, 5.5rem);
        line-height: .99;
        font-weight: 750;
        letter-spacing: -.045em;
    }
    .jr-hero .jr-accent { color: #dbf894; }
    .jr-hero p { max-width: 37rem; margin: 0; color: #d8e5d6; font-size: clamp(1rem, 1.8vw, 1.19rem); }
    .jr-hero--compact { padding-block: 1.8rem 2rem; }
    .jr-hero--compact h1 { font-size: clamp(2.15rem, 4vw, 4rem); }
    .jr-tag {
        display: inline-block;
        margin-top: .9rem;
        padding: .2rem .65rem;
        border: 1px solid #d4ed9e66;
        border-radius: 999px;
        color: #e5f7bb;
        font-size: .85rem;
        font-weight: 650;
    }
    [data-testid="stMetric"], [data-testid="stPlotlyChart"] {
        background: #fcfdf9;
        border: 1px solid #dce5d8;
        border-radius: 16px;
        box-shadow: 0 4px 16px #102a1708;
    }
    [data-testid="stMetric"] { height: 100%; padding: 1rem; }
    [data-testid="stMetricLabel"] p { color: #506356; }
    [data-testid="stMetricValue"] { color: #172820; font-weight: 680; }
    [data-testid="stPlotlyChart"] { padding: .5rem; }
    [data-testid="stFileUploaderDropzone"] { background: #e6efe2; border: 1px dashed #9db39f; }
    [data-testid="stWidgetLabel"] p, [data-testid="stFileUploaderDropzone"] { color: #172820; }
    button[data-testid="stBaseButton-primary"] { background: #28674c; border-color: #28674c; color: #fff; }
    button[data-testid="stBaseButton-primary"]:hover { background: #1a4f38; border-color: #1a4f38; color: #fff; }

    @media (max-width: 640px) {
        .block-container { padding-top: 3rem; }
        .jr-hero { border-radius: 18px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "data" not in st.session_state:
    st.session_state.data = None
if "page" not in st.session_state:
    st.session_state.page = "Upload"


def portfolio_header(overview=False):
    title, accent = ("Portfolio", "overview.") if overview else ("Loan portfolio", "dashboard.")
    description = (
        "Monitor application status, disbursements, and monthly portfolio value."
        if overview
        else "Upload an Excel workbook to track applications, compare lenders, and see how your portfolio changes over time."
    )
    variant = " jr-hero--compact" if overview else ""
    tag = '<span class="jr-tag">Sample data</span>' if overview and st.session_state.get("demo") else ""
    st.markdown(
        f"""
        <header class="jr-hero{variant}">
          <div class="jr-brand"><span class="jr-monogram" aria-hidden="true">JR</span> JR Financial</div>
          <h1>{title} <span class="jr-accent">{accent}</span></h1>
          <p>{description}</p>
          {tag}
        </header>
        """,
        unsafe_allow_html=True,
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

def chart(fig, height=320):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=16, r=20, t=20, b=20),
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(color=INK, size=13),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.08, yanchor="top"),
        hoverlabel=dict(bgcolor=PAPER, font_color=INK),
    )
    fig.update_xaxes(gridcolor=LINE, tickfont=dict(color=MUTED), automargin=True)
    fig.update_yaxes(gridcolor=LINE, tickfont=dict(color=MUTED), automargin=True)
    st.plotly_chart(fig, use_container_width=True, theme=None, config={"displaylogo": False})

def summary(data, key):
    return data.groupby(key, dropna=False).agg(Applications=("_Amount", "size"), Portfolio=("_Amount", "sum")).reset_index().sort_values("Applications", ascending=False)

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
    portfolio_header()
    upload_area, sample_area = st.columns([1.7, 1])
    with upload_area, st.container(border=True):
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

    with sample_area, st.container(border=True):
        st.subheader("Explore a sample portfolio")
        st.caption("Try the dashboard with 248 fictional loan applications.")
        if st.button("View sample dashboard", use_container_width=True):
            open_portfolio(sample_portfolio(), demo=True)

if st.session_state.data is None or st.session_state.page == "Upload":
    upload()
    st.stop()

st.sidebar.markdown("## JR Financial")
st.sidebar.caption("Loan portfolio analytics")
if st.session_state.get("demo"):
    st.sidebar.caption("Sample data")
pages = ["Overview", "Loan Types", "Banks", "Executives", "Records", "KPI Metrics"]
page = st.sidebar.radio("Navigation", pages, key="portfolio_navigation")
st.session_state.page = page
if st.sidebar.button("Upload new data", use_container_width=True):
    st.session_state.page = "Upload"
    st.rerun()

data = st.session_state.data.copy()
if page == "Overview":
    portfolio_header(overview=True)
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
else:
    st.markdown(f"## {page}")

status = data["_Status"].str.lower()
disbursed = status.str.contains("disburs", na=False)
pending = status.str.contains("pending|processing|under review|in progress", regex=True, na=False)
if page == "Overview":
    a, b, c, d = st.columns(4)
    a.metric("Applications", f"{len(data):,}")
    b.metric("Portfolio Value", money(data["_Amount"].sum()))
    c.metric("Disbursed", f"{disbursed.sum():,}")
    d.metric("Pending", f"{pending.sum():,}")
    left, right = st.columns([1, 1.2])
    with left:
        st.markdown("#### Application Status")
        counts = data["_Status"].value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        if not counts.empty:
            fig = px.pie(
                counts,
                names="Status",
                values="Count",
                color="Status",
                hole=.7,
                color_discrete_map=STATUS_COLORS,
                color_discrete_sequence=PALETTE,
            )
            fig.update_traces(textinfo="none", marker=dict(line=dict(color=PAPER, width=2)))
            fig.add_annotation(text=f"<b>{len(data):,}</b><br>Applications", x=.5, y=.5, showarrow=False)
            chart(fig)
        else:
            st.info("No records in this date range.")
    with right:
        st.markdown("#### Portfolio by Status")
        s = summary(data, "_Status").sort_values("Portfolio")
        if not s.empty:
            fig = px.bar(s, x="Portfolio", y="_Status", orientation="h", color_discrete_sequence=[PINE])
            fig.update_layout(yaxis_title="", xaxis_title="Amount (₹)")
            chart(fig)
        else:
            st.info("No records in this date range.")
    st.markdown("#### Monthly Portfolio Trend")
    dated = data.dropna(subset=["_Date"]).copy()
    if not dated.empty:
        dated["Month"] = dated["_Date"].dt.to_period("M").astype(str)
        monthly = dated.groupby("Month").agg(Applications=("_Amount", "size"), Portfolio=("_Amount", "sum")).reset_index()
        fig = px.area(monthly, x="Month", y="Portfolio", markers=True, color_discrete_sequence=[PINE])
        fig.update_traces(fillcolor="#dcebcf", line_width=3)
        fig.update_layout(yaxis_title="Amount (₹)")
        chart(fig, 310)
    else:
        st.info("No valid application dates found for monthly trends.")
    x, y = st.columns(2)
    for col, key, title, color in [(x, "_LoanType", "Loan Types", PINE), (y, "_Bank", "Top Banks", "#69893b")]:
        with col:
            st.markdown(f"#### {title}")
            s = summary(data, key).head(8).sort_values("Applications")
            if not s.empty:
                fig = px.bar(s, x="Applications", y=key, orientation="h", color_discrete_sequence=[color])
                fig.update_layout(yaxis_title="")
                chart(fig)
            else:
                st.info("No data to display.")
elif page in ["Loan Types", "Banks", "Executives"]:
    key = {"Loan Types": "_LoanType", "Banks": "_Bank", "Executives": "_Executive"}[page]
    s = summary(data, key)
    if not s.empty:
        fig = px.bar(s.head(20).sort_values("Applications"), x="Applications", y=key, orientation="h", color_discrete_sequence=[PINE])
        fig.update_layout(yaxis_title="")
        chart(fig, 450)
    st.dataframe(s.rename(columns={key: page[:-1] if page.endswith("s") else page}), use_container_width=True, hide_index=True)
elif page == "Records":
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
    st.dataframe(pd.DataFrame({"Metric": ["Total Applications", "Disbursed", "Pending"], "Count": [total, int(disbursed.sum()), int(pending.sum())]}), hide_index=True, use_container_width=True)
