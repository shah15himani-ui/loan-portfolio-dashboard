
import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Loan Portfolio Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* MAIN APPLICATION */

.stApp {
    background-color: #F4F6FA;
    color: #24364B;
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* HEADINGS */

h1 {
    color: #172B4D !important;
    font-weight: 750 !important;
    letter-spacing: -0.5px;
}

h2, h3 {
    color: #24364B !important;
    font-weight: 650 !important;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E7ECF2;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #172B4D !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #53657B !important;
}

/* SIDEBAR EXPANDERS */

[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #F8FAFD;
    border: 1px solid #E7ECF2;
    border-radius: 10px;
    margin-bottom: 9px;
}

/* DROPDOWNS */

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #FFFFFF;
    border: 1px solid #DCE3ED;
    border-radius: 8px;
    min-height: 42px;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #26384D;
}

/* INPUTS */

[data-testid="stSidebar"] input {
    background: #FFFFFF;
    color: #26384D;
    border-radius: 8px;
}

/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background: #F8FAFD;
    border: 1px solid #E3EAF2;
    border-radius: 12px;
    padding: 12px;
}

[data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF;
    border: 2px dashed #A9C2DE;
    border-radius: 12px;
    transition: 0.2s ease;
}

[data-testid="stFileUploaderDropzone"]:hover {
    background: #EDF5FF;
    border-color: #2563EB;
}

/* BUTTONS */

.stButton button {
    background: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    min-height: 40px;
    transition: 0.2s ease;
}

.stButton button:hover {
    background: #1D4ED8;
    color: #FFFFFF;
}

/* LANDING PAGE */

.landing-container {
    background: #FFFFFF;
    border: 1px solid #E5EAF1;
    border-radius: 20px;
    padding: 35px;
    box-shadow: 0 8px 30px rgba(30, 50, 80, 0.06);
}

/* KPI CARDS */

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8EDF3;
    border-top: 4px solid #2563EB;
    border-radius: 13px;
    padding: 18px;
    min-height: 135px;
    box-shadow: 0 3px 12px rgba(30, 50, 80, 0.04);
    transition: 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 7px 18px rgba(30, 50, 80, 0.09);
}

.kpi-green {
    border-top-color: #10B981;
}

.kpi-blue {
    border-top-color: #3B82F6;
}

.kpi-orange {
    border-top-color: #F59E0B;
}

.kpi-purple {
    border-top-color: #8B5CF6;
}

