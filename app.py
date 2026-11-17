
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import html

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="JR Financial | Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. DESIGN AND CSS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #F2F5FA !important;
    color: #172B4D;
    font-family: 'Inter', sans-serif;
}

/* TOP BAR */

header[data-testid="stHeader"] {
    background: #F2F5FA !important;
    height: 3.5rem !important;
    z-index: 999999 !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stAppDeployButton {
    display: none !important;
}

/* MAIN CONTENT SPACING */

.block-container {
    padding-top: 4.5rem !important;
    padding-right: 1.5rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.5rem !important;
    max-width: 100% !important;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E1E7F0;
}

[data-testid="stSidebar"] * {
    color: #334766;
}

.brand-box {
    padding: 15px 8px 22px;
    border-bottom: 1px solid #E7ECF3;
    margin-bottom: 20px;
}

.brand-kicker {
    color: #4778E8;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
}

.brand-title {
    color: #172B4D;
    font-size: 23px;
    font-weight: 800;
    margin-top: 5px;
}

.brand-subtitle {
    color: #8493A9;
    font-size: 10px;
    margin-top: 4px;
}

/* PAGE HEADER */

.page-title {
    color: #172B4D;
    font-size: 25px;
    font-weight: 800;
    margin-top: 8px !important;
    padding-top: 5px !important;
    margin-bottom: 3px;
    position: relative;
    z-index: 1;
}

.page-subtitle {
    color: #71829C;
    font-size: 12px;
    margin-bottom: 16px;
}

/* FILTERS */

.filter-label {
    color: #8290A5;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.4px;
    margin: 12px 0;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stTextInput"] label {
    color: #536780;
    font-size: 11px;
    font-weight: 600;
}

div[data-baseweb="select"] > div {
    background: #FFFFFF;
    border-color: #DCE4EF;
    border-radius: 7px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stDateInput"] input {
    background: #FFFFFF;
    border-color: #DCE4EF;
    border-radius: 7px;
}

/* CARDS */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid #DCE5F0;
    border-radius: 15px;
    box-shadow: 0 3px 12px rgba(31, 55, 90, 0.035);
    padding: 10px 12px;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #FFFFFF !important;
}

/* CHARTS */

div[data-testid="stPlotlyChart"],
div[data-testid="stPlotlyChart"] > div {
    background: #FFFFFF !important;
    border-radius: 10px !important;
}

/* CHART HEADINGS */

.card-heading {
    color: #173253;
    font-size: 14px;
    font-weight: 750;
    margin: 1px 0 2px;
}

.card-subheading {
    color: #8291A6;
    font-size: 10px;
    margin-bottom: 8px;
}

/* KPI CARDS */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #DCE5F0;
    border-radius: 12px;
    padding: 13px 15px;
    min-height: 95px;
    box-shadow: 0 2px 9px rgba(31, 55, 90, 0.03);
}

.kpi-label {
    color: #8492A7;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .5px;
}

.kpi-value {
    color: #172B4D;
    font-size: 23px;
    font-weight: 800;
    margin-top: 7px;
}

.kpi-note {
    color: #28A879;
    font-size: 10px;
    margin-top: 3px;
}

/* STATUS ROWS */

.status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 11px 0;
    border-bottom: 1px solid #E9EEF5;
    gap: 8px;
}

.status-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.status-pill {
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}

.status-count {
    color: #8291A6;
    font-size: 10px;
}

.status-amount {
    color: #173253;
    font-size: 11px;
    font-weight: 750;
    white-space: nowrap;
}

/* PRIORITY ACTIONS */

.action-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #EDF1F6;
    gap: 10px;
}

.action-name {
    color: #263D5B;
    font-size: 11px;
    font-weight: 650;
}

.action-detail {
    color: #8A98AB;
    font-size: 10px;
    margin-top: 3px;
}

.action-tag {
    border-radius: 20px;
    padding: 5px 9px;
    font-size: 9px;
    font-weight: 700;
    white-space: nowrap;
}

/* BUTTONS */

