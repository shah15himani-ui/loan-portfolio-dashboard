
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
# 2. GLOBAL CSS
# =========================================================

st.html("""
<style>

.stApp {
    background-color: #F4F6FA;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E5EAF1;
}

.stButton > button {
    border-radius: 9px;
    border: none;
    background-color: #2563EB;
    color: white;
    font-weight: 600;
    padding: 10px 18px;
}

.stButton > button:hover {
    background-color: #1D4ED8;
    color: white;
    border: none;
}

[data-testid="stDataFrame"] {
    border: 1px solid #E5EAF1;
    border-radius: 12px;
}

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5EAF1;
    border-radius: 15px;
    padding: 22px;
    min-height: 135px;
    box-shadow: 0 4px 15px rgba(30,50,80,0.04);
}

.kpi-label {
    color: #718096;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
}

.kpi-value {
    color: #172B4D;
    font-size: 27px;
    font-weight: 700;
}

.kpi-note {
    color: #94A3B8;
    font-size: 12px;
    margin-top: 8px;
}

.section-heading {
    color: #172B4D;
    font-size: 21px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 12px;
}

</style>
""")


# =========================================================
# 3. DATA CLEANING FUNCTION
# =========================================================

def clean_loan_data(data):

    data = data.copy()

    # Remove empty rows and columns
    data = data.dropna(axis=1, how="all")
    data = data.dropna(axis=0, how="all")

    # Clean column names
    data.columns = data.columns.astype(str).str.strip()

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
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # Clean text columns
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
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    # Convert loan amount to numeric
    data["Loan Amount"] = (
        data["Loan Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("Rs.", "", regex=False)
        .str.strip()
    )

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

    # Remove invalid loan amounts and dates
    data = data.dropna(
        subset=["Loan Amount", "Date"]
    )

    if data.empty:
        raise ValueError(
            "No valid loan records found in the Excel file."
        )

    return data


# =========================================================
# 4. HELPER FUNCTIONS
# =========================================================

def format_crore(amount):

    return f"₹{amount / 10000000:.2f} Cr"


def create_kpi_card(label, value, note):

    # HTML is rendered directly, not through Markdown
    st.html(f"""
    <div class="kpi-card">

        <div class="kpi-label">
            {label}
        </div>

        <div class="kpi-value">
            {value}
        </div>

        <div class="kpi-note">
            {note}
        </div>

    </div>
    """)


def create_section_heading(title):

    st.html(f"""
    <div class="section-heading">
        {title}
    </div>
    """)


def chart_layout(fig):

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            color="#475569"
        ),
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=30
        ),
        legend_title_text=""
    )

    return fig


# =========================================================
# 5. LANDING PAGE
# =========================================================

