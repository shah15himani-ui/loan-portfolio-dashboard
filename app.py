
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import html

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="JR Financial | Loan Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# THEME AND CSS
# =========================================================

st.html("""
<style>
.stApp {
    background: #F2F3F5;
    color: #263238;
}

.block-container {
    padding: 0.8rem 1rem 0.5rem 1rem;
    max-width: 100%;
}

header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    display: none;
}

.top-header {
    background: #202020;
    padding: 10px 18px;
    border-radius: 8px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.brand-name {
    color: white;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: .5px;
}

.brand-subtitle {
    color: #B8C4B8;
    font-size: 9px;
    margin-top: 2px;
}

.dashboard-title {
    color: #263238;
    font-size: 21px;
    font-weight: 800;
    margin-bottom: 2px;
}

.dashboard-subtitle {
    color: #87918B;
    font-size: 10px;
    margin-bottom: 10px;
}

.nav-label {
    color: #FFFFFF;
    font-size: 10px;
    font-weight: 600;
}

.kpi-rail {
    background: #FFFFFF;
    border: 1px solid #E5E8E5;
    border-radius: 9px;
    padding: 10px 8px;
    margin-bottom: 8px;
    min-height: 83px;
    text-align: center;
}

.kpi-icon {
    color: #55A66A;
    font-size: 18px;
    margin-bottom: 3px;
}

.kpi-rail-label {
    font-size: 9px;
    color: #7B8580;
    font-weight: 600;
}

.kpi-rail-value {
    font-size: 19px;
    color: #27332D;
    font-weight: 800;
    margin-top: 2px;
}

.kpi-rail-note {
    color: #55A66A;
    font-size: 8px;
    margin-top: 2px;
}

.metric-card {
    background: white;
    border: 1px solid #E6E9E6;
    border-radius: 9px;
    padding: 10px 12px;
    min-height: 82px;
}

.metric-label {
    color: #849087;
    font-size: 10px;
    font-weight: 600;
}

.metric-value {
    color: #28352D;
    font-size: 22px;
    font-weight: 800;
    margin-top: 5px;
}

.metric-note {
    color: #55A66A;
    font-size: 9px;
    margin-top: 2px;
}

.panel-title {
    color: #39443D;
    font-size: 11px;
    font-weight: 750;
    margin-bottom: 4px;
}

.section-label {
    color: #8A948D;
    font-size: 9px;
    letter-spacing: 1.2px;
    font-weight: 700;
    margin: 8px 0 5px 2px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border: 1px solid #E6E9E6;
    border-radius: 9px;
}

div[data-testid="stPlotlyChart"] {
    margin-bottom: -10px;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stTextInput"] label {
    font-size: 10px;
    color: #65716A;
    font-weight: 600;
}

div[data-testid="stRadio"] > div {
    gap: 5px;
}

div[data-testid="stRadio"] label {
    background: #303030;
    border-radius: 6px;
    padding: 5px 9px;
    color: white !important;
    font-size: 10px;
}

div[data-testid="stRadio"] label p {
    color: white !important;
    font-size: 10px;
}

div[data-testid="stRadio"] label:has(input:checked) {
    background: #55A66A;
}

.stButton button {
    border-radius: 6px;
    font-size: 11px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #E5E8E5;
    border-radius: 8px;
}

footer {
    visibility: hidden;
}
</style>
""")


# =========================================================
# DATA CLEANING
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

    data = data.dropna(
        subset=["Loan Amount", "Date"]
    )

    return data.reset_index(drop=True)


# =========================================================
# FORMATTING FUNCTIONS
# =========================================================

def format_crore(value):
    return f"₹{value / 10000000:.2f} Cr"


def format_money(value):
    return f"₹{value:,.0f}"


def rail_metric(icon, label, value, note="Portfolio metric"):

    st.html(f"""
    <div class="kpi-rail">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-rail-label">{html.escape(str(label))}</div>
        <div class="kpi-rail-value">{html.escape(str(value))}</div>
        <div class="kpi-rail-note">{html.escape(str(note))}</div>
    </div>
    """)