.stButton button,
.stDownloadButton button {
    background: #4778E8;
    color: white;
    border: 1px solid #4778E8;
    border-radius: 7px;
    font-size: 11px;
    font-weight: 700;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #3266D5;
    color: white;
    border-color: #3266D5;
}

/* TABLE */

[data-testid="stDataFrame"] {
    border: 1px solid #DCE5F0;
    border-radius: 10px;
    overflow: hidden;
}

/* FOOTER */

.footer {
    color: #96A2B3;
    text-align: center;
    font-size: 10px;
    padding: 15px 0 5px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. CONSTANTS
# =====================================================

NAVIGATION = [
    "Summary",
    "Loan Types",
    "Banks",
    "Executives",
    "Records",
    "KPI Metrics"
]

REQUIRED_COLUMNS = [
    "Customer Name",
    "Type of Loan",
    "Status",
    "Loan Amount",
    "Bank Name",
    "Executive Name",
    "Date"
]

COLORS = [
    "#4778E8",
    "#28C979",
    "#8951F5",
    "#F13D91",
    "#F5AD3D",
    "#24A9C5",
    "#8393AA"
]

STATUS_STYLES = {
    "Disbursed": ("#E0F6EC", "#16865B"),
    "Approved": ("#E7F0FF", "#3269D1"),
    "Pending": ("#FFF2D8", "#A66A00"),
    "Rejected": ("#FFE6EB", "#CF4260"),
    "Under Review": ("#F0E9FF", "#8152C9")
}


# =====================================================
# 4. DATA CLEANING
# =====================================================

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


# =====================================================
# 5. HELPER FUNCTIONS
# =====================================================

def safe(value):
    return html.escape(str(value))


def format_crore(value):
    return f"₹{value / 10000000:.2f} Cr"


def format_money(value):
    return f"₹{value:,.0f}"


def show_kpi(label, value, note):

    st.html(f"""
    <div class="kpi-card">
        <div class="kpi-label">{safe(label)}</div>
        <div class="kpi-value">{safe(value)}</div>
        <div class="kpi-note">{safe(note)}</div>
    </div>
    """)


def card_heading(title, subtitle=""):

    st.html(f"""
    <div class="card-heading">{safe(title)}</div>
    <div class="card-subheading">{safe(subtitle)}</div>
    """)


def chart_theme(fig, height=260):

    fig.update_layout(
        height=height,
        autosize=True,
        margin=dict(l=15, r=15, t=25, b=25),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, Arial",
            size=10,
            color="#75849A"
        ),
        hoverlabel=dict(
            bgcolor="#173253",
            font_color="#FFFFFF",
            bordercolor="#173253"
        ),
        legend=dict(
            font=dict(size=9, color="#65758C"),
            bgcolor="#FFFFFF",
            borderwidth=0
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#E5EAF1",
        tickfont=dict(size=9, color="#8291A6"),
        automargin=True
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#E5EAF1",
        tickfont=dict(size=9, color="#8291A6"),
        automargin=True
    )

    return fig


def show_chart(fig, height=260, key=None):

    fig = chart_theme(fig, height)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True
        },
        key=key
    )


# =====================================================
# 6. UPLOAD PAGE
# =====================================================

if "loan_df" not in st.session_state:

    # The upload page uses st.html() to render HTML.
    # The top spacing is controlled by block-container CSS.

    st.html("""
    <div style="
        max-width:680px;
        margin:20px auto 25px;
        text-align:center;
        font-family:Inter,Arial,sans-serif;
    ">
        <div style="
            color:#4778E8;
            font-size:12px;
            font-weight:800;
            letter-spacing:3px;
        ">
            JR FINANCIAL
        </div>

        <h1 style="
            color:#172B4D;
            font-size:36px;
            font-weight:800;
            margin:12px 0;
        ">
            Loan Portfolio Analytics
        </h1>

        <p style="
            color:#71829C;
            font-size:14px;
            margin-top:8px;
        ">
            Enterprise Banking Intelligence Platform
        </p>

        <p style="
            color:#71829C;
            font-size:13px;
            margin-top:18px;
        ">
            Upload your loan records to explore portfolio
            performance, application status and trends.
        </p>
    </div>
    """)

    with st.container(border=True):

        st.html("""
        <div style="padding:5px 0 8px;">
            <div style="
                color:#172B4D;
                font-size:17px;
                font-weight:750;
            ">
                Upload Loan Portfolio
            </div>
            <div style="
                color:#8291A6;
                font-size:11px;
                margin-top:5px;
            ">
                Select your Excel workbook to open the dashboard.
            </div>
        </div>
        """)

        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=["xlsx"],
            key="landing_upload"
        )

        if uploaded_file is not None:

            try:
                raw_data = pd.read_excel(uploaded_file)
                cleaned = clean_loan_data(raw_data)

                if cleaned.empty:
                    st.error("No valid records found in this workbook.")

                else:
                    st.session_state["loan_df"] = cleaned
                    st.session_state["loan_filename"] = uploaded_file.name
                    st.rerun()

            except Exception as e:
                st.error(f"Upload error: {e}")

    st.stop()


