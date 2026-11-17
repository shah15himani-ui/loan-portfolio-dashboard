
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import html

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DESIGN / CSS
# =========================================================

st.html("""
<style>
.stApp {
    background: #F0F1F5;
    color: #172B4D;
}

.block-container {
    padding: 1rem 1.3rem 0.5rem 1.3rem;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background: #192B4D;
}

[data-testid="stSidebar"] > div:first-child {
    background: #192B4D;
}

[data-testid="stSidebar"] * {
    color: #E8EEF9;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 7px 10px;
    border-radius: 7px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #2C4168;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    font-size: 13px;
}

.sidebar-brand {
    padding: 12px 8px 24px 8px;
}

.sidebar-brand .small {
    font-size: 10px;
    letter-spacing: 2px;
    color: #8FA9D4;
    font-weight: 700;
}

.sidebar-brand .large {
    font-size: 21px;
    font-weight: 800;
    color: white;
    margin-top: 5px;
}

.page-title {
    font-size: 23px;
    font-weight: 750;
    color: #263653;
    margin-bottom: 2px;
}

.page-subtitle {
    color: #8490A5;
    font-size: 11px;
    margin-bottom: 14px;
}

.kpi-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 13px 14px;
    min-height: 100px;
    border: 1px solid #E8EAF0;
    box-shadow: 0 2px 7px rgba(25,43,77,0.04);
}

.kpi-label {
    font-size: 10px;
    font-weight: 700;
    color: #8590A3;
    letter-spacing: .5px;
}

.kpi-value {
    font-size: 24px;
    color: #263653;
    font-weight: 800;
    margin-top: 7px;
}

.kpi-note {
    font-size: 10px;
    color: #1E9C72;
    margin-top: 4px;
}

.panel {
    background: white;
    border: 1px solid #E8EAF0;
    border-radius: 10px;
    padding: 10px 12px 4px 12px;
    box-shadow: 0 2px 7px rgba(25,43,77,0.035);
    margin-bottom: 8px;
}

.panel-title {
    color: #34435D;
    font-size: 12px;
    font-weight: 750;
    margin-bottom: 3px;
}

.section-label {
    color: #8994A7;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 12px 0 7px 2px;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stTextInput"] label {
    font-size: 11px;
    color: #64748B;
    font-weight: 600;
}

.stButton button {
    border-radius: 7px;
    font-weight: 600;
}

[data-testid="stDataFrame"] {
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
            "Missing columns: " + ", ".join(missing)
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
            data[col].fillna("")
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
# HELPER FUNCTIONS
# =========================================================

def crore(value):
    return f"₹{value / 10000000:.2f} Cr"


def money(value):
    return f"₹{value:,.0f}"


def kpi_card(label, value, note="Portfolio overview"):

    st.html(f"""
    <div class="kpi-card">
        <div class="kpi-label">{html.escape(str(label))}</div>
        <div class="kpi-value">{html.escape(str(value))}</div>
        <div class="kpi-note">{html.escape(str(note))}</div>
    </div>
    """)


def panel_title(title):
    st.html(f"""
    <div class="panel-title">
        {html.escape(str(title))}
    </div>
    """)


def style_chart(fig, height=220):

    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=12, b=8),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=10,
            color="#68758B"
        ),
        legend=dict(
            font=dict(size=9),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hoverlabel=dict(
            bgcolor="#192B4D",
            font_color="white"
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EEF0F5",
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False
    )

    return fig


def show_chart(fig, height=220):

    st.plotly_chart(
        style_chart(fig, height),
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
        margin:85px auto 30px auto;
        text-align:center;
    ">
        <div style="
            color:#2563EB;
            font-size:12px;
            font-weight:700;
            letter-spacing:2px;
            margin-bottom:12px;
        ">
            LOAN PORTFOLIO MANAGEMENT
        </div>

        <h1 style="
            font-size:38px;
            color:#172B4D;
            margin-bottom:12px;
        ">
            Loan Portfolio Analytics
        </h1>

        <p style="
            color:#64748B;
            font-size:16px;
        ">
            Upload your loan records to explore portfolio
            performance, application status and trends.
        </p>
    </div>
    """)

    upload = st.file_uploader(
        "Upload your Excel workbook",
        type=["xlsx"]
    )

    if upload:

        try:
            raw = pd.read_excel(upload)
            cleaned = clean_loan_data(raw)

            if cleaned.empty:
                st.error("No valid loan records found.")
            else:
                st.session_state["loan_df"] = cleaned
                st.session_state["loan_filename"] = upload.name
                st.rerun()

        except Exception as e:
            st.error(f"Upload error: {e}")

    st.stop()