.kpi-label {
    color: #77869A;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

.kpi-value {
    color: #172B4D;
    font-size: 26px;
    font-weight: 750;
    margin-bottom: 8px;
}

.kpi-note {
    color: #8996A8;
    font-size: 11px;
}

/* CHARTS */

[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid #E8EDF3;
    border-radius: 13px;
    padding: 8px;
    box-shadow: 0 3px 12px rgba(30, 50, 80, 0.03);
}

/* DATA TABLE */

[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E8EDF3;
}

/* DIVIDERS */

hr {
    border-color: #E7ECF2;
}

/* DOWNLOAD BUTTON */

.stDownloadButton button {
    background: #10B981;
    color: white;
    border-radius: 8px;
    border: none;
}

.stDownloadButton button:hover {
    background: #059669;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. DATA CLEANING FUNCTION
# =========================================================

def clean_loan_data(data):

    data = data.copy()

    # Remove completely empty columns
    data = data.dropna(axis=1, how="all")

    required_columns = [
        "Customer Name",
        "Type of Loan",
        "Status",
        "Loan Amount",
        "Bank Name",
        "Executive Name",
        "Date"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Clean text columns
    for col in data.select_dtypes(include="object").columns:
        data[col] = data[col].str.strip()

    # Convert loan amount
    data["Loan Amount"] = pd.to_numeric(
        data["Loan Amount"],
        errors="coerce"
    )

    # Convert date
    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce",
        dayfirst=True
    )

    # Remove invalid amounts and dates
    data = data.dropna(
        subset=["Loan Amount", "Date"]
    )

    if data.empty:
        raise ValueError("No valid loan records found.")

    return data



# =========================================================
# 4. LANDING PAGE
# =========================================================

if "loan_df" not in st.session_state:

    # Hide sidebar on landing page
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            padding-top: 2rem;
        }

        .upload-card {
            background: #FFFFFF;
            border: 1px solid #E5EAF1;
            border-radius: 20px;
            padding: 35px;
            text-align: center;
            box-shadow: 0 8px 30px rgba(30,50,80,0.06);
        }
    </style>
    """, unsafe_allow_html=True)

    # Landing page heading
    st.markdown("""
    <div style="
        text-align: center;
        padding: 65px 10px 35px;
    ">

        <div style="
            color: #2563EB;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 12px;
        ">
            LOAN PORTFOLIO MANAGEMENT
        </div>

        <h1 style="
            font-size: 38px;
            color: #172B4D;
            margin-bottom: 12px;
        ">
            Loan Portfolio Analytics
        </h1>

        <p style="
            color: #718096;
            font-size: 16px;
        ">
            Transform your loan data into meaningful
            insights and smarter decisions.
        </p>

    </div>
    """, unsafe_allow_html=True)

    # Center upload card
    left, center, right = st.columns([1, 1.7, 1])

    with center:

        st.markdown("""
        <div class="upload-card">

            <div style="font-size:48px; margin-bottom:15px;">
                📊
            </div>

            <h2 style="
                color:#172B4D;
                font-size:24px;
            ">
                Upload Your Loan Records
            </h2>

            <p style="
                color:#718096;
                font-size:14px;
            ">
                Select your Excel dataset to access
                your interactive analytics dashboard.
            </p>

        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose your Excel file",
            type=["xlsx"],
            key="landing_upload"
        )

        if uploaded_file is not None:

            try:

                raw_data = pd.read_excel(uploaded_file)

                cleaned_data = clean_loan_data(raw_data)

                st.session_state["loan_df"] = cleaned_data

                st.session_state["loan_filename"] = (
                    uploaded_file.name
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Unable to process your Excel file: {e}"
                )

    # Footer
    st.markdown("""
    <div style="
        text-align:center;
        color:#94A3B8;
        font-size:12px;
        margin-top:35px;
    ">
        Supported format: Excel (.xlsx)
        <br><br>
        Loan Portfolio Analytics Dashboard
    </div>
    """, unsafe_allow_html=True)

    st.stop()



# =========================================================
# 5. DASHBOARD DATA
# =========================================================

df = st.session_state["loan_df"]


# =========================================================
# 6. SIDEBAR HEADER
# =========================================================