def metric_card(label, value, note="Portfolio overview"):

    st.html(f"""
    <div class="metric-card">
        <div class="metric-label">{html.escape(str(label))}</div>
        <div class="metric-value">{html.escape(str(value))}</div>
        <div class="metric-note">{html.escape(str(note))}</div>
    </div>
    """)


def panel_heading(title):

    st.html(
        f'<div class="panel-title">{html.escape(str(title))}</div>'
    )


def draw_chart(fig, height=190):

    fig.update_layout(
        height=height,
        margin=dict(l=5, r=5, t=12, b=5),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=9,
            color="#6C776F"
        ),
        hoverlabel=dict(
            bgcolor="#25352B",
            font_color="white"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=8)
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EDF0ED",
        zeroline=False,
        tickfont=dict(size=8)
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=8)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )


# =========================================================
# UPLOAD PAGE
# =========================================================

if "loan_df" not in st.session_state:

    st.html("""
    <div style="
        max-width:700px;
        margin:90px auto 25px auto;
        text-align:center;
    ">
        <div style="
            color:#55A66A;
            font-size:12px;
            font-weight:700;
            letter-spacing:2px;
        ">
            JR FINANCIAL
        </div>

        <h1 style="
            font-size:38px;
            color:#26352B;
            margin:12px 0;
        ">
            Loan Portfolio Analytics
        </h1>

        <p style="
            color:#7C8980;
            font-size:15px;
        ">
            Upload your loan records to explore portfolio
            performance, application status and trends.
        </p>
    </div>
    """)

    uploaded_file = st.file_uploader(
        "Upload your Excel workbook",
        type=["xlsx"]
    )

    if uploaded_file is not None:

        try:

            raw_df = pd.read_excel(uploaded_file)
            cleaned_df = clean_loan_data(raw_df)

            if cleaned_df.empty:

                st.error("No valid loan records found.")

            else:

                st.session_state["loan_df"] = cleaned_df
                st.session_state["loan_filename"] = uploaded_file.name

                st.rerun()

        except Exception as e:

            st.error(f"Unable to process file: {e}")

    st.stop()


# =========================================================
# LOAD DATA
# =========================================================

df = st.session_state["loan_df"].copy()

df["Month"] = df["Date"].dt.to_period("M")
df["Month Year"] = df["Month"].astype(str)


# =========================================================
# TOP HEADER
# =========================================================

header_left, header_right = st.columns([2, 1])

with header_left:

    st.html("""
    <div class="top-header">
        <div>
            <div class="brand-name">JR FINANCIAL</div>
            <div class="brand-subtitle">
                LOAN PORTFOLIO MANAGEMENT SYSTEM
            </div>
        </div>
    </div>
    """)

with header_right:

    st.html("""
    <div style="
        background:#202020;
        border-radius:8px;
        padding:13px;
        color:#DDE5DD;
        font-size:10px;
        text-align:right;
        min-height:50px;
    ">
        LIVE PORTFOLIO ANALYTICS
    </div>
    """)


# =========================================================
# TOP NAVIGATION
# =========================================================

page = st.radio(
    "Dashboard Navigation",
    [
        "Summary",
        "Loan Types",
        "Banks",
        "Executives",
        "Records",
        "KPI Metrics"
    ],
    horizontal=True,
    label_visibility="collapsed"
)


# =========================================================
# PAGE TITLE
# =========================================================

st.html("""
<div class="dashboard-title">
    Loan Portfolio Dashboard
</div>

<div class="dashboard-subtitle">
    Monitor loan applications, portfolio performance and business activity
</div>
""")


# =========================================================
# FILTERS
# =========================================================

f1, f2, f3, f4 = st.columns([1.15, 1.15, 1.15, 1.5])

with f1:

    bank_filter = st.selectbox(
        "Bank",
        ["All Banks"] + sorted(df["Bank Name"].unique().tolist())
    )

with f2:

    loan_filter = st.selectbox(
        "Loan Type",
        ["All Loan Types"] + sorted(df["Type of Loan"].unique().tolist())
    )

with f3:

    status_filter = st.selectbox(
        "Application Status",
        ["All Statuses"] + sorted(df["Status"].unique().tolist())
    )

with f4:

    customer_search = st.text_input(
        "Search Customer",
        placeholder="Enter customer name..."
    )


