import io
import re
import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="JR Financial | Loan Portfolio", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
BLUE, NAVY, TEAL, ORANGE, PURPLE = "#315CF5", "#14213D", "#25B98A", "#F5A623", "#8057E8"
st.markdown("""<style>
.stApp{background:#f5f7fc}.block-container{padding-top:3.4rem;padding-bottom:2rem;max-width:1500px}
[data-testid="stSidebar"]{background:white;border-right:1px solid #e9edf5}
h1,h2,h3{color:#14213d}div[data-testid="stMetric"]{background:white;padding:19px;border:1px solid #e9edf5;border-radius:16px;box-shadow:0 3px 12px #14213d08}
[data-testid="stPlotlyChart"],div[data-testid="stDataFrame"]{background:white;border:1px solid #e9edf5;border-radius:16px;padding:10px}
[data-testid="stFileUploader"]{background:white;border-radius:14px;padding:12px}
</style>""", unsafe_allow_html=True)

if "data" not in st.session_state:
    st.session_state.data = None
if "page" not in st.session_state:
    st.session_state.page = "Upload"

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

def chart(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=12, r=12, t=22, b=15), paper_bgcolor="white", plot_bgcolor="white", font=dict(color=NAVY), legend=dict(orientation="h", y=1.13))
    st.plotly_chart(fig, use_container_width=True)

def summary(data, key):
    return data.groupby(key, dropna=False).agg(Applications=("_Amount", "size"), Portfolio=("_Amount", "sum")).reset_index().sort_values("Applications", ascending=False)

def upload():
    st.markdown("<div style='text-align:center;color:#315cf5;font-size:12px;letter-spacing:4px;font-weight:700'>JR FINANCIAL</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;font-size:clamp(30px,5vw,52px);margin-bottom:30px'>Loan Portfolio <span style='color:#315cf5'>Dashboard</span></h1>", unsafe_allow_html=True)
    _, middle, _ = st.columns([1, 1.7, 1])
    with middle:
        file = st.file_uploader("Upload XLSX or XLS workbook", type=["xlsx", "xls"])
        if file is not None:
            try:
                content = file.getvalue()
                workbook = pd.ExcelFile(io.BytesIO(content))
                sheet = st.selectbox("Worksheet", workbook.sheet_names)
                raw = pd.read_excel(io.BytesIO(content), sheet_name=sheet)
                st.caption(f"{len(raw):,} rows · {len(raw.columns)} columns")
                if st.button("Open Dashboard", type="primary", use_container_width=True):
                    if raw.empty:
                        st.error("The selected worksheet is empty.")
                    else:
                        st.session_state.data, st.session_state.found = clean(raw)
                        st.session_state.page = "Overview"
                        st.rerun()
            except Exception as exc:
                st.error(f"Unable to read workbook: {exc}")

if st.session_state.data is None or st.session_state.page == "Upload":
    upload()
    st.stop()

st.sidebar.markdown("## JR Financial")
st.sidebar.caption("LOAN PORTFOLIO ANALYTICS")
pages = ["Overview", "Loan Types", "Banks", "Executives", "Records", "KPI Metrics"]
page = st.sidebar.radio("Navigation", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
st.session_state.page = page
if st.sidebar.button("＋ Upload New Data", use_container_width=True):
    st.session_state.page = "Upload"
    st.rerun()

data = st.session_state.data.copy()
if page == "Overview":
    left, right = st.columns([2.5, 1.25], vertical_alignment="top")
    with left:
        st.markdown("## Dashboard Overview")
    with right:
        if data["_Date"].notna().any():
            valid = data["_Date"].dropna()
            dates = st.date_input("Date range", value=(valid.min().date(), valid.max().date()), min_value=valid.min().date(), max_value=valid.max().date(), format="DD/MM/YYYY")
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
            fig = px.pie(counts, names="Status", values="Count", hole=.65, color_discrete_sequence=[BLUE, TEAL, ORANGE, PURPLE, "#ef6464"])
            fig.add_annotation(text=f"<b>{len(data):,}</b><br>Applications", x=.5, y=.5, showarrow=False)
            chart(fig)
        else:
            st.info("No records in this date range.")
    with right:
        st.markdown("#### Portfolio by Status")
        s = summary(data, "_Status").sort_values("Portfolio")
        if not s.empty:
            fig = px.bar(s, x="Portfolio", y="_Status", orientation="h", color_discrete_sequence=[BLUE])
            fig.update_layout(yaxis_title="", xaxis_title="Amount (₹)")
            chart(fig)
        else:
            st.info("No records in this date range.")
    st.markdown("#### Monthly Portfolio Trend")
    dated = data.dropna(subset=["_Date"]).copy()
    if not dated.empty:
        dated["Month"] = dated["_Date"].dt.to_period("M").astype(str)
        monthly = dated.groupby("Month").agg(Applications=("_Amount", "size"), Portfolio=("_Amount", "sum")).reset_index()
        fig = px.area(monthly, x="Month", y="Portfolio", markers=True, color_discrete_sequence=[BLUE])
        chart(fig, 310)
    else:
        st.info("No valid application dates found for monthly trends.")
    x, y = st.columns(2)
    for col, key, title, color in [(x, "_LoanType", "Loan Types", BLUE), (y, "_Bank", "Top Banks", TEAL)]:
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
        fig = px.bar(s.head(20).sort_values("Applications"), x="Applications", y=key, orientation="h", color_discrete_sequence=[BLUE])
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