# =========================================================
# LOAD DATA
# =========================================================

df = st.session_state["loan_df"].copy()

df["Month"] = df["Date"].dt.to_period("M")
df["Month Year"] = df["Month"].astype(str)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.html("""
<div class="sidebar-brand">
    <div class="small">LOAN PORTFOLIO</div>
    <div class="large">Analytics</div>
</div>
""")

st.sidebar.caption("MAIN MENU")

page = st.sidebar.radio(
    "Navigation",
    [
        "Summary",
        "Loan Types",
        "Banks",
        "Executives",
        "Records",
        "KPI Metrics"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.caption(
    f"DATA SOURCE: {st.session_state.get('loan_filename', 'Excel file')}"
)

if st.sidebar.button(
    "Upload Another File",
    use_container_width=True
):

    for key in ["loan_df", "loan_filename"]:
        st.session_state.pop(key, None)

    st.rerun()


# =========================================================
# TOP FILTERS
# =========================================================

st.html("""
<div class="page-title">Loan Portfolio Analytics</div>
<div class="page-subtitle">
    Interactive portfolio monitoring and performance dashboard
</div>
""")

f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 1.5])

with f1:
    bank = st.selectbox(
        "Bank",
        ["All Banks"] + sorted(df["Bank Name"].unique().tolist())
    )

with f2:
    loan_type = st.selectbox(
        "Loan Type",
        ["All Loan Types"] + sorted(df["Type of Loan"].unique().tolist())
    )

with f3:
    status = st.selectbox(
        "Status",
        ["All Statuses"] + sorted(df["Status"].unique().tolist())
    )

with f4:
    search = st.text_input(
        "Search Customer",
        placeholder="Customer name..."
    )


# Date filter
date_col1, date_col2, reset_col = st.columns([1, 1, 3])

with date_col1:
    start_date = st.date_input(
        "From Date",
        value=df["Date"].min().date()
    )

with date_col2:
    end_date = st.date_input(
        "To Date",
        value=df["Date"].max().date()
    )

with reset_col:
    st.write("")
    st.write("")
    if st.button("Reset Filters"):
        st.rerun()


# =========================================================
# APPLY FILTERS
# =========================================================

filtered = df.copy()

if bank != "All Banks":
    filtered = filtered[filtered["Bank Name"] == bank]

if loan_type != "All Loan Types":
    filtered = filtered[filtered["Type of Loan"] == loan_type]

if status != "All Statuses":
    filtered = filtered[filtered["Status"] == status]

if search.strip():
    filtered = filtered[
        filtered["Customer Name"].str.contains(
            search.strip(),
            case=False,
            na=False
        )
    ]

if start_date > end_date:
    st.error("Start date cannot be after end date.")
    st.stop()

filtered = filtered[
    (filtered["Date"].dt.date >= start_date)
    & (filtered["Date"].dt.date <= end_date)
]


if filtered.empty:
    st.warning("No records found for the selected filters.")
    st.stop()


# =========================================================
# COMMON METRICS
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


# =========================================================
# SUMMARY PAGE
# =========================================================