if "loan_df" not in st.session_state:

    # Hide sidebar on landing page
    st.html("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            padding-top: 2rem;
        }
    </style>
    """)

    # Landing page heading
    st.html("""
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
    """)

    # Center upload section
    left, center, right = st.columns([1, 1.7, 1])

    with center:

        st.html("""
        <div style="
            background: #FFFFFF;
            border: 1px solid #E5EAF1;
            border-radius: 20px;
            padding: 35px;
            text-align: center;
            box-shadow: 0 8px 30px rgba(30,50,80,0.06);
        ">

            <div style="
                font-size: 48px;
                margin-bottom: 15px;
            ">
                📊
            </div>

            <h2 style="
                color: #172B4D;
                font-size: 24px;
            ">
                Upload Your Loan Records
            </h2>

            <p style="
                color: #718096;
                font-size: 14px;
            ">
                Select your Excel dataset to access
                your interactive analytics dashboard.
            </p>

        </div>
        """)

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

    # Landing page footer
    st.html("""
    <div style="
        text-align: center;
        color: #94A3B8;
        font-size: 12px;
        margin-top: 35px;
    ">
        Supported format: Excel (.xlsx)
        <br><br>
        Loan Portfolio Analytics Dashboard
    </div>
    """)

    st.stop()


# =========================================================
# 6. DASHBOARD DATA
# =========================================================

df = st.session_state["loan_df"].copy()

df["Year"] = df["Date"].dt.year

df["Month Year"] = (
    df["Date"]
    .dt.to_period("M")
    .astype(str)
)

df["Month Sort"] = (
    df["Date"]
    .dt.to_period("M")
)


# =========================================================
# 7. SIDEBAR
# =========================================================

st.sidebar.title("📊 Loan Analytics")

st.sidebar.caption(
    st.session_state.get("loan_filename", "Uploaded file")
)

st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")


# Reset filters
def reset_filters():

    for key in [
        "bank_filter",
        "loan_filter",
        "status_filter",
        "executive_filter",
        "customer_search",
        "date_filter"
    ]:

        st.session_state.pop(key, None)


if st.sidebar.button(
    "↻ Reset Filters",
    use_container_width=True,
    on_click=reset_filters
):
    pass


st.sidebar.divider()


# Upload another file
if st.sidebar.button(
    "⬆ Upload Another File",
    use_container_width=True
):

    st.session_state.pop("loan_df", None)
    st.session_state.pop("loan_filename", None)
    st.session_state.pop("landing_upload", None)

    st.rerun()


# =========================================================
# 8. FILTER OPTIONS
# =========================================================

bank_options = (
    ["All Banks"]
    + sorted(df["Bank Name"].unique().tolist())
)

loan_options = (
    ["All Loan Types"]
    + sorted(df["Type of Loan"].unique().tolist())
)

status_options = (
    ["All Statuses"]
    + sorted(df["Status"].unique().tolist())
)

executive_options = (
    ["All Executives"]
    + sorted(df["Executive Name"].unique().tolist())
)


selected_bank = st.sidebar.selectbox(
    "Bank Name",
    bank_options,
    key="bank_filter"
)

selected_loan = st.sidebar.selectbox(
    "Type of Loan",
    loan_options,
    key="loan_filter"
)

selected_status = st.sidebar.selectbox(
    "Application Status",
    status_options,
    key="status_filter"
)

selected_executive = st.sidebar.selectbox(
    "Executive Name",
    executive_options,
    key="executive_filter"
)


min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_filter"
)


customer_search = st.sidebar.text_input(
    "Search Customer",
    placeholder="Enter customer name...",
    key="customer_search"
)


# =========================================================
# 9. APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if selected_bank != "All Banks":

    filtered_df = filtered_df[
        filtered_df["Bank Name"] == selected_bank
    ]


if selected_loan != "All Loan Types":

    filtered_df = filtered_df[
        filtered_df["Type of Loan"] == selected_loan
    ]


if selected_status != "All Statuses":

    filtered_df = filtered_df[
        filtered_df["Status"] == selected_status
    ]


if selected_executive != "All Executives":

    filtered_df = filtered_df[
        filtered_df["Executive Name"] == selected_executive
    ]


if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        &
        (filtered_df["Date"].dt.date <= end_date)
    ]


if customer_search:

    filtered_df = filtered_df[
        filtered_df["Customer Name"].str.contains(
            customer_search,
            case=False,
            na=False
        )
    ]


# =========================================================
# 10. DASHBOARD HEADER
# =========================================================

st.html("""
<div style="margin-bottom: 25px;">

    <div style="
        color: #2563EB;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    ">
        OVERVIEW
    </div>

    <h1 style="
        color: #172B4D;
        font-size: 32px;
        margin: 0;
    ">
        Loan Portfolio Dashboard
    </h1>

    <p style="
        color: #718096;
        font-size: 14px;
        margin-top: 8px;
    ">
        Monitor applications, loan amounts and portfolio performance.
    </p>