d1, d2, d3 = st.columns([1, 1, 3])

with d1:

    start_date = st.date_input(
        "From Date",
        value=df["Date"].min().date()
    )

with d2:

    end_date = st.date_input(
        "To Date",
        value=df["Date"].max().date()
    )

with d3:

    st.write("")
    st.write("")

    if st.button("Reset All Filters"):

        st.rerun()


# =========================================================
# APPLY FILTERS
# =========================================================

filtered = df.copy()

if bank_filter != "All Banks":

    filtered = filtered[
        filtered["Bank Name"] == bank_filter
    ]

if loan_filter != "All Loan Types":

    filtered = filtered[
        filtered["Type of Loan"] == loan_filter
    ]

if status_filter != "All Statuses":

    filtered = filtered[
        filtered["Status"] == status_filter
    ]

if customer_search.strip():

    filtered = filtered[
        filtered["Customer Name"].str.contains(
            customer_search.strip(),
            case=False,
            na=False
        )
    ]

if start_date > end_date:

    st.error("From Date cannot be after To Date.")
    st.stop()

filtered = filtered[
    (filtered["Date"].dt.date >= start_date)
    & (filtered["Date"].dt.date <= end_date)
]

if filtered.empty:

    st.warning("No records found for the selected filters.")
    st.stop()


# =========================================================
# METRICS
# =========================================================

total_apps = len(filtered)

total_amount = filtered["Loan Amount"].sum()

disbursed = filtered[
    filtered["Status"].str.lower() == "disbursed"
]

pending = filtered[
    filtered["Status"].str.lower() == "pending"
]

approved = filtered[
    filtered["Status"].str.lower() == "approved"
]

disbursed_amount = disbursed["Loan Amount"].sum()

approval_rate = (
    len(approved) / total_apps * 100
    if total_apps else 0
)

disbursement_rate = (
    len(disbursed) / total_apps * 100
    if total_apps else 0
)


# =========================================================
# SUMMARY PAGE
# =========================================================