if page == "Summary":

    st.html('<div class="section-label">PORTFOLIO OVERVIEW</div>')

    a, b, c, d = st.columns(4, gap="small")

    with a:
        kpi_card(
            "TOTAL APPLICATIONS",
            f"{total_apps:,}",
            "Applications in selected period"
        )

    with b:
        kpi_card(
            "TOTAL LOAN AMOUNT",
            crore(total_amount),
            "Total applied loan value"
        )

    with c:
        kpi_card(
            "DISBURSED AMOUNT",
            crore(disbursed_amount),
            "Successfully disbursed"
        )

    with d:
        kpi_card(
            "PENDING APPLICATIONS",
            f"{len(pending):,}",
            "Awaiting further action"
        )

    # -----------------------------------------------------
    # CHART ROW 1
    # -----------------------------------------------------

    st.html('<div class="section-label">PORTFOLIO PERFORMANCE</div>')

    c1, c2 = st.columns([1.45, 1])

    with c1:

        with st.container(border=True):
            panel_title("Monthly Loan Amount Trend")

            monthly = (
                filtered.groupby("Month")["Loan Amount"]
                .sum()
                .reset_index()
                .sort_values("Month")
            )

            monthly["Month"] = monthly["Month"].astype(str)

            fig = px.line(
                monthly,
                x="Month",
                y="Loan Amount",
                markers=True
            )

            fig.update_traces(
                line=dict(color="#BE3455", width=3),
                marker=dict(size=7),
                fill="tozeroy",
                fillcolor="rgba(190,52,85,0.08)"
            )

            fig.update_layout(
                xaxis_title="",
                yaxis_title="Loan Amount",
                showlegend=False
            )

            show_chart(fig, 235)

    with c2:

        with st.container(border=True):
            panel_title("Application Status Breakdown")

            status_data = (
                filtered["Status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = ["Status", "Applications"]

            fig = px.pie(
                status_data,
                names="Status",
                values="Applications",
                hole=0.62,
                color_discrete_sequence=[
                    "#BE3455",
                    "#E58BA2",
                    "#D8D8D8",
                    "#263B60",
                    "#7D91B3"
                ]
            )

            fig.update_traces(
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>Applications: %{value}<extra></extra>"
            )

            show_chart(fig, 235)

    # -----------------------------------------------------
    # CHART ROW 2
    # -----------------------------------------------------

    c3, c4 = st.columns(2)

    with c3:

        with st.container(border=True):
            panel_title("Top 5 Loan Types")

            loan_data = (
                filtered.groupby("Type of Loan")["Loan Amount"]
                .sum()
                .nlargest(5)
                .reset_index()
                .sort_values("Loan Amount")
            )

            fig = px.bar(
                loan_data,
                x="Loan Amount",
                y="Type of Loan",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=["#BE3455"]
            )

            fig.update_layout(
                xaxis_title="Loan Amount",
                yaxis_title=""
            )

            show_chart(fig, 205)

    with c4:

        with st.container(border=True):
            panel_title("Bank-wise Loan Distribution")

            bank_data = (
                filtered.groupby("Bank Name")["Loan Amount"]
                .sum()
                .nlargest(5)
                .reset_index()
                .sort_values("Loan Amount")
            )

            fig = px.bar(
                bank_data,
                x="Loan Amount",
                y="Bank Name",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=["#263B60"]
            )

            fig.update_layout(
                xaxis_title="Loan Amount",
                yaxis_title=""
            )

            show_chart(fig, 205)

    # -----------------------------------------------------
    # CHART ROW 3
    # -----------------------------------------------------

    c5, c6 = st.columns(2)

    with c5:

        with st.container(border=True):
            panel_title("Executive Performance")

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
                text_auto=".2s",
                color_discrete_sequence=["#BE3455"]
            )

            fig.update_layout(
                xaxis_title="Loan Amount",
                yaxis_title=""
            )

            show_chart(fig, 205)

    with c6:

        with st.container(border=True):
            panel_title("Top 5 Customers")

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
                text_auto=".2s",
                color_discrete_sequence=["#263B60"]
            )

            fig.update_layout(
                xaxis_title="Loan Amount",
                yaxis_title=""
            )

            show_chart(fig, 205)


# =========================================================
# LOAN TYPES PAGE
# =========================================================