# =====================================================
# 7. LOAD DATA
# =====================================================

df = st.session_state["loan_df"].copy()

df["Month"] = df["Date"].dt.to_period("M")
df["Month Year"] = df["Month"].astype(str)


# =====================================================
# 8. SIDEBAR NAVIGATION
# =====================================================

st.sidebar.html("""
<div class="brand-box">
    <div class="brand-kicker">JR FINANCIAL</div>
    <div class="brand-title">Portfolio BI</div>
    <div class="brand-subtitle">LOAN PORTFOLIO MANAGEMENT</div>
</div>
""")

st.sidebar.html("""
<div style="
    font-size:10px;
    color:#8795A9;
    font-weight:800;
    letter-spacing:1.5px;
    margin-bottom:8px;
">
    MAIN MENU
</div>
""")

page = st.sidebar.radio(
    "Navigation",
    NAVIGATION,
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.html("""
<div style="
    font-size:10px;
    color:#8795A9;
    font-weight:800;
    letter-spacing:1px;
">
    DATA SOURCE
</div>
""")

st.sidebar.caption(
    st.session_state.get("loan_filename", "Excel workbook")
)

st.sidebar.caption(f"{len(df):,} records loaded")

if st.sidebar.button("Upload Another File", use_container_width=True):

    for key in ["loan_df", "loan_filename", "landing_upload"]:
        st.session_state.pop(key, None)

    st.rerun()


# =====================================================
# 9. PAGE-WISE FILTERS
# =====================================================

PAGE_FILTERS = {
    "Summary": [
        "Date Range", "Bank", "Loan Type", "Status", "Executive"
    ],
    "Loan Types": [
        "Date Range", "Loan Type", "Status", "Bank"
    ],
    "Banks": [
        "Date Range", "Bank", "Loan Type", "Status"
    ],
    "Executives": [
        "Date Range", "Executive", "Loan Type", "Status"
    ],
    "Records": [
        "Date Range", "Customer", "Status",
        "Bank", "Loan Type", "Executive"
    ],
    "KPI Metrics": [
        "Date Range", "Bank", "Loan Type", "Executive"
    ]
}

FILTER_COLUMNS = {
    "Bank": "Bank Name",
    "Loan Type": "Type of Loan",
    "Status": "Status",
    "Executive": "Executive Name"
}


def reset_page_filters(selected_page):

    prefix = selected_page.lower().replace(" ", "_")

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


def display_filters(data, selected_page):

    filters = PAGE_FILTERS[selected_page]
    prefix = selected_page.lower().replace(" ", "_")

    result = data.copy()

    st.html("""
    <div class="filter-label">
        FILTERS FOR THIS PAGE
    </div>
    """)

    columns = st.columns(
        [1] * len(filters) + [0.65],
        gap="small"
    )

    for i, filter_name in enumerate(filters):

        with columns[i]:

            if filter_name == "Date Range":

                selected_dates = st.date_input(
                    "Date Range",
                    value=(
                        data["Date"].min().date(),
                        data["Date"].max().date()
                    ),
                    key=f"{prefix}_date"
                )

                if (
                    isinstance(selected_dates, (tuple, list))
                    and len(selected_dates) == 2
                ):

                    start_date, end_date = selected_dates

                    if start_date > end_date:
                        st.error("Start date must be before end date.")
                        st.stop()

                    result = result[
                        (result["Date"].dt.date >= start_date)
                        & (result["Date"].dt.date <= end_date)
                    ]

                else:
                    st.info("Select both dates.")
                    st.stop()

            elif filter_name in FILTER_COLUMNS:

                column_name = FILTER_COLUMNS[filter_name]
                key_name = filter_name.lower().replace(" ", "_")

                options = sorted(
                    data[column_name].dropna().unique().tolist()
                )

                all_label = f"All {filter_name}s"

                selected_value = st.selectbox(
                    filter_name,
                    [all_label] + options,
                    key=f"{prefix}_{key_name}"
                )

                if selected_value != all_label:
                    result = result[
                        result[column_name] == selected_value
                    ]

            elif filter_name == "Customer":

                search = st.text_input(
                    "Customer Name",
                    placeholder="Search customer",
                    key=f"{prefix}_customer"
                )

                if search.strip():

                    result = result[
                        result["Customer Name"].str.contains(
                            search.strip(),
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

    return result


# =====================================================
# 10. PAGE HEADER
# =====================================================

PAGE_TITLES = {
    "Summary": "Loan Portfolio Dashboard",
    "Loan Types": "Loan Type Analysis",
    "Banks": "Bank Performance",
    "Executives": "Executive Performance",
    "Records": "Loan Application Records",
    "KPI Metrics": "Portfolio KPI Metrics"
}

PAGE_SUBTITLES = {
    "Summary": "Executive overview · All business teams",
    "Loan Types": "Loan category trends and portfolio distribution",
    "Banks": "Bank-wise funding and application performance",
    "Executives": "Executive-wise portfolio and productivity",
    "Records": "Search, review and export loan applications",
    "KPI Metrics": "Financial and operational performance indicators"
}

st.html(f"""
<div class="page-title">{safe(PAGE_TITLES[page])}</div>
<div class="page-subtitle">{safe(PAGE_SUBTITLES[page])}</div>
""")


# =====================================================
# 11. APPLY FILTERS
# =====================================================

filtered = display_filters(df, page)

if filtered.empty:
    st.warning("No records found for the selected filters.")
    st.stop()


# =====================================================
# 12. COMMON METRICS
# =====================================================

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


# =====================================================
# 13. SUMMARY PAGE
# =====================================================

if page == "Summary":

    left, right = st.columns([1.5, 1], gap="small")

    with left:

        with st.container(border=True):

            card_heading(
                "Monthly funding recorded",
                "Loan portfolio value by month · Selected period"
            )

            monthly_data = filtered.copy()

            monthly_data["Month"] = (
                monthly_data["Date"].dt.to_period("M")
            )

            monthly = (
                monthly_data
                .groupby("Month", as_index=False)
                .agg(Total_Funding=("Loan Amount", "sum"))
                .sort_values("Month")
            )

            if not monthly.empty:

                monthly["Month Label"] = (
                    monthly["Month"].astype(str)
                )

                monthly["Funding Cr"] = (
                    monthly["Total_Funding"] / 10000000
                )

                fig = px.bar(
                    monthly,
                    x="Month Label",
                    y="Funding Cr",
                    text="Funding Cr",
                    color_discrete_sequence=["#4778E8"]
                )

                fig.update_traces(
                    texttemplate="%{text:.2f}",
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Funding: ₹%{y:.2f} Cr"
                        "<extra></extra>"
                    ),
                    cliponaxis=False
                )

                fig.update_layout(
                    showlegend=False,
                    xaxis_title=None,
                    yaxis_title="₹ Crores",
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="#EDF1F6",
                        zeroline=False
                    )
                )

                show_chart(fig, 260, "monthly_funding_chart")

            else:
                st.info("No monthly funding data is available.")

            st.caption(
                "₹ Cr · Aggregated from loan application dates"
            )

    with right:

        with st.container(border=True):

            card_heading(
                "Current stage distribution",
                "Application count and requested loan amount"
            )

            for status in [
                "Approved",
                "Disbursed",
                "Pending",
                "Under Review",
                "Rejected"
            ]:

                subset = filtered[
                    filtered["Status"].str.lower() == status.lower()
                ]

                count = len(subset)
                amount = subset["Loan Amount"].sum()

                bg, fg = STATUS_STYLES[status]

                st.html(f"""
                <div class="status-row">
                    <div class="status-left">
                        <span class="status-pill"
                            style="background:{bg};color:{fg};">
                            {safe(status)}
                        </span>
                        <span class="status-count">
                            {count} applications
                        </span>
                    </div>
                    <div class="status-amount">
                        {format_crore(amount)}
                    </div>
                </div>
                """)

            st.html("""
            <p style="
                font-size:10px;
                color:#8291A6;
                margin-top:12px;
            ">
                Stage totals use requested proposal amounts.
                Disbursed amounts are tracked separately.
            </p>
            """)

    left, right = st.columns([1.5, 1], gap="small")

    with left:

        with st.container(border=True):

            card_heading(
                "Priority actions",
                "Applications requiring attention"
            )

            action_data = filtered[
                filtered["Status"].str.lower().isin(
                    ["pending", "under review"]
                )
            ].copy()

            action_data = action_data.sort_values(
                "Date",
                ascending=True
            ).head(5)

            if action_data.empty:

                st.html("""
                <div style="
                    text-align:center;
                    color:#8291A6;
                    font-size:12px;
                    padding:45px 0;
                ">
                    No open actions.
                </div>
                """)

            else:

                for _, row in action_data.iterrows():

                    status = row["Status"]

                    bg, fg = STATUS_STYLES.get(
                        status,
                        ("#EEF2F7", "#536780")
                    )

                    st.html(f"""
                    <div class="action-row">
                        <div>
                            <div class="action-name">
                                {safe(row["Customer Name"])}
                            </div>
                            <div class="action-detail">
                                {safe(row["Type of Loan"])}
                                · {safe(row["Bank Name"])}
                                · {row["Date"].strftime("%d %b %Y")}
                            </div>
                        </div>
                        <span class="action-tag"
                            style="background:{bg};color:{fg};">
                            {safe(status)}
                        </span>
                    </div>
                    """)

    with right:

        with st.container(border=True):

            executive_counts = (
                filtered.groupby("Executive Name")
                .size()
                .reset_index(name="Applications")
                .sort_values("Applications", ascending=False)
            )

            total_cases = executive_counts["Applications"].sum()

            card_heading(
                "Business Team Cases",
                f"{total_cases:,} applications"
            )

            if not executive_counts.empty:

                fig = go.Figure(
                    go.Pie(
                        labels=executive_counts["Executive Name"],
                        values=executive_counts["Applications"],
                        hole=0.67,
                        sort=False,
                        marker=dict(
                            colors=COLORS * (
                                len(executive_counts) // len(COLORS) + 1
                            ),
                            line=dict(color="#FFFFFF", width=3)
                        ),
                        textinfo="none",
                        hovertemplate=(
                            "%{label}<br>"
                            "Applications: %{value}"
                            "<extra></extra>"
                        )
                    )
                )

                fig.update_layout(
                    annotations=[
                        dict(
                            text=f"<b>{total_cases}</b>",
                            x=0.5,
                            y=0.53,
                            font=dict(size=28, color="#172B4D"),
                            showarrow=False
                        ),
                        dict(
                            text="Total cases",
                            x=0.5,
                            y=0.40,
                            font=dict(size=10, color="#8291A6"),
                            showarrow=False
                        )
                    ],
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        x=0.95,
                        y=0.5,
                        xanchor="left",
                        font=dict(size=9),
                        bgcolor="#FFFFFF"
                    ),
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF"
                )

                show_chart(fig, 230, "business_team_chart")


