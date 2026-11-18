from __future__ import annotations

from io import BytesIO
import re

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="MarketPulse | Business Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = {
    "navy": "#142b4a",
    "blue": "#4779db",
    "teal": "#14a58a",
    "purple": "#8666d8",
    "amber": "#efa942",
    "muted": "#718096",
    "line": "#e6ebf2",
    "canvas": "#f5f7fb",
}

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      :root {{ --ink:{PALETTE['navy']}; --muted:{PALETTE['muted']}; --line:{PALETTE['line']}; }}
      html, body, [class*="css"] {{ font-family:'DM Sans',sans-serif; }}
      .stApp {{ background:{PALETTE['canvas']}; color:var(--ink); }}
      [data-testid="stHeader"] {{ background:rgba(245,247,251,.82); }}
      [data-testid="stSidebar"] {{ background:#fff; border-right:1px solid var(--line); }}
      [data-testid="stSidebar"] > div {{ padding-top:1.25rem; }}
      .block-container {{ max-width:1540px; padding-top:1.65rem; padding-bottom:3rem; }}
      .brand-row {{ display:flex; align-items:center; gap:12px; margin:0 0 1.35rem; }}
      .brand-mark {{ display:grid; place-items:center; width:43px; height:43px; border-radius:14px; color:white; font-size:20px; background:linear-gradient(145deg,{PALETTE['blue']},{PALETTE['teal']}); box-shadow:0 7px 18px #4779db35; }}
      .brand-copy b {{ display:block; color:{PALETTE['navy']}; font:800 16px/1.15 Manrope,sans-serif; }}
      .brand-copy small {{ display:block; margin-top:4px; color:{PALETTE['muted']}; font-size:10px; letter-spacing:1.15px; font-weight:700; }}
      .hero {{ position:relative; overflow:hidden; padding:26px 30px; margin:0 0 22px; border:1px solid #dce6f5; border-radius:20px; background:linear-gradient(115deg,#fff 0%,#f3f7ff 56%,#eefaf7 100%); box-shadow:0 8px 26px #1b34520a; }}
      .hero:after {{ position:absolute; content:''; width:250px; height:250px; right:-85px; top:-145px; border-radius:50%; background:radial-gradient(circle,#86aef333,transparent 68%); }}
      .hero-kicker {{ color:{PALETTE['blue']}; font-size:10px; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; }}
      .hero h1 {{ margin:8px 0 5px; color:{PALETTE['navy']}; font:800 clamp(25px,3vw,36px)/1.16 Manrope,sans-serif; letter-spacing:-1.1px; }}
      .hero p {{ margin:0; color:#62748b; font-size:14px; }}
      .hero-badge {{ position:absolute; z-index:1; right:26px; bottom:22px; padding:7px 11px; border:1px solid #d5e5dd; border-radius:999px; background:#f3fbf7; color:#177a63; font-size:10px; font-weight:700; }}
      [data-testid="stMetric"] {{ min-height:124px; padding:17px 18px; border:1px solid var(--line); border-radius:15px; background:#fff; box-shadow:0 4px 15px #243b5308; }}
      [data-testid="stMetricLabel"] p {{ color:#65768c; font-size:12px; font-weight:600; }}
      [data-testid="stMetricValue"] {{ color:{PALETTE['navy']}; font:800 clamp(22px,2vw,29px) Manrope,sans-serif; letter-spacing:-.6px; }}
      [data-testid="stMetricDelta"] {{ font-size:11px; }}
      .section-title {{ margin:4px 0 12px; color:{PALETTE['navy']}; font:750 16px Manrope,sans-serif; }}
      .section-note {{ margin-top:-8px; margin-bottom:10px; color:{PALETTE['muted']}; font-size:11px; }}
      .chart-card {{ padding:17px 17px 8px; border:1px solid var(--line); border-radius:16px; background:#fff; box-shadow:0 4px 15px #243b5308; }}
      .stButton button, .stDownloadButton button {{ border-radius:10px; font-weight:650; }}
      [data-testid="stDataFrame"] {{ border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
      .source-note {{ color:#8491a2; font-size:10px; }}
      @media (max-width:760px) {{ .hero {{ padding:22px 20px; }} .hero-badge {{ position:static; display:inline-block; margin-top:13px; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def make_demo_data() -> pd.DataFrame:
    """Return deterministic portfolio data so the dashboard works immediately."""
    rng = np.random.default_rng(24)
    rows = 720
    products = {
        "Analytics Suite": "Software",
        "Cloud Workspace": "Software",
        "Advisory Package": "Services",
        "Implementation": "Services",
        "Team License": "Subscriptions",
        "Data Connectors": "Subscriptions",
    }
    product_names = list(products)
    product = rng.choice(product_names, size=rows, p=[.19, .15, .16, .14, .21, .15])
    category = [products[name] for name in product]
    unit_price = np.array([{"Analytics Suite": 62000, "Cloud Workspace": 38000,
                            "Advisory Package": 94000, "Implementation": 115000,
                            "Team License": 26000, "Data Connectors": 18000}[name]
                           for name in product])
    quantity = rng.integers(1, 7, size=rows)
    sales = (unit_price * quantity * rng.uniform(.82, 1.22, size=rows)).round(0)
    profit = (sales * rng.uniform(.12, .36, size=rows)).round(0)
    dates = rng.choice(pd.date_range(end=pd.Timestamp.today().normalize(), periods=365, freq="D"), size=rows)
    regions = rng.choice(["West", "South", "North", "East", "Central"], size=rows, p=[.28, .24, .2, .16, .12])
    segments = rng.choice(["Enterprise", "Mid-market", "Small business"], size=rows, p=[.3, .42, .28])
    return pd.DataFrame({
        "Order ID": [f"MP-{i:05d}" for i in range(1, rows + 1)],
        "Order Date": pd.to_datetime(dates),
        "Region": regions,
        "Category": category,
        "Product": product,
        "Customer Segment": segments,
        "Quantity": quantity,
        "Sales": sales,
        "Profit": profit,
    }).sort_values("Order Date", ascending=False).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def read_uploaded_file(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    source = BytesIO(file_bytes)
    if file_name.lower().endswith(".csv"):
        return pd.read_csv(source)
    return pd.read_excel(source)


def normalized_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def guess_column(columns: list[object], aliases: tuple[str, ...]) -> object | None:
    names = {normalized_name(column): column for column in columns}
    for alias in aliases:
        if normalized_name(alias) in names:
            return names[normalized_name(alias)]
    for alias in aliases:
        match = next((column for column in columns if normalized_name(alias) in normalized_name(column)), None)
        if match is not None:
            return match
    return None


def format_amount(value: float, symbol: str) -> str:
    amount = float(value or 0)
    magnitude = abs(amount)
    if magnitude >= 10_000_000:
        return f"{symbol}{amount / 10_000_000:,.1f} Cr"
    if magnitude >= 100_000:
        return f"{symbol}{amount / 100_000:,.1f} L"
    if magnitude >= 1_000:
        return f"{symbol}{amount:,.0f}"
    return f"{symbol}{amount:,.2f}"


with st.sidebar:
    st.markdown(
        '<div class="brand-row"><div class="brand-mark">↗</div><div class="brand-copy"><b>MarketPulse</b><small>BUSINESS ANALYTICS</small></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Build your view")
    uploaded_file = st.file_uploader("Upload a dataset", type=["csv", "xlsx"], help="CSV and Excel workbooks are supported.")
    currency = st.selectbox("Currency display", ["₹", "$", "€", "£"], index=0)
    st.caption("No file? The demo dataset loads automatically.")
    st.divider()


if uploaded_file is None:
    raw_data = make_demo_data()
    source_label = "Sample portfolio dataset"
else:
    try:
        raw_data = read_uploaded_file(uploaded_file.name, uploaded_file.getvalue())
        source_label = uploaded_file.name
    except Exception as exc:
        st.error(f"Could not read this file: {exc}")
        st.stop()

if raw_data.empty or len(raw_data.columns) == 0:
    st.warning("This dataset is empty. Upload a file containing column headers and data rows.")
    st.stop()

columns = list(raw_data.columns)
numeric_columns = list(raw_data.select_dtypes(include="number").columns)
if not numeric_columns:
    for column in columns:
        if raw_data[column].dtype == "object":
            candidate = pd.to_numeric(raw_data[column].astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")
            if candidate.notna().mean() >= .8:
                raw_data[column] = candidate
                numeric_columns.append(column)

date_columns: list[object] = []
for column in columns:
    series = raw_data[column]
    if pd.api.types.is_datetime64_any_dtype(series):
        date_columns.append(column)
    elif not pd.api.types.is_numeric_dtype(series):
        parsed = pd.to_datetime(series, errors="coerce")
        if parsed.notna().mean() >= .7 and parsed.nunique() > 2:
            date_columns.append(column)

if not numeric_columns:
    st.error("I couldn’t find a numeric column to analyze. Add a sales, revenue, amount, or other numeric field.")
    st.stop()

dimension_columns = [
    column for column in columns
    if column not in numeric_columns and column not in date_columns
    and 1 < raw_data[column].nunique(dropna=True) <= 100
]

with st.sidebar:
    st.markdown("### Map your columns")
    date_guess = guess_column(columns, ("date", "order date", "invoice date", "created at"))
    amount_guess = guess_column(numeric_columns, ("sales", "revenue", "amount", "loan amount", "value"))
    profit_guess = guess_column(numeric_columns, ("profit", "margin", "net income"))
    category_guess = guess_column(dimension_columns, ("category", "product type", "type"))
    region_guess = guess_column(dimension_columns, ("region", "state", "territory", "city"))

    date_options = ["(No date field)"] + [str(column) for column in date_columns]
    date_default = date_options.index(str(date_guess)) if date_guess is not None and str(date_guess) in date_options else 0
    date_choice = st.selectbox("Date column", date_options, index=date_default)
    amount_options = [str(column) for column in numeric_columns]
    amount_default = amount_options.index(str(amount_guess)) if amount_guess is not None and str(amount_guess) in amount_options else 0
    amount_column = st.selectbox("Value column", amount_options, index=amount_default)
    profit_options = ["(No profit field)"] + [str(column) for column in numeric_columns if str(column) != amount_column]
    profit_default = profit_options.index(str(profit_guess)) if profit_guess is not None and str(profit_guess) in profit_options else 0
    profit_choice = st.selectbox("Profit / comparison column", profit_options, index=profit_default)

    dimension_options = ["(No breakdown)"] + [str(column) for column in dimension_columns]
    category_default = dimension_options.index(str(category_guess)) if category_guess is not None and str(category_guess) in dimension_options else 0
    dimension_choice = st.selectbox("Primary breakdown", dimension_options, index=category_default)
    region_default = dimension_options.index(str(region_guess)) if region_guess is not None and str(region_guess) in dimension_options else 0
    segment_choice = st.selectbox("Secondary breakdown", dimension_options, index=region_default)

date_column = None if date_choice == "(No date field)" else date_choice
profit_column = None if profit_choice == "(No profit field)" else profit_choice
dimension_column = None if dimension_choice == "(No breakdown)" else dimension_choice
segment_column = None if segment_choice == "(No breakdown)" else segment_choice

data = raw_data.copy()
data[amount_column] = pd.to_numeric(data[amount_column], errors="coerce")
if profit_column:
    data[profit_column] = pd.to_numeric(data[profit_column], errors="coerce")
if date_column:
    data["_dashboard_date"] = pd.to_datetime(data[date_column], errors="coerce")

with st.sidebar:
    st.markdown("### Filters")
    filtered = data.copy()
    if date_column and filtered["_dashboard_date"].notna().any():
        min_date = filtered["_dashboard_date"].min().date()
        max_date = filtered["_dashboard_date"].max().date()
        selected_dates = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            filtered = filtered[
                filtered["_dashboard_date"].dt.date.between(start_date, end_date)
            ]
    for label, column in (("Primary filter", dimension_column), ("Secondary filter", segment_column)):
        if column:
            options = sorted(filtered[column].dropna().astype(str).unique().tolist())
            selected = st.multiselect(label, options, default=options, key=f"filter_{normalized_name(column)}")
            if selected:
                filtered = filtered[filtered[column].astype(str).isin(selected)]
            else:
                filtered = filtered.iloc[0:0]

    st.divider()
    st.caption("MarketPulse · interactive analytics portfolio demo")

filtered = filtered.dropna(subset=[amount_column]).copy()

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">Portfolio project · Live data exploration</div>
      <h1>Business performance, at a glance.</h1>
      <p>Explore revenue, product mix, profitability, and regional trends in one interactive workspace.</p>
      <span class="hero-badge">●&nbsp; {len(filtered):,} records in view</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.info("No records match these filters. Adjust the sidebar filters to continue.")
    st.stop()

total_value = float(filtered[amount_column].sum())
average_value = float(filtered[amount_column].mean())
record_count = len(filtered)
unique_customers = filtered[segment_column].nunique() if segment_column else filtered[dimension_column].nunique() if dimension_column else record_count
total_profit = float(filtered[profit_column].sum()) if profit_column else None
margin = (total_profit / total_value * 100) if total_profit is not None and total_value else None

metric_columns = st.columns(4)
metric_columns[0].metric("Total value", format_amount(total_value, currency), help=f"Sum of {amount_column}")
metric_columns[1].metric("Records", f"{record_count:,}", help="Rows matching the selected filters")
metric_columns[2].metric("Average value", format_amount(average_value, currency), help=f"Average {amount_column} per record")
metric_columns[3].metric("Profit margin" if margin is not None else "Unique groups", f"{margin:.1f}%" if margin is not None else f"{unique_customers:,}", help="Profit divided by value" if margin is not None else "Distinct values in your selected breakdown")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
left_chart, right_chart = st.columns([1.55, 1], gap="medium")

with left_chart:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Value trend</div>', unsafe_allow_html=True)
    if date_column and filtered["_dashboard_date"].notna().any():
        trend_data = filtered.dropna(subset=["_dashboard_date"]).copy()
        trend_data["Period"] = trend_data["_dashboard_date"].dt.to_period("M").dt.to_timestamp()
        trend = trend_data.groupby("Period", as_index=False)[amount_column].sum().sort_values("Period")
        trend_fig = px.area(trend, x="Period", y=amount_column, color_discrete_sequence=[PALETTE["blue"]])
        trend_fig.update_traces(line={"width": 3}, fillcolor="rgba(71,121,219,.13)", hovertemplate="%{x|%b %Y}<br>Value: %{y:,.0f}<extra></extra>")
        trend_fig.update_layout(xaxis_title=None, yaxis_title=None, hovermode="x unified")
        trend_fig.update_yaxes(tickprefix=currency, separatethousands=True, gridcolor="#edf1f6", zeroline=False)
        trend_fig.update_xaxes(showgrid=False, tickformat="%b '%y")
    else:
        trend_fig = px.histogram(filtered, x=amount_column, nbins=18, color_discrete_sequence=[PALETTE["blue"]])
        trend_fig.update_layout(xaxis_title=amount_column, yaxis_title="Records")
        trend_fig.update_xaxes(tickprefix=currency, separatethousands=True, gridcolor="#edf1f6")
    trend_fig.update_layout(height=300, margin={"l": 8, "r": 8, "t": 8, "b": 5}, plot_bgcolor="white", paper_bgcolor="white", font={"family": "DM Sans", "color": "#65768c"}, showlegend=False)
    st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with right_chart:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Value by {dimension_column or "record"}</div>', unsafe_allow_html=True)
    if dimension_column:
        breakdown = filtered.groupby(dimension_column, dropna=False)[amount_column].sum().sort_values(ascending=True).tail(8).reset_index()
        breakdown[dimension_column] = breakdown[dimension_column].fillna("Unspecified").astype(str)
        bar_fig = px.bar(breakdown, x=amount_column, y=dimension_column, orientation="h", color=amount_column, color_continuous_scale=["#dce8ff", PALETTE["blue"]])
        bar_fig.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
        bar_fig.update_xaxes(tickprefix=currency, separatethousands=True, gridcolor="#edf1f6", zeroline=False)
    else:
        bar_fig = px.histogram(filtered, x=amount_column, nbins=12, color_discrete_sequence=[PALETTE["teal"]])
        bar_fig.update_layout(xaxis_title=amount_column, yaxis_title="Records")
    bar_fig.update_layout(height=300, margin={"l": 8, "r": 8, "t": 8, "b": 5}, plot_bgcolor="white", paper_bgcolor="white", font={"family": "DM Sans", "color": "#65768c"})
    st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
lower_left, lower_right = st.columns([1.05, 1], gap="medium")

with lower_left:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Portfolio composition</div>", unsafe_allow_html=True)
    donut_dimension = segment_column or dimension_column
    if donut_dimension:
        composition = filtered.groupby(donut_dimension, dropna=False)[amount_column].sum().reset_index()
        composition[donut_dimension] = composition[donut_dimension].fillna("Unspecified").astype(str)
        donut_fig = px.pie(composition, names=donut_dimension, values=amount_column, hole=.68, color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"], PALETTE["purple"], PALETTE["amber"], "#58b8c8", "#e97991"])
        donut_fig.update_traces(textposition="inside", textinfo="percent", marker={"line": {"color": "white", "width": 3}}, hovertemplate="%{label}<br>Value: %{value:,.0f}<extra></extra>")
        donut_fig.update_layout(height=290, margin={"l": 5, "r": 5, "t": 5, "b": 5}, paper_bgcolor="white", font={"family": "DM Sans", "color": "#65768c"}, legend={"orientation": "h", "y": -0.05, "x": .5, "xanchor": "center"}, showlegend=composition[donut_dimension].nunique() <= 8)
        st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Choose a text column in the sidebar to see portfolio composition.")
    st.markdown("</div>", unsafe_allow_html=True)

with lower_right:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Profitability by period</div>", unsafe_allow_html=True)
    if profit_column and date_column and filtered["_dashboard_date"].notna().any():
        profit_data = filtered.dropna(subset=["_dashboard_date", profit_column]).copy()
        profit_data["Period"] = profit_data["_dashboard_date"].dt.to_period("M").dt.to_timestamp()
        monthly_profit = profit_data.groupby("Period", as_index=False)[[amount_column, profit_column]].sum().sort_values("Period")
        profit_fig = px.bar(monthly_profit, x="Period", y=[amount_column, profit_column], barmode="group", color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"]])
        profit_fig.update_layout(xaxis_title=None, yaxis_title=None, legend_title=None, legend={"orientation": "h", "y": 1.12, "x": 0})
        profit_fig.update_yaxes(tickprefix=currency, separatethousands=True, gridcolor="#edf1f6", zeroline=False)
        profit_fig.update_xaxes(showgrid=False, tickformat="%b '%y")
        profit_fig.update_layout(height=290, margin={"l": 8, "r": 8, "t": 20, "b": 5}, plot_bgcolor="white", paper_bgcolor="white", font={"family": "DM Sans", "color": "#65768c"})
        st.plotly_chart(profit_fig, use_container_width=True, config={"displayModeBar": False})
    elif profit_column:
        profit_fig = px.scatter(filtered, x=amount_column, y=profit_column, color=dimension_column if dimension_column else None, color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"], PALETTE["purple"]], opacity=.75)
        profit_fig.update_layout(xaxis_title=amount_column, yaxis_title=profit_column, legend_title=None)
        profit_fig.update_xaxes(tickprefix=currency, separatethousands=True, gridcolor="#edf1f6")
        profit_fig.update_yaxes(tickprefix=currency, separatethousands=True, gridcolor="#edf1f6")
        profit_fig.update_layout(height=290, margin={"l": 8, "r": 8, "t": 15, "b": 5}, plot_bgcolor="white", paper_bgcolor="white", font={"family": "DM Sans", "color": "#65768c"})
        st.plotly_chart(profit_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Map a profit or comparison column to unlock profitability analysis.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
table_header, table_download = st.columns([1, 0.2], vertical_alignment="center")
with table_header:
    st.markdown('<div class="section-title">Filtered records</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-note">Showing {len(filtered):,} of {len(raw_data):,} rows from {source_label}</div>', unsafe_allow_html=True)
with table_download:
    csv_bytes = filtered.drop(columns=["_dashboard_date"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv_bytes, file_name="marketpulse_filtered_data.csv", mime="text/csv", use_container_width=True)

display_data = filtered.drop(columns=["_dashboard_date"], errors="ignore").copy()
if date_column:
    display_data[date_column] = pd.to_datetime(display_data[date_column], errors="coerce").dt.strftime("%d %b %Y")
st.dataframe(display_data, use_container_width=True, hide_index=True, height=370)
st.markdown('<p class="source-note">MarketPulse is a portfolio demo. Sample records are synthetic; uploaded data stays in the current app session.</p>', unsafe_allow_html=True)
