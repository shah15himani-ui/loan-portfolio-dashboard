        with metric_cols[0]:

            show_kpi(
                "Disbursement Rate",
                f"{disbursement_rate:.1f}%",
                "Disbursed / total applications"
            )

        with metric_cols[1]:

            show_kpi(
                "Approval Rate",
                f"{approval_rate:.1f}%",
                "Approved / total applications"
            )

        with metric_cols[2]:

            show_kpi(
                "Rejection Rate",
                f"{rejection_rate:.1f}%",
                "Rejected / total applications"
            )

        st.write("")

        show_panel_title("Application Status Breakdown")

        status_breakdown = (
            status_counts
            .rename_axis("Status")
            .reset_index(name="Applications")
        )

        fig = px.bar(
            status_breakdown,
            x="Status",
            y="Applications",
            color="Status",
            color_discrete_map=STATUS_COLORS,
            text="Applications"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            chart_layout(fig, 370),
            use_container_width=True
        )

    if amount_col and type_col:

        show_panel_title("Loan Amount by Category")

        category_metrics = (
            filtered_df.groupby(type_col)[amount_col]
            .agg(["count", "sum", "mean"])
            .reset_index()
        )

        category_metrics.columns = [
            "Loan Type",
            "Applications",
            "Total Loan Amount",
            "Average Loan Amount"
        ]

        category_metrics["Total Loan Amount"] = (
            category_metrics["Total Loan Amount"].apply(money_inr)
        )

        category_metrics["Average Loan Amount"] = (
            category_metrics["Average Loan Amount"].apply(money_inr)
        )

        st.dataframe(
            category_metrics,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# 19. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        JR Financial · Loan Portfolio Analytics
    </div>
    """,
    unsafe_allow_html=True
)