# =====================================================
# 14. LOAN TYPES PAGE
# =====================================================

elif page == "Loan Types":

    summary = (
        filtered.groupby("Type of Loan")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum"),
            Average_Loan=("Loan Amount", "mean")
        )
        .reset_index()
        .sort_values("Loan_Amount", ascending=False)
    )

    a, b, c = st.columns(3)

    with a:
        show_kpi("LOAN CATEGORIES", str(len(summary)), "Categories in selection")

    with b:
        show_kpi("APPLICATIONS", f"{total_apps:,}", "Total applications")

    with c:
        show_kpi("TOTAL FUNDING", format_crore(total_amount), "Requested loan amount")

    left, right = st.columns(2)

    with left:

        with st.container(border=True):

            card_heading("Loan amount by category")

            chart_data = summary.sort_values("Loan_Amount")

            fig = px.bar(
                chart_data,
                x="Loan_Amount",
                y="Type of Loan",
                orientation="h",
                color_discrete_sequence=["#4778E8"]
            )

            fig.update_traces(
                hovertemplate="%{y}<br>Amount: ₹%{x:,.0f}<extra></extra>"
            )

            show_chart(fig, 320, "loan_type_amount")

    with right:

        with st.container(border=True):

            card_heading("Applications by loan category")

            fig = px.pie(
                summary,
                names="Type of Loan",
                values="Applications",
                hole=0.62,
                color_discrete_sequence=COLORS
            )

            fig.update_traces(textinfo="percent")

            show_chart(fig, 320, "loan_type_distribution")

    st.markdown("#### Loan Category Details")

    display = summary.copy()
    display["Loan_Amount"] = display["Loan_Amount"].apply(format_money)
    display["Average_Loan"] = display["Average_Loan"].apply(format_money)

    st.dataframe(display, use_container_width=True, hide_index=True)