st.sidebar.markdown("""
    <div style="
        padding:5px 0 12px;
    ">
        <div style="
            font-size:22px;
            font-weight:750;
            color:#172B4D;
        ">
            📊 Loan Analytics
        </div>

        <div style="
            color:#8996A8;
            font-size:12px;
            margin-top:5px;
        ">
            Portfolio Management Dashboard
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Current dataset: " +
    st.session_state["loan_filename"]
)

# Return to landing page
if st.sidebar.button(
    "↻ Upload Another File",
    use_container_width=True
):

    del st.session_state["loan_df"]
    del st.session_state["loan_filename"]

    if "dashboard_ready" in st.session_state:
        del st.session_state["dashboard_ready"]

    st.rerun()


# =========================================================
# 7. DASHBOARD HEADER
# =========================================================

st.title("Loan Portfolio Dashboard")

st.markdown(
    "Monitor loan applications, portfolio performance, "
    "bank activity and executive performance."
)

st.divider()


# =========================================================
# 8. FILTER OPTIONS
# =========================================================

bank_options = (
    ["All Banks"] +
    sorted(df["Bank Name"].dropna().unique().tolist())
)

loan_options = (
    ["All Loan Types"] +
    sorted(df["Type of Loan"].dropna().unique().tolist())
)

status_options = (
    ["All Statuses"] +
    sorted(df["Status"].dropna().unique().tolist())
)

executive_options = (
    ["All Executives"] +
    sorted(df["Executive Name"].dropna().unique().tolist())
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()


# =========================================================
# 9. RESET FILTER FUNCTION
# =========================================================

def reset_filters():

    st.session_state["bank_filter"] = "All Banks"

    st.session_state["loan_filter"] = "All Loan Types"

    st.session_state["status_filter"] = "All Statuses"

    st.session_state["executive_filter"] = "All Executives"

    st.session_state["date_filter"] = (
        min_date,
        max_date
    )

    st.session_state["customer_search"] = ""


# =========================================================
# 10. INTERACTIVE SIDEBAR FILTERS
# =========================================================

st.sidebar.markdown("## 🎛️ Dashboard Filters")

st.sidebar.caption(
    "Customize your loan portfolio view"
)


# BANK FILTER

with st.sidebar.expander(
    "🏦 Bank Selection",
    expanded=True
):

    selected_bank = st.selectbox(
        "Select Bank",
        bank_options,
        key="bank_filter"
    )


# LOAN FILTERS

with st.sidebar.expander(
    "💰 Loan Details",
    expanded=True
):

    selected_loan = st.selectbox(
        "Type of Loan",
        loan_options,
        key="loan_filter"
    )

    selected_status = st.selectbox(
        "Application Status",
        status_options,
        key="status_filter"
    )


# EXECUTIVE FILTER

with st.sidebar.expander(
    "👤 Executive Details",
    expanded=False
):

    selected_executive = st.selectbox(
        "Select Executive",
        executive_options,
        key="executive_filter"
    )


# DATE FILTER

with st.sidebar.expander(
    "📅 Date Range",
    expanded=False
):

    selected_dates = st.date_input(
        "Select Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )


# CUSTOMER SEARCH

with st.sidebar.expander(
    "🔍 Customer Search",
    expanded=False
):

    search = st.text_input(
        "Customer Name",
        placeholder="Search customer...",
        key="customer_search"
    )


# RESET BUTTON

st.sidebar.button(
    "↻ Reset All Filters",
    on_click=reset_filters,
    use_container_width=True
)


# =========================================================
# 11. APPLY FILTERS
# =========================================================

filtered_df = df.copy()


# Bank filter

if selected_bank != "All Banks":

    filtered_df = filtered_df[
        filtered_df["Bank Name"] == selected_bank
    ]


# Loan type filter

if selected_loan != "All Loan Types":

    filtered_df = filtered_df[
        filtered_df["Type of Loan"] == selected_loan
    ]


# Status filter

if selected_status != "All Statuses":

    filtered_df = filtered_df[
        filtered_df["Status"] == selected_status
    ]


# Executive filter

if selected_executive != "All Executives":

    filtered_df = filtered_df[
        filtered_df["Executive Name"] == selected_executive
    ]


# Date filter

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date) &
        (filtered_df["Date"].dt.date <= end_date)
    ]


# Customer search

if search:

    filtered_df = filtered_df[
        filtered_df["Customer Name"].str.contains(
            search,
            case=False,
            na=False,
            regex=False
        )
    ]


# Sidebar record count

st.sidebar.markdown("---")

st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} applications"
)


# =========================================================
# 12. KPI CALCULATIONS
# =========================================================

total_applications = len(filtered_df)

total_amount = filtered_df["Loan Amount"].sum()

disbursed_df = filtered_df[
    filtered_df["Status"] == "Disbursed"
]

disbursed_amount = disbursed_df["Loan Amount"].sum()

pending_applications = (
    filtered_df["Status"] == "Pending"
).sum()

disbursed_applications = len(disbursed_df)


# =========================================================
# 13. KPI CARDS
# =========================================================

st.subheader("Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div class="kpi-label">TOTAL APPLICATIONS</div>
        <div class="kpi-value">{total_applications:,}</div>
        <div class="kpi-note">Applications in selected records</div>
    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-label">TOTAL LOAN AMOUNT</div>
        <div class="kpi-value">₹{total_amount/10000000:.2f} Cr</div>
        <div class="kpi-note">Total portfolio value</div>
    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown(f"""
    <div class="kpi-card kpi-orange">
        <div class="kpi-label">DISBURSED AMOUNT</div>
        <div class="kpi-value">₹{disbursed_amount/10000000:.2f} Cr</div>
        <div class="kpi-note">
            {disbursed_applications} disbursed applications
        </div>
    </div>
    """, unsafe_allow_html=True)


with col4:

    st.markdown(f"""
    <div class="kpi-card kpi-purple">
        <div class="kpi-label">PENDING APPLICATIONS</div>
        <div class="kpi-value">{pending_applications:,}</div>
        <div class="kpi-note">Awaiting further action</div>
    </div>
    """, unsafe_allow_html=True)


st.write("")


# =========================================================
# 14. APPLICATION STATUS AND LOAN TYPE
# =========================================================

st.subheader("Application Analysis")

col1, col2 = st.columns(2)


# STATUS PIE CHART

with col1:

    status_data = (
        filtered_df["Status"]
        .value_counts()
        .reset_index()
    )

    status_data.columns = [
        "Status",
        "Applications"
    ]

    if not status_data.empty:

        fig1 = px.pie(
            status_data,
            names="Status",
            values="Applications",
            hole=0.48,
            title="Applications by Status",
            color_discrete_sequence=[
                "#2563EB",
                "#10B981",
                "#F59E0B",
                "#8B5CF6",
                "#EC4899"
            ]
        )

        fig1.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#24364B",
            margin=dict(l=20, r=20, t=60, b=20),
            legend_title_text=""
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    else:

        st.info("No status data available.")


# LOAN TYPE BAR CHART

with col2:

    loan_data = (
        filtered_df.groupby("Type of Loan")["Loan Amount"]
        .sum()
        .reset_index()
        .sort_values("Loan Amount", ascending=False)
    )

    if not loan_data.empty:

        fig2 = px.bar(
            loan_data,
            x="Type of Loan",
            y="Loan Amount",
            color="Type of Loan",
            title="Loan Amount by Loan Type",
            text_auto=".2s",
            color_discrete_sequence=[
                "#2563EB",
                "#10B981",
                "#F59E0B",
                "#8B5CF6",
                "#EC4899",
                "#06B6D4",
                "#64748B"
            ]
        )

        fig2.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="#24364B",
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=60)
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:

        st.info("No loan type data available.")


st.divider()


# =========================================================
# 15. BANK PERFORMANCE
# =========================================================

st.subheader("Bank Performance")

bank_data = (
    filtered_df.groupby("Bank Name")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Loan Amount", ascending=True)
)

if not bank_data.empty:

    fig3 = px.bar(
        bank_data,
        x="Loan Amount",
        y="Bank Name",
        orientation="h",
        color="Loan Amount",
        title="Loan Amount by Bank",
        text_auto=".2s",
        color_continuous_scale="Blues"
    )

    fig3.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color="#24364B",
        yaxis=dict(categoryorder="total ascending"),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

else:

    st.info("No bank data available.")


st.divider()


# =========================================================
# 16. EXECUTIVE PERFORMANCE
# =========================================================

st.subheader("Executive Performance")

executive_data = (
    filtered_df.groupby("Executive Name")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Loan Amount", ascending=False)
)

if not executive_data.empty:

    fig4 = px.bar(
        executive_data,
        x="Executive Name",
        y="Loan Amount",
        title="Loan Amount by Executive",
        color="Loan Amount",
        text_auto=".2s",
        color_continuous_scale="Teal"
    )

    fig4.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color="#24364B",
        margin=dict(l=20, r=20, t=60, b=50)
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

else:

    st.info("No executive data available.")


st.divider()


# =========================================================
# 17. MONTHLY LOAN TREND
# =========================================================

st.subheader("Monthly Loan Trend")

monthly_data = filtered_df.copy()

monthly_data["Month"] = (
    monthly_data["Date"].dt.to_period("M").astype(str)
)

monthly_data = (
    monthly_data.groupby("Month")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Month")
)

if not monthly_data.empty:

    fig5 = px.line(
        monthly_data,
        x="Month",
        y="Loan Amount",
        markers=True,
        title="Monthly Loan Amount Trend"
    )

    fig5.update_traces(
        line=dict(
            color="#2563EB",
            width=3
        ),
        marker=dict(
            color="#10B981",
            size=8
        ),
        hovertemplate=(
            "Month: %{x}<br>"
            "Loan Amount: ₹%{y:,.0f}"
            "<extra></extra>"
        )
    )

    fig5.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color="#24364B",
        xaxis_title="Month",
        yaxis_title="Loan Amount",
        margin=dict(l=20, r=20, t=60, b=30)
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

else:

    st.info("No monthly data available.")


st.divider()


# =========================================================
# 18. DETAILED LOAN RECORDS
# =========================================================

st.subheader("Detailed Loan Records")

st.caption(
    f"Total filtered records: {len(filtered_df):,}"
)

if not filtered_df.empty:

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "No records match your selected filters. "
        "Try changing or resetting your filters."
    )


# =========================================================
# 19. DOWNLOAD FILTERED DATA
# =========================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv_data,
    file_name="filtered_loan_records.csv",
    mime="text/csv",
    use_container_width=True
)


# =========================================================
# 20. FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
    <div style="
        text-align:center;
        color:#8996A8;
        font-size:12px;
        padding:10px;
    ">
        Loan Portfolio Analytics Dashboard
        <br>
        Built with Python, Pandas, Plotly and Streamlit
    </div>
""", unsafe_allow_html=True)