if page == "Summary":

    # LEFT KPI RAIL + MAIN DASHBOARD

    left_rail, main_area = st.columns(
        [0.17, 0.83],
        gap="small"
    )

    # -----------------------------------------------------
    # LEFT KPI RAIL
    # -----------------------------------------------------

    with left_rail:

        rail_metric(
            "◉",
            "Total Applications",
            f"{total_apps:,}"
        )

        rail_metric(
            "◈",
            "Loan Portfolio",
            format_crore(total_amount)
        )

        rail_metric(
            "▣",
            "Disbursed",
            f"{len(disbursed):,}"
        )

        rail_metric(
            "◇",
            "Approval Rate",
            f"{approval_rate:.1f}%"
        )

        rail_metric(
            "⌛",
            "Pending",
            f"{len(pending):,}"
        )

    # -----------------------------------------------------
    # MAIN AREA
    # -----------------------------------------------------

    with main_area:

        # TOP KPI CARDS

        st.html(
            '<div class="section-label">PORTFOLIO OVERVIEW</div>'
        )

        m1, m2, m3 = st.columns(3, gap="small")

        with m1:

            metric_card(
                "Total Loan Amount",
                format_crore(total_amount),
                "Total portfolio value"
            )

        with m2:

            metric_card(
                "Disbursed Amount",
                format_crore(disbursed_amount),
                "Successfully disbursed"
            )

        with m3:

            metric_card(
                "Unique Customers",
                f"{filtered['Customer Name'].nunique():,}",
                "Customers in selected period"
            )

        # -------------------------------------------------
        # ROW 1: LOAN TYPE AND STATUS
        # -------------------------------------------------

        st.html(
            '<div class="section-label">PORTFOLIO BREAKDOWN</div>'
        )

        c1, c2 = st.columns([1.25, 1], gap="small")

        with c1:

            with st.container(border=True):

                panel_heading("Loan Type Performance")

                loan_data = (
                    filtered.groupby("Type of Loan")["Loan Amount"]
                    .sum()
                    .reset_index()
                    .sort_values("Loan Amount", ascending=True)
                )

                fig = px.bar(
                    loan_data,
                    x="Loan Amount",
                    y="Type of Loan",
                    orientation="h",
                    text_auto=".2s",
                    color_discrete_sequence=["#55A66A"]
                )

                fig.update_layout(
                    xaxis_title="Loan Amount",
                    yaxis_title=""
                )

                draw_chart(fig, 205)

        with c2:

            with st.container(border=True):

                panel_heading("Application Status")

                status_data = (
                    filtered["Status"]
                    .value_counts()
                    .reset_index()
                )

                status_data.columns = [
                    "Status",
                    "Applications"
                ]

                fig = px.pie(
                    status_data,
                    names="Status",
                    values="Applications",
                    hole=0.58,
                    color_discrete_sequence=[
                        "#55A66A",
                        "#83B95C",
                        "#D9B93D",
                        "#A8B1AB",
                        "#3E7850"
                    ]
                )

                fig.update_traces(
                    textinfo="percent",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Applications: %{value}<extra></extra>"
                    )
                )

                draw_chart(fig, 205)

        # -------------------------------------------------
        # ROW 2: MONTHLY TREND AND BANK COMPARISON
        # -------------------------------------------------

        c3, c4 = st.columns(2, gap="small")

        with c3:

            with st.container(border=True):

                panel_heading("Monthly Loan Trend")

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
                        line=dict(
                            color="#55A66A",
                            width=2
                        ),
                        marker=dict(size=5),
                        fill="tozeroy",
                        fillcolor="rgba(85,166,106,0.15)"
                    )
                )

                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Loan Amount"
                )

                draw_chart(fig, 190)

        with c4:

            with st.container(border=True):

                panel_heading("Bank-wise Comparison")

                bank_data = (
                    filtered.groupby("Bank Name")["Loan Amount"]
                    .sum()
                    .nlargest(6)
                    .reset_index()
                )

                fig = px.bar(
                    bank_data,
                    x="Bank Name",
                    y="Loan Amount",
                    color_discrete_sequence=["#4C985A"]
                )

                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Loan Amount"
                )

                draw_chart(fig, 190)

        # -------------------------------------------------
        # ROW 3: EXECUTIVE AND CUSTOMER PERFORMANCE
        # -------------------------------------------------

        c5, c6 = st.columns(2, gap="small")

        with c5:

            with st.container(border=True):

                panel_heading("Executive Performance")

                executive_data = (
                    filtered.groupby("Executive Name")["Loan Amount"]
                    .sum()
                    .nlargest(5)
                    .reset_index()
                    .sort_values("Loan Amount")
                )

                fig = px.bar(
                    executive_data,
                    x="Loan Amount",
                    y="Executive Name",
                    orientation="h",
                    color_discrete_sequence=["#83B95C"]
                )

                fig.update_layout(
                    xaxis_title="Loan Amount",
                    yaxis_title=""
                )

                draw_chart(fig, 185)

        with c6:

            with st.container(border=True):

                panel_heading("Top 5 Customers")

                customer_data = (
                    filtered.groupby("Customer Name")["Loan Amount"]
                    .sum()
                    .nlargest(5)
                    .reset_index()
                    .sort_values("Loan Amount")
                )

                fig = px.bar(
                    customer_data,
                    x="Loan Amount",
                    y="Customer Name",
                    orientation="h",
                    color_discrete_sequence=["#3E7850"]
                )

                fig.update_layout(
                    xaxis_title="Loan Amount",
                    yaxis_title=""
                )

                draw_chart(fig, 185)


# =========================================================
# LOAN TYPES PAGE
# =========================================================