# =====================================================
# 15. BANKS PAGE
# =====================================================

elif page == "Banks":

    summary = (
        filtered.groupby("Bank Name")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum"),
            Average_Loan=("Loan Amount", "mean")
        )
        .reset_index()
        .sort_values("Loan_Amount", ascending=False)
    )

    a, b, c = st.columns(3)

    with a:
        show_kpi("BANKS", str(len(summary)), "Banks in selection")

    with b:
        show_kpi("APPLICATIONS", f"{total_apps:,}", "Total applications")

    with c:
        show_kpi("TOTAL FUNDING", format_crore(total_amount), "Loan portfolio")

    left, right = st.columns(2)

    with left:

        with st.container(border=True):

            card_heading("Bank-wise loan funding")

            chart_data = summary.sort_values("Loan_Amount")

            fig = px.bar(
                chart_data,
                x="Loan_Amount",
                y="Bank Name",
                orientation="h",
                color_discrete_sequence=["#4778E8"]
            )

            show_chart(fig, 340, "bank_funding")

    with right:

        with st.container(border=True):

            card_heading("Applications by bank")

            fig = px.pie(
                summary,
                names="Bank Name",
                values="Applications",
                hole=0.62,
                color_discrete_sequence=COLORS
            )

            show_chart(fig, 340, "bank_applications")

    st.markdown("#### Bank Performance Details")

    display = summary.copy()
    display["Loan_Amount"] = display["Loan_Amount"].apply(format_money)
    display["Average_Loan"] = display["Average_Loan"].apply(format_money)

    st.dataframe(display, use_container_width=True, hide_index=True)


