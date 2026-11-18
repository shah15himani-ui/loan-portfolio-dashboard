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
SEQUENCE = [PALETTE["blue"], PALETTE["teal"], PALETTE["purple"], PALETTE["amber"], "#58b8c8", "#e97991"]
NONE_DATE = "(No date field)"
NONE_PROFIT = "(No profit field)"
NONE_DIM = "(No breakdown)"

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
      .hero {{ position:relative; overflow:hidden; padding:26px 30px; margin:0 0 18px; border:1px solid #dce6f5; border-radius:20px; background:linear-gradient(115deg,#fff 0%,#f3f7ff 56%,#eefaf7 100%); box-shadow:0 8px 26px #1b34520a; }}
      .hero:after {{ position:absolute; content:''; width:250px; height:250px; right:-85px; top:-145px; border-radius:50%; background:radial-gradient(circle,#86aef333,transparent 68%); }}
      .hero-kicker {{ color:{PALETTE['blue']}; font-size:10px; font-weight:800; letter-spacing:1.5px; text-transform:uppercase; }}
      .hero h1 {{ margin:8px 0 5px; color:{PALETTE['navy']}; font:800 clamp(25px,3vw,36px)/1.16 Manrope,sans-serif; letter-spacing:-1.1px; }}
      .hero p {{ margin:0; color:#62748b; font-size:14px; }}
      .hero-badge {{ position:absolute; z-index:1; right:26px; bottom:22px; padding:7px 11px; border:1px solid #d5e5dd; border-radius:999px; background:#f3fbf7; color:#177a63; font-size:10px; font-weight:700; }}
      .chip {{ display:inline-block; margin:0 8px 8px 0; padding:6px 12px; border-radius:999px; background:#eaf1ff; color:{PALETTE['blue']}; font-size:12px; font-weight:700; border:1px solid #cfdcf7; }}
      [data-testid="stMetric"] {{ min-height:124px; padding:17px 18px; border:1px solid var(--line); border-radius:15px; background:#fff; box-shadow:0 4px 15px #243b5308; transition:transform .15s ease, box-shadow .15s ease; }}
      [data-testid="stMetric"]:hover {{ transform:translateY(-3px); box-shadow:0 10px 24px #243b5316; }}
      [data-testid="stMetricLabel"] p {{ color:#65768c; font-size:12px; font-weight:600; }}
      [data-testid="stMetricValue"] {{ color:{PALETTE['navy']}; font:800 clamp(22px,2vw,29px) Manrope,sans-serif; letter-spacing:-.6px; }}
      [data-testid="stMetricDelta"] {{ font-size:11px; }}
      .section-title {{ margin:4px 0 12px; color:{PALETTE['navy']}; font:750 16px Manrope,sans-serif; }}
      .section-note {{ margin-top:-8px; margin-bottom:10px; color:{PALETTE['muted']}; font-size:11px; }}
      .stButton button, .stDownloadButton button {{ border-radius:10px; font-weight:650; }}
      [data-testid="stDataFrame"] {{ border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
      [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:16px; background:#fff; border-color:var(--line); box-shadow:0 4px 15px #243b5308; }}
      .stTabs [data-baseweb="tab-list"] {{ gap:6px; }}
      .stTabs [data-baseweb="tab"] {{ padding:8px 16px; border-radius:10px 10px 0 0; font-weight:650; }}
      .source-note {{ color:#8491a2; font-size:10px; }}
      @media (max-width:760px) {{ .hero {{ padding:22px 20px; }} .hero-badge {{ position:static; display:inline-block; margin-top:13px; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- data helpers
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
    prices = {"Analytics Suite": 62000, "Cloud Workspace": 38000, "Advisory Package": 94000,
              "Implementation": 115000, "Team License": 26000, "Data Connectors": 18000}
    product = rng.choice(list(products), size=rows, p=[.19, .15, .16, .14, .21, .15])
    category = [products[name] for name in product]
    unit_price = np.array([prices[name] for name in product])
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


def pct_delta(current: float, previous: float) -> str | None:
    if not previous:
        return None
    return f"{(current - previous) / abs(previous) * 100:+.1f}% vs previous period"


def style_fig(fig, height: int = 300, top: int = 8):
    fig.update_layout(
        height=height,
        margin={"l": 8, "r": 8, "t": top, "b": 5},
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"family": "DM Sans", "color": "#65768c"},
        hoverlabel={"font_family": "DM Sans"},
    )
    return fig


def reset_filters() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("f_"):
            del st.session_state[key]
    st.session_state["sel_nonce"] = st.session_state.get("sel_nonce", 0) + 1


def clear_drill() -> None:
    st.session_state["sel_nonce"] = st.session_state.get("sel_nonce", 0) + 1


# ---------------------------------------------------------------- sidebar: data
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
    with st.expander("Map your columns", expanded=uploaded_file is not None):
        date_guess = guess_column(columns, ("date", "order date", "invoice date", "created at"))
        amount_guess = guess_column(numeric_columns, ("sales", "revenue", "amount", "loan amount", "value"))
        profit_guess = guess_column(numeric_columns, ("profit", "margin", "net income"))
        category_guess = guess_column(dimension_columns, ("category", "product type", "type"))
        region_guess = guess_column(dimension_columns, ("region", "state", "territory", "city"))

        date_options = [NONE_DATE] + [str(column) for column in date_columns]
        date_default = date_options.index(str(date_guess)) if date_guess is not None and str(date_guess) in date_options else 0
        date_choice = st.selectbox("Date column", date_options, index=date_default)
        amount_options = [str(column) for column in numeric_columns]
        amount_default = amount_options.index(str(amount_guess)) if amount_guess is not None and str(amount_guess) in amount_options else 0
        amount_column = st.selectbox("Value column", amount_options, index=amount_default)
        profit_options = [NONE_PROFIT] + [str(column) for column in numeric_columns if str(column) != amount_column]
        profit_default = profit_options.index(str(profit_guess)) if profit_guess is not None and str(profit_guess) in profit_options else 0
        profit_choice = st.selectbox("Profit / comparison column", profit_options, index=profit_default)

        dimension_options = [NONE_DIM] + [str(column) for column in dimension_columns]
        category_default = dimension_options.index(str(category_guess)) if category_guess is not None and str(category_guess) in dimension_options else 0
        dimension_choice = st.selectbox("Primary breakdown", dimension_options, index=category_default)
        region_default = dimension_options.index(str(region_guess)) if region_guess is not None and str(region_guess) in dimension_options else 0
        segment_choice = st.selectbox("Secondary breakdown", dimension_options, index=region_default)

date_column = None if date_choice == NONE_DATE else date_choice
profit_column = None if profit_choice == NONE_PROFIT else profit_choice
dimension_column = None if dimension_choice == NONE_DIM else dimension_choice
segment_column = None if segment_choice == NONE_DIM else segment_choice

data = raw_data.copy()
data[amount_column] = pd.to_numeric(data[amount_column], errors="coerce")
if profit_column:
    data[profit_column] = pd.to_numeric(data[profit_column], errors="coerce")
data["_count"] = 1
has_dates = False
if date_column:
    data["_dashboard_date"] = pd.to_datetime(data[date_column], errors="coerce")
    has_dates = bool(data["_dashboard_date"].notna().any())

data = data.dropna(subset=[amount_column]).copy()
if data.empty:
    st.info("The selected value column has no numeric records.")
    st.stop()

# ---------------------------------------------------------------- sidebar: filters
with st.sidebar:
    st.markdown("### Filters")
    base = data.copy()
    for label, column in (("Primary filter", dimension_column), ("Secondary filter", segment_column)):
        if column:
            options = sorted(data[column].dropna().astype(str).unique().tolist())
            selected = st.multiselect(label, options, default=options, key=f"f_{normalized_name(column)}_{label[:3]}")
            base = base[base[column].astype(str).isin(selected)] if selected else base.iloc[0:0]

    filtered = base.copy()
    start_ts = end_ts = None
    preset = "All time"
    if has_dates:
        min_date = data["_dashboard_date"].min().normalize()
        max_date = data["_dashboard_date"].max().normalize()
        preset = st.radio(
            "Period", ["All time", "Last 30 days", "Last 90 days", "Last 12 months", "Custom"],
            key="f_preset", horizontal=True,
        )
        if preset == "Last 30 days":
            start_ts, end_ts = max_date - pd.Timedelta(days=29), max_date
        elif preset == "Last 90 days":
            start_ts, end_ts = max_date - pd.Timedelta(days=89), max_date
        elif preset == "Last 12 months":
            start_ts, end_ts = max_date - pd.DateOffset(years=1) + pd.Timedelta(days=1), max_date
        elif preset == "Custom":
            picked = st.date_input("Date range", value=(min_date.date(), max_date.date()),
                                   min_value=min_date.date(), max_value=max_date.date(), key="f_dates")
            if isinstance(picked, (tuple, list)) and len(picked) == 2:
                start_ts, end_ts = pd.Timestamp(picked[0]), pd.Timestamp(picked[1])
        if start_ts is not None:
            filtered = base[(base["_dashboard_date"] >= start_ts) &
                            (base["_dashboard_date"] < end_ts + pd.Timedelta(days=1))]

    st.button("↺ Reset all filters", on_click=reset_filters, use_container_width=True)
    st.divider()
    st.caption("MarketPulse · interactive analytics portfolio demo")

if filtered.empty:
    st.info("No records match these filters. Adjust the sidebar filters to continue.")
    st.stop()

# ---------------------------------------------------------------- drill-down state
nonce = st.session_state.setdefault("sel_nonce", 0)
bar_key = f"f_bar_sel_{nonce}"
drill_value = None
try:
    state = st.session_state.get(bar_key)
    points = state["selection"]["points"] if state else []
    if points:
        drill_value = str(points[0].get("y"))
except Exception:
    drill_value = None
if drill_value is not None and dimension_column:
    view = filtered[filtered[dimension_column].astype(str) == drill_value]
    if view.empty:
        view, drill_value = filtered, None
else:
    view, drill_value = filtered, None

# ---------------------------------------------------------------- hero
badge = f"●&nbsp; {len(view):,} records in view"
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-kicker">Portfolio project · Live data exploration</div>
      <h1>Business performance, at a glance.</h1>
      <p>Click, filter and drill into revenue, product mix, profitability, and regional trends.</p>
      <span class="hero-badge">{badge}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if drill_value is not None:
    chip_col, clear_col = st.columns([5, 1], vertical_alignment="center")
    chip_col.markdown(f'<span class="chip">Drilled into {dimension_column}: {drill_value}</span>'
                      '<span class="source-note">All charts below are filtered to this selection.</span>',
                      unsafe_allow_html=True)
    clear_col.button("✕ Clear drill-down", on_click=clear_drill, use_container_width=True)
else:
    st.caption("💡 Tip: click any bar in “Value by …” to drill the whole dashboard into that group.")

# ---------------------------------------------------------------- KPIs
def kpis(frame: pd.DataFrame) -> tuple[float, int, float, float | None]:
    total = float(frame[amount_column].sum())
    count = len(frame)
    avg = float(frame[amount_column].mean()) if count else 0.0
    prof = float(frame[profit_column].sum()) if profit_column else None
    return total, count, avg, prof


total_value, record_count, average_value, total_profit = kpis(view)
margin = (total_profit / total_value * 100) if total_profit is not None and total_value else None
unique_groups = (view[segment_column].nunique() if segment_column
                 else view[dimension_column].nunique() if dimension_column else record_count)

d_total = d_count = d_avg = None
if has_dates and start_ts is not None:
    span = end_ts - start_ts + pd.Timedelta(days=1)
    prev = base[(base["_dashboard_date"] >= start_ts - span) & (base["_dashboard_date"] < start_ts)]
    if drill_value is not None and dimension_column:
        prev = prev[prev[dimension_column].astype(str) == drill_value]
    if not prev.empty:
        p_total, p_count, p_avg, _ = kpis(prev)
        d_total, d_count, d_avg = pct_delta(total_value, p_total), pct_delta(record_count, p_count), pct_delta(average_value, p_avg)

metric_columns = st.columns(4)
metric_columns[0].metric("Total value", format_amount(total_value, currency), d_total, help=f"Sum of {amount_column}")
metric_columns[1].metric("Records", f"{record_count:,}", d_count, help="Rows matching the selected filters")
metric_columns[2].metric("Average value", format_amount(average_value, currency), d_avg, help=f"Average {amount_column} per record")
metric_columns[3].metric("Profit margin" if margin is not None else "Unique groups",
                         f"{margin:.1f}%" if margin is not None else f"{unique_groups:,}",
                         help="Profit divided by value" if margin is not None else "Distinct values in your selected breakdown")
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# measure selector shared by charts
measure_choices = {f"Value ({amount_column})": amount_column}
if profit_column:
    measure_choices[f"Profit ({profit_column})"] = profit_column
measure_choices["Record count"] = "_count"
is_money = lambda col: col != "_count"

tab_overview, tab_explore, tab_data = st.tabs(["📊 Overview", "🔎 Explore", "🗂 Data"])

# ================================================================ OVERVIEW
with tab_overview:
    ctrl = st.columns([1.4, 1, 1, 1])
    measure_label = ctrl[0].selectbox("Measure", list(measure_choices), key="f_measure")
    measure = measure_choices[measure_label]
    tick = currency if is_money(measure) else ""
    grain_label = ctrl[1].selectbox("Time grain", ["Day", "Week", "Month", "Quarter"], index=2, key="f_grain",
                                    disabled=not has_dates)
    chart_kind = ctrl[2].selectbox("Trend style", ["Area", "Line", "Bar"], key="f_kind")
    cumulative = ctrl[3].toggle("Cumulative", key="f_cum", disabled=not has_dates)
    freq = {"Day": "D", "Week": "W", "Month": "M", "Quarter": "Q"}[grain_label]

    left_chart, right_chart = st.columns([1.55, 1], gap="medium")

    with left_chart:
        with st.container(border=True):
            st.markdown(f'<div class="section-title">{measure_label.split(" (")[0]} trend</div>', unsafe_allow_html=True)
            if has_dates:
                td = view.dropna(subset=["_dashboard_date"]).copy()
                td["Period"] = td["_dashboard_date"].dt.to_period(freq).dt.to_timestamp()
                trend = td.groupby("Period", as_index=False)[measure].sum().sort_values("Period")
                if cumulative:
                    trend[measure] = trend[measure].cumsum()
                if chart_kind == "Bar":
                    fig = px.bar(trend, x="Period", y=measure, color_discrete_sequence=[PALETTE["blue"]])
                elif chart_kind == "Line":
                    fig = px.line(trend, x="Period", y=measure, markers=True, color_discrete_sequence=[PALETTE["blue"]])
                    fig.update_traces(line={"width": 3})
                else:
                    fig = px.area(trend, x="Period", y=measure, color_discrete_sequence=[PALETTE["blue"]])
                    fig.update_traces(line={"width": 3}, fillcolor="rgba(71,121,219,.13)")
                fig.update_traces(hovertemplate="%{x|%d %b %Y}<br>%{y:,.0f}<extra></extra>")
                fig.update_layout(xaxis_title=None, yaxis_title=None, hovermode="x unified", showlegend=False)
                fig.update_yaxes(tickprefix=tick, separatethousands=True, gridcolor="#edf1f6", zeroline=False)
                fig.update_xaxes(showgrid=False, rangeslider={"visible": True, "thickness": .07},
                                 rangeselector={"buttons": [
                                     {"count": 3, "label": "3m", "step": "month", "stepmode": "backward"},
                                     {"count": 6, "label": "6m", "step": "month", "stepmode": "backward"},
                                     {"step": "all", "label": "All"}]})
                style_fig(fig, height=360)
            else:
                fig = px.histogram(view, x=measure, nbins=18, color_discrete_sequence=[PALETTE["blue"]])
                fig.update_layout(xaxis_title=measure, yaxis_title="Records", showlegend=False)
                fig.update_xaxes(tickprefix=tick, separatethousands=True, gridcolor="#edf1f6")
                style_fig(fig, height=330)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with right_chart:
        with st.container(border=True):
            st.markdown(f'<div class="section-title">{measure_label.split(" (")[0]} by {dimension_column or "record"}</div>',
                        unsafe_allow_html=True)
            if dimension_column:
                bc = st.columns([1, 1])
                top_n = bc[0].slider("Show top", 3, 20, 8, key="f_topn")
                ascending_order = bc[1].toggle("Lowest first", key="f_asc")
                # bar chart always uses the un-drilled data so every bar stays clickable
                bd = filtered.groupby(dimension_column, dropna=False)[measure].sum()
                bd.index = bd.index.map(lambda v: "Unspecified" if pd.isna(v) else str(v))
                bd = bd.groupby(level=0).sum().sort_values(ascending=ascending_order).head(top_n).sort_values(ascending=True).reset_index()
                bd.columns = [dimension_column, measure]
                colors = [PALETTE["amber"] if (drill_value and v == drill_value) else PALETTE["blue"]
                          for v in bd[dimension_column]]
                bar_fig = px.bar(bd, x=measure, y=dimension_column, orientation="h")
                bar_fig.update_traces(marker_color=colors, hovertemplate="%{y}<br>%{x:,.0f}<extra></extra>")
                bar_fig.update_layout(xaxis_title=None, yaxis_title=None, clickmode="event+select")
                bar_fig.update_xaxes(tickprefix=tick, separatethousands=True, gridcolor="#edf1f6", zeroline=False)
                style_fig(bar_fig, height=260)
                try:
                    st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False},
                                    on_select="rerun", selection_mode="points", key=bar_key)
                except TypeError:  # older Streamlit without selection support
                    st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})
                    st.caption("Upgrade Streamlit (>=1.35) to enable click-to-drill.")
            else:
                hist = px.histogram(view, x=measure, nbins=12, color_discrete_sequence=[PALETTE["teal"]])
                hist.update_layout(xaxis_title=measure, yaxis_title="Records")
                st.plotly_chart(style_fig(hist, height=300), use_container_width=True, config={"displayModeBar": False})

    lower_left, lower_right = st.columns([1.05, 1], gap="medium")

    with lower_left:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Portfolio composition</div>", unsafe_allow_html=True)
            donut_dimension = segment_column or dimension_column
            if donut_dimension:
                comp = view.copy()
                comp[donut_dimension] = comp[donut_dimension].fillna("Unspecified").astype(str)
                comp = comp.groupby(donut_dimension)[measure].sum().reset_index()
                comp = comp[comp[measure] > 0]
                donut = px.pie(comp, names=donut_dimension, values=measure, hole=.68, color_discrete_sequence=SEQUENCE)
                donut.update_traces(textposition="inside", textinfo="percent", pull=[.03] * len(comp),
                                    marker={"line": {"color": "white", "width": 3}},
                                    hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>")
                donut.update_layout(legend={"orientation": "h", "y": -0.05, "x": .5, "xanchor": "center"},
                                    showlegend=len(comp) <= 8,
                                    annotations=[{"text": f"<b>{format_amount(comp[measure].sum(), tick) if is_money(measure) else f'{int(comp[measure].sum()):,}'}</b>",
                                                  "showarrow": False, "font": {"size": 16, "color": PALETTE["navy"]}}])
                st.plotly_chart(style_fig(donut, height=300, top=5), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Choose a text column in the sidebar to see portfolio composition.")

    with lower_right:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Profitability</div>", unsafe_allow_html=True)
            if profit_column and has_dates:
                pdata = view.dropna(subset=["_dashboard_date", profit_column]).copy()
                pdata["Period"] = pdata["_dashboard_date"].dt.to_period(freq).dt.to_timestamp()
                mp = pdata.groupby("Period", as_index=False)[[amount_column, profit_column]].sum().sort_values("Period")
                pf = px.bar(mp, x="Period", y=[amount_column, profit_column], barmode="group",
                            color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"]])
                pf.update_layout(xaxis_title=None, yaxis_title=None, legend_title=None,
                                 legend={"orientation": "h", "y": 1.12, "x": 0}, hovermode="x unified")
                pf.update_yaxes(tickprefix=currency, separatethousands=True, gridcolor="#edf1f6", zeroline=False)
                pf.update_xaxes(showgrid=False)
                st.plotly_chart(style_fig(pf, height=300, top=20), use_container_width=True, config={"displayModeBar": False})
            elif profit_column:
                pf = px.scatter(view, x=amount_column, y=profit_column, color=dimension_column, opacity=.75,
                                color_discrete_sequence=SEQUENCE)
                pf.update_layout(legend_title=None)
                st.plotly_chart(style_fig(pf, height=300, top=15), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Map a profit or comparison column to unlock profitability analysis.")

# ================================================================ EXPLORE
with tab_explore:
    ex_left, ex_right = st.columns(2, gap="medium")

    with ex_left:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Hierarchy treemap</div>", unsafe_allow_html=True)
            st.markdown("<div class='section-note'>Click a block to zoom in; click the header to zoom out.</div>", unsafe_allow_html=True)
            path = [c for c in (dimension_column, segment_column) if c]
            path = list(dict.fromkeys(path))
            if path:
                tm = view.copy()
                for c in path:
                    tm[c] = tm[c].fillna("Unspecified").astype(str)
                tm = tm.groupby(path, as_index=False)[amount_column].sum()
                tm = tm[tm[amount_column] > 0]
                tree = px.treemap(tm, path=path, values=amount_column, color=amount_column,
                                  color_continuous_scale=["#dce8ff", PALETTE["blue"], PALETTE["navy"]])
                tree.update_layout(coloraxis_showscale=False)
                tree.update_traces(hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>")
                st.plotly_chart(style_fig(tree, height=380), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Pick a breakdown column to see the hierarchy.")

    with ex_right:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Heatmap: primary × secondary</div>", unsafe_allow_html=True)
            st.markdown("<div class='section-note'>Hover any cell for exact values.</div>", unsafe_allow_html=True)
            if dimension_column and segment_column and dimension_column != segment_column:
                hm = view.copy()
                hm[dimension_column] = hm[dimension_column].fillna("Unspecified").astype(str)
                hm[segment_column] = hm[segment_column].fillna("Unspecified").astype(str)
                pivot = hm.pivot_table(index=dimension_column, columns=segment_column, values=amount_column,
                                       aggfunc="sum", fill_value=0)
                heat = px.imshow(pivot, aspect="auto", text_auto=".2s",
                                 color_continuous_scale=["#f1f6ff", PALETTE["blue"], PALETTE["navy"]])
                heat.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
                st.plotly_chart(style_fig(heat, height=380), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Choose two different breakdown columns to see the heatmap.")

    with st.container(border=True):
        st.markdown("<div class='section-title'>Build your own scatter</div>", unsafe_allow_html=True)
        sc = st.columns(4)
        num_labels = [str(c) for c in numeric_columns]
        x_axis = sc[0].selectbox("X axis", num_labels, index=0, key="f_sx")
        y_axis = sc[1].selectbox("Y axis", num_labels, index=min(1, len(num_labels) - 1), key="f_sy")
        color_by = sc[2].selectbox("Colour by", [NONE_DIM] + [str(c) for c in dimension_columns],
                                   index=([NONE_DIM] + [str(c) for c in dimension_columns]).index(str(dimension_column)) if dimension_column else 0,
                                   key="f_sc")
        trendline = sc[3].toggle("Trendline", key="f_tl")
        sample = view.copy()
        for c in (x_axis, y_axis):
            sample[c] = pd.to_numeric(sample[c], errors="coerce")
        sample = sample.dropna(subset=[x_axis, y_axis])
        if len(sample) > 3000:
            sample = sample.sample(3000, random_state=1)
        if color_by != NONE_DIM:
            sample[color_by] = sample[color_by].astype(str)
        scatter_kwargs = {"trendline": "ols"} if trendline else {}
        try:
            sfig = px.scatter(sample, x=x_axis, y=y_axis, color=None if color_by == NONE_DIM else color_by,
                              opacity=.7, color_discrete_sequence=SEQUENCE, **scatter_kwargs)
        except Exception:  # statsmodels missing for trendline
            sfig = px.scatter(sample, x=x_axis, y=y_axis, color=None if color_by == NONE_DIM else color_by,
                              opacity=.7, color_discrete_sequence=SEQUENCE)
            st.caption("Trendline needs the `statsmodels` package.")
        sfig.update_layout(legend_title=None)
        sfig.update_xaxes(gridcolor="#edf1f6")
        sfig.update_yaxes(gridcolor="#edf1f6")
        st.plotly_chart(style_fig(sfig, height=380), use_container_width=True, config={"displaylogo": False})

# ================================================================ DATA
with tab_data:
    helper_cols = ["_dashboard_date", "_count"]
    display_data = view.drop(columns=helper_cols, errors="ignore").copy()
    if date_column:
        display_data[date_column] = pd.to_datetime(display_data[date_column], errors="coerce").dt.strftime("%d %b %Y")

    head, dl = st.columns([1, 0.2], vertical_alignment="center")
    with head:
        st.markdown('<div class="section-title">Filtered records</div>', unsafe_allow_html=True)
    with dl:
        st.download_button("Download CSV", data=view.drop(columns=helper_cols, errors="ignore").to_csv(index=False).encode("utf-8"),
                           file_name="marketpulse_filtered_data.csv", mime="text/csv", use_container_width=True)

    tc = st.columns([2, 2, 1])
    query = tc[0].text_input("Search records", placeholder="Type to search any column…", key="f_search")
    shown_cols = tc[1].multiselect("Columns", list(display_data.columns), default=list(display_data.columns), key="f_cols")
    sort_col = tc[2].selectbox("Sort by", ["(None)"] + list(display_data.columns), key="f_sort")

    table = display_data[shown_cols] if shown_cols else display_data
    if query:
        mask = table.astype(str).apply(lambda s: s.str.contains(query, case=False, na=False, regex=False)).any(axis=1)
        table = table[mask]
    if sort_col != "(None)" and sort_col in table.columns:
        table = table.sort_values(sort_col, ascending=False)

    st.markdown(f'<div class="section-note">Showing {len(table):,} of {len(raw_data):,} rows from {source_label}</div>', unsafe_allow_html=True)
    st.dataframe(table, use_container_width=True, hide_index=True, height=420)

st.markdown('<p class="source-note">MarketPulse is a portfolio demo. Sample records are synthetic; uploaded data stays in the current app session.</p>', unsafe_allow_html=True)