elif page == "Loan Types":

    st.html('<div class="section-label">LOAN TYPE ANALYSIS</div>')

    loan_summary = (
        filtered.groupby("Type of Loan")
        .agg(
            Applications=("Customer Name", "count"),
            Total_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            panel_title("Loan Amount by Type")

            fig = px.bar(
                loan_summary.sort_values("Total_Amount"),
                x="Total_Amount",
                y="Type of Loan",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=["#BE3455"]
            )

            show_chart(fig, 360)

    with right:
        with st.container(border=True):
            panel_title("Application Share by Loan Type")

            fig = px.pie(
                loan_summary,
                names="Type of Loan",
                values="Applications",
                hole=0.55
            )

            show_chart(fig, 360)

    st.dataframe(
        loan_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# BANKS PAGE
# =========================================================

elif page == "Banks":

    st.html('<div class="section-label">BANK PERFORMANCE</div>')

    bank_summary = (
        filtered.groupby("Bank Name")
        .agg(
            Applications=("Customer Name", "count"),
            Total_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            panel_title("Bank-wise Loan Amount")

            fig = px.bar(
                bank_summary.sort_values("Total_Amount"),
                x="Total_Amount",
                y="Bank Name",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=["#263B60"]
            )

            show_chart(fig, 360)

    with right:
        with st.container(border=True):
            panel_title("Applications by Bank")

            fig = px.pie(
                bank_summary,
                names="Bank Name",
                values="Applications",
                hole=0.55
            )

            show_chart(fig, 360)

    st.dataframe(
        bank_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# EXECUTIVES PAGE
# =========================================================

elif page == "Executives":

    st.html('<div class="section-label">EXECUTIVE PERFORMANCE</div>')

    executive_summary = (
        filtered.groupby("Executive Name")
        .agg(
            Applications=("Customer Name", "count"),
            Total_Amount=("Loan Amount", "sum")
        )
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            panel_title("Executive-wise Loan Amount")

            fig = px.bar(
                executive_summary.sort_values("Total_Amount"),
                x="Total_Amount",
                y="Executive Name",
                orientation="h",
                text_auto=".2s",
                color_discrete_sequence=["#BE3455"]
            )

            show_chart(fig, 360)

    with right:
        with st.container(border=True):
            panel_title("Executive Application Share")

            fig = px.pie(
                executive_summary,
                names="Executive Name",
                values="Applications",
                hole=0.55
            )

            show_chart(fig, 360)

    st.dataframe(
        executive_summary,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# RECORDS PAGE
# =========================================================

elif page == "Records":

    st.html('<div class="section-label">DETAILED LOAN RECORDS</div>')

    display_df = filtered.copy()

    display_df["Date"] = display_df["Date"].dt.strftime("%d-%b-%Y")

    st.caption(f"Showing {len(display_df):,} filtered records")

    st.dataframe(
        display_df,
        use_container_width=True,
        height=480,
        hide_index=True
    )

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Filtered Records",
        data=csv,
        file_name="loan_records.csv",
        mime="text/csv"
    )


# =========================================================
# KPI METRICS PAGE
# =========================================================

elif page == "KPI Metrics":

    st.html('<div class="section-label">KEY PERFORMANCE INDICATORS</div>')

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        kpi_card("TOTAL APPLICATIONS", total_apps)

    with k2:
        kpi_card("APPROVED APPLICATIONS", len(approved))

    with k3:
        kpi_card("DISBURSED APPLICATIONS", len(disbursed))

    with k4:
        kpi_card("PENDING APPLICATIONS", len(pending))

    st.divider()

    conversion_rate = (
        len(disbursed) / total_apps * 100
        if total_apps else 0
    )

    approval_rate = (
        len(approved) / total_apps * 100
        if total_apps else 0
    )

    st.metric(
        "Disbursement Rate",
        f"{conversion_rate:.1f}%"
    )

    st.metric(
        "Approval Rate",
        f"{approval_rate:.1f}%"
    )

    st.metric(
        "Average Loan Amount",
        money(filtered["Loan Amount"].mean())
    )

    st.metric(
        "Average Disbursed Amount",
        money(
            disbursed["Loan Amount"].mean()
            if len(disbursed) else 0
        )
    )


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div style="
    text-align:center;
    color:#98A1B2;
    font-size:10px;
    padding:12px 0 3px 0;
">
    Loan Portfolio Analytics | Interactive Dashboard
</div>
""")