# =====================================================
# 16. EXECUTIVES PAGE
# =====================================================

elif page == "Executives":

    summary = (
        filtered.groupby("Executive Name")
        .agg(
            Applications=("Customer Name", "count"),
            Loan_Amount=("Loan Amount", "sum"),
            Average_Loan=("Loan Amount", "mean")
        )
        .reset_index()
        .sort_values("Applications", ascending=False)
    )

    a, b, c = st.columns(3)

    with a:
        show_kpi("EXECUTIVES", str(len(summary)), "Active executives")

    with b:
        show_kpi("APPLICATIONS", f"{total_apps:,}", "Managed applications")

    with c:
        show_kpi("TOTAL FUNDING", format_crore(total_amount), "Loan portfolio")

    left, right = st.columns(2)

    with left:

        with st.container(border=True):

            card_heading("Executive-wise loan portfolio")

            chart_data = summary.sort_values("Loan_Amount")

            fig = px.bar(
                chart_data,
                x="Loan_Amount",
                y="Executive Name",
                orientation="h",
                color_discrete_sequence=["#28A879"]
            )

            show_chart(fig, 340, "executive_funding")

    with right:

        with st.container(border=True):

            card_heading("Executive-wise application distribution")

            fig = go.Figure(
                go.Pie(
                    labels=summary["Executive Name"],
                    values=summary["Applications"],
                    hole=0.65,
                    marker=dict(
                        colors=COLORS * (
                            len(summary) // len(COLORS) + 1
                        ),
                        line=dict(color="#FFFFFF", width=3)
                    )
                )
            )

            fig.update_layout(
                annotations=[
                    dict(
                        text=f"<b>{total_apps}</b>",
                        x=0.5,
                        y=0.52,
                        font=dict(size=27, color="#172B4D"),
                        showarrow=False
                    ),
                    dict(
                        text="Applications",
                        x=0.5,
                        y=0.39,
                        font=dict(size=10, color="#8291A6"),
                        showarrow=False
                    )
                ],
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF"
            )

            show_chart(fig, 340, "executive_distribution")

    st.markdown("#### Executive Performance Details")

    display = summary.copy()
    display["Loan_Amount"] = display["Loan_Amount"].apply(format_money)
    display["Average_Loan"] = display["Average_Loan"].apply(format_money)

    st.dataframe(display, use_container_width=True, hide_index=True)