elif page == "Loan Types":

    st.html(
        '<div class="section-label">LOAN TYPE PERFORMANCE</div>'
    )

    loan_summary = (
        filtered.groupby("Type of Loan")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Loan_Amount", ascending=False)
    )

    c1, c2 = st.columns(2)

    with c1:

        with st.container(border=True):

            panel_heading("Loan Amount by Type")

            fig = px.bar(
                loan_summary.sort_values("Loan_Amount"),
                x="Loan_Amount",
                y="Type of Loan",
                orientation="h",
                color_discrete_sequence=["#55A66A"]
            )

            draw_chart(fig, 350)

    with c2:

        with st.container(border=True):

            panel_heading("Application Distribution")

            fig = px.pie(
                loan_summary,
                names="Type of Loan",
                values="Applications",
                hole=0.55
            )

            draw_chart(fig, 350)

    st.dataframe(
        loan_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# BANKS PAGE
# =========================================================

elif page == "Banks":

    st.html(
        '<div class="section-label">BANK PERFORMANCE ANALYSIS</div>'
    )

    bank_summary = (
        filtered.groupby("Bank Name")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Loan_Amount", ascending=False)
    )

    c1, c2 = st.columns(2)

    with c1:

        with st.container(border=True):

            panel_heading("Bank-wise Loan Amount")

            fig = px.bar(
                bank_summary.sort_values("Loan_Amount"),
                x="Loan_Amount",
                y="Bank Name",
                orientation="h",
                color_discrete_sequence=["#55A66A"]
            )

            draw_chart(fig, 350)

    with c2:

        with st.container(border=True):

            panel_heading("Applications by Bank")

            fig = px.pie(
                bank_summary,
                names="Bank Name",
                values="Applications",
                hole=0.55
            )

            draw_chart(fig, 350)

    st.dataframe(
        bank_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# EXECUTIVES PAGE
# =========================================================

elif page == "Executives":

    st.html(
        '<div class="section-label">EXECUTIVE PERFORMANCE</div>'
    )

    executive_summary = (
        filtered.groupby("Executive Name")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Loan_Amount", ascending=False)
    )

    c1, c2 = st.columns(2)

    with c1:

        with st.container(border=True):

            panel_heading("Executive-wise Loan Amount")

            fig = px.bar(
                executive_summary.sort_values("Loan_Amount"),
                x="Loan_Amount",
                y="Executive Name",
                orientation="h",
                color_discrete_sequence=["#55A66A"]
            )

            draw_chart(fig, 350)

    with c2:

        with st.container(border=True):

            panel_heading("Executive Application Share")

            fig = px.pie(
                executive_summary,
                names="Executive Name",
                values="Applications",
                hole=0.55
            )

            draw_chart(fig, 350)

    st.dataframe(
        executive_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# RECORDS PAGE
# =========================================================

elif page == "Records":

    st.html(
        '<div class="section-label">LOAN APPLICATION RECORDS</div>'
    )

    display_df = filtered.copy()

    display_df["Date"] = (
        display_df["Date"].dt.strftime("%d-%b-%Y")
    )

    st.caption(
        f"Showing {len(display_df):,} records"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        height=480,
        hide_index=True
    )

    csv_data = filtered.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Filtered Records",
        data=csv_data,
        file_name="loan_portfolio_records.csv",
        mime="text/csv"
    )


# =========================================================
# KPI METRICS PAGE
# =========================================================

elif page == "KPI Metrics":

    st.html(
        '<div class="section-label">PORTFOLIO KPI METRICS</div>'
    )

    a, b, c, d = st.columns(4)

    with a:
        metric_card("Total Applications", total_apps)

    with b:
        metric_card("Approved Applications", len(approved))

    with c:
        metric_card("Disbursed Applications", len(disbursed))

    with d:
        metric_card("Pending Applications", len(pending))

    st.divider()

    a, b, c = st.columns(3)

    with a:
        st.metric(
            "Approval Rate",
            f"{approval_rate:.1f}%"
        )

    with b:
        st.metric(
            "Disbursement Rate",
            f"{disbursement_rate:.1f}%"
        )

    with c:
        st.metric(
            "Average Loan Amount",
            format_money(filtered["Loan Amount"].mean())
        )

    with st.container(border=True):

        panel_heading("Application Status Comparison")

        status_summary = (
            filtered["Status"]
            .value_counts()
            .reset_index()
        )

        status_summary.columns = [
            "Status",
            "Applications"
        ]

        fig = px.bar(
            status_summary,
            x="Status",
            y="Applications",
            color_discrete_sequence=["#55A66A"]
        )

        draw_chart(fig, 300)


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div style="
    text-align:center;
    color:#A0AAA2;
    font-size:9px;
    padding:10px 0 2px 0;
">
    JR Financial | Loan Portfolio Analytics
</div>
""")