</div>
""")


# =========================================================
# 11. CHECK FILTERED DATA
# =========================================================

if filtered_df.empty:

    st.warning(
        "No records match the selected filters. "
        "Please change your filters."
    )

    st.stop()


# =========================================================
# 12. KPI CALCULATIONS
# =========================================================

total_applications = len(filtered_df)

total_loan_amount = filtered_df["Loan Amount"].sum()

disbursed_df = filtered_df[
    filtered_df["Status"].str.lower() == "disbursed"
]

disbursed_amount = disbursed_df["Loan Amount"].sum()

pending_applications = (
    filtered_df["Status"].str.lower() == "pending"
).sum()


# =========================================================
# 13. KPI CARDS
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:

    create_kpi_card(
        "TOTAL APPLICATIONS",
        f"{total_applications:,}",
        "Applications in selected data"
    )


with kpi2:

    create_kpi_card(
        "TOTAL LOAN AMOUNT",
        format_crore(total_loan_amount),
        "Total loan application value"
    )


with kpi3:

    create_kpi_card(
        "DISBURSED AMOUNT",
        format_crore(disbursed_amount),
        "Amount from disbursed applications"
    )


with kpi4:

    create_kpi_card(
        "PENDING APPLICATIONS",
        f"{pending_applications:,}",
        "Applications with pending status"
    )


st.write("")


# =========================================================
# 14. STATUS DISTRIBUTION
# =========================================================

create_section_heading("Application Status Overview")

col1, col2 = st.columns(2)


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

    fig_status = px.pie(
        status_data,
        names="Status",
        values="Applications",
        hole=0.55,
        title="Application Status Distribution"
    )

    fig_status.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_status = chart_layout(fig_status)

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )


# =========================================================
# 15. LOAN TYPE ANALYSIS
# =========================================================

with col2:

    loan_data = (
        filtered_df
        .groupby("Type of Loan")["Loan Amount"]
        .sum()
        .reset_index()
        .sort_values("Loan Amount", ascending=False)
    )

    fig_loan = px.bar(
        loan_data,
        x="Type of Loan",
        y="Loan Amount",
        title="Loan Amount by Loan Type",
        color="Loan Amount",
        color_continuous_scale="Blues"
    )

    fig_loan.update_layout(
        xaxis_title="Loan Type",
        yaxis_title="Loan Amount (₹)"
    )

    fig_loan = chart_layout(fig_loan)

    st.plotly_chart(
        fig_loan,
        use_container_width=True
    )


# =========================================================
# 16. BANK PERFORMANCE
# =========================================================

create_section_heading("Bank Performance")

bank_data = (
    filtered_df
    .groupby("Bank Name")
    .agg(
        Applications=("Customer Name", "count"),
        Loan_Amount=("Loan Amount", "sum")
    )
    .reset_index()
    .sort_values("Loan_Amount", ascending=True)
)


fig_bank = px.bar(
    bank_data,
    x="Loan_Amount",
    y="Bank Name",
    orientation="h",
    title="Loan Amount by Bank",
    color="Loan_Amount",
    color_continuous_scale="Blues",
    hover_data=["Applications"]
)

fig_bank.update_layout(
    xaxis_title="Loan Amount (₹)",
    yaxis_title="Bank"
)

fig_bank = chart_layout(fig_bank)

st.plotly_chart(
    fig_bank,
    use_container_width=True
)


# =========================================================
# 17. EXECUTIVE PERFORMANCE
# =========================================================

create_section_heading("Executive Performance")

executive_data = (
    filtered_df
    .groupby("Executive Name")
    .agg(
        Applications=("Customer Name", "count"),
        Loan_Amount=("Loan Amount", "sum")
    )
    .reset_index()
    .sort_values("Loan_Amount", ascending=False)
)


fig_executive = px.bar(
    executive_data,
    x="Executive Name",
    y="Loan_Amount",
    title="Loan Amount Handled by Executive",
    color="Loan_Amount",
    color_continuous_scale="Teal"
)

fig_executive.update_layout(
    xaxis_title="Executive",
    yaxis_title="Loan Amount (₹)"
)

fig_executive = chart_layout(fig_executive)

st.plotly_chart(
    fig_executive,
    use_container_width=True
)


# =========================================================
# 18. MONTHLY LOAN TREND
# =========================================================

create_section_heading("Monthly Loan Trend")

monthly_data = (
    filtered_df
    .groupby("Month Sort")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Month Sort")
)

monthly_data["Month Year"] = (
    monthly_data["Month Sort"].astype(str)
)


fig_monthly = px.line(
    monthly_data,
    x="Month Year",
    y="Loan Amount",
    title="Monthly Loan Application Amount",
    markers=True
)

fig_monthly.update_traces(
    line=dict(width=3),
    marker=dict(size=8)
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Loan Amount (₹)"
)

fig_monthly = chart_layout(fig_monthly)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)


# =========================================================
# 19. TOP 10 CUSTOMERS
# =========================================================

create_section_heading("Top 10 Customers")

top_customers = (
    filtered_df
    .groupby("Customer Name")["Loan Amount"]
    .sum()
    .reset_index()
    .sort_values("Loan Amount", ascending=False)
    .head(10)
)

top_customers = top_customers.sort_values(
    "Loan Amount",
    ascending=True
)


fig_customers = px.bar(
    top_customers,
    x="Loan Amount",
    y="Customer Name",
    orientation="h",
    title="Top 10 Customers by Loan Amount",
    color="Loan Amount",
    color_continuous_scale="Blues"
)

fig_customers = chart_layout(fig_customers)

st.plotly_chart(
    fig_customers,
    use_container_width=True
)


# =========================================================
# 20. DETAILED LOAN RECORDS
# =========================================================

create_section_heading("Detailed Loan Records")

display_columns = [
    col for col in [
        "Sr. No.",
        "Customer Name",
        "Type of Loan",
        "Status",
        "Loan Amount",
        "Bank Name",
        "Executive Name",
        "Date"
    ]
    if col in filtered_df.columns
]

display_df = filtered_df[display_columns].copy()

display_df["Date"] = (
    display_df["Date"].dt.strftime("%d-%b-%Y")
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 21. DOWNLOAD FILTERED DATA
# =========================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Data",
    data=csv_data,
    file_name="loan_portfolio_filtered_data.csv",
    mime="text/csv"
)


# =========================================================
# 22. FOOTER
# =========================================================

st.html("""
<div style="
    text-align: center;
    color: #94A3B8;
    font-size: 12px;
    padding: 30px 0 10px;
    border-top: 1px solid #E5EAF1;
    margin-top: 35px;
">
    Loan Portfolio Analytics Dashboard
    <br>
    Data-driven insights for smarter loan management
</div>
""")