# =====================================================
# 17. RECORDS PAGE
# =====================================================

elif page == "Records":

    with st.container(border=True):

        card_heading(
            "Loan Application Database",
            f"{len(filtered):,} matching records"
        )

        display = filtered.copy()
        display["Date"] = display["Date"].dt.strftime("%d-%b-%Y")

        st.dataframe(
            display,
            use_container_width=True,
            height=470,
            hide_index=True
        )

        st.download_button(
            "Download Filtered Records",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="JR_Financial_Loan_Records.csv",
            mime="text/csv"
        )


# =====================================================
# 18. KPI METRICS PAGE
# =====================================================

elif page == "KPI Metrics":

    a, b, c, d = st.columns(4)

    with a:
        show_kpi(
            "TOTAL APPLICATIONS",
            f"{total_apps:,}",
            "Selected applications"
        )

    with b:
        show_kpi(
            "APPROVAL RATE",
            f"{approval_rate:.1f}%",
            "Approved / total"
        )

    with c:
        show_kpi(
            "DISBURSEMENT RATE",
            f"{disbursement_rate:.1f}%",
            "Disbursed / total"
        )

    with d:
        show_kpi(
            "AVERAGE LOAN",
            format_money(average_loan),
            "Average loan amount"
        )

    left, right = st.columns(2)

    with left:

        with st.container(border=True):

            card_heading("Application status comparison")

            status_data = (
                filtered["Status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = ["Status", "Applications"]

            fig = px.bar(
                status_data,
                x="Status",
                y="Applications",
                color="Status",
                color_discrete_sequence=COLORS
            )

            fig.update_layout(showlegend=False)

            show_chart(fig, 300, "kpi_status_chart")

    with right:

        with st.container(border=True):

            card_heading("Financial portfolio distribution")

            financial = pd.DataFrame({
                "Category": [
                    "Disbursed",
                    "Other applications"
                ],
                "Amount": [
                    disbursed_amount,
                    max(total_amount - disbursed_amount, 0)
                ]
            })

            fig = px.pie(
                financial,
                names="Category",
                values="Amount",
                hole=0.65,
                color_discrete_sequence=["#28C979", "#4778E8"]
            )

            show_chart(fig, 300, "kpi_financial_chart")

    a, b, c = st.columns(3)

    with a:
        st.metric("Total Loan Amount", format_crore(total_amount))

    with b:
        st.metric("Disbursed Amount", format_crore(disbursed_amount))

    with c:
        st.metric(
            "Unique Customers",
            f"{filtered['Customer Name'].nunique():,}"
        )


# =====================================================
# 19. FOOTER
# =====================================================

st.html("""
<div class="footer">
    JR FINANCIAL · ENTERPRISE LOAN PORTFOLIO ANALYTICS
</div>
""")
