# pages/overview.py — Level 1: ภาพรวมสาขา

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import BRANCH_NAME, PERIOD, CATEGORIES
from data.processor import branch_summary, branch_trend, add_kpi_columns, customer_alerts
from components.kpi_card import kpi_card
from components.charts import gauge_chart, category_bar, trend_line
from components.alerts import show_alert_table
from exports.export_utils import download_summary_excel, download_excel_button


def render(df: pd.DataFrame) -> None:
    st.header(f"🏦 {BRANCH_NAME} — ภาพรวมปีงบประมาณ {PERIOD}")

    summary = branch_summary(add_kpi_columns(df))
    trend   = branch_trend(df)

    # =========================================================
    # ROW 1: Gauge + KPI Cards
    # =========================================================
    col_gauge, col_cards = st.columns([1, 2])

    with col_gauge:
        overall_rate = (
            summary["actual"].sum() / summary["target"].sum() * 100
            if summary["target"].sum() > 0 else 0
        )
        st.plotly_chart(
            gauge_chart(overall_rate, "ภาพรวมบรรลุเป้า"),
            use_container_width=True,
        )

    with col_cards:
        st.markdown("**ผลการดำเนินงานตามหมวด**")
        n_cols = 3
        rows = [summary.iloc[i:i+n_cols] for i in range(0, len(summary), n_cols)]
        for row_df in rows:
            cols = st.columns(len(row_df))
            for col, (_, r) in zip(cols, row_df.iterrows()):
                with col:
                    kpi_card(
                        label=r["category"],
                        target=r["target"],
                        actual=r["actual"],
                        rate=r["achievement_rate"],
                        status=r["status"],
                    )

    st.divider()

    # =========================================================
    # ROW 2: Bar chart + Trend
    # =========================================================
    col_bar, col_trend = st.columns(2)

    with col_bar:
        st.plotly_chart(category_bar(summary), use_container_width=True)

    with col_trend:
        cat_options = ["ทั้งหมด"] + CATEGORIES
        selected_cat = st.selectbox("เลือกหมวดแนวโน้ม", cat_options, key="trend_cat")
        if not trend.empty:
            st.plotly_chart(
                trend_line(trend, selected_cat),
                use_container_width=True,
            )
        else:
            st.info("ไม่มีข้อมูลรายเดือน")

    st.divider()

    # =========================================================
    # ROW 3: Alert + Export
    # =========================================================
    st.subheader("🔴 รายการต้องติดตาม (< 80%)")
    alert_df = customer_alerts(df)
    show_alert_table(alert_df)

    st.subheader("📥 ส่งออกรายงาน")
    from data.processor import zone_summary
    zone_df_all = zone_summary(add_kpi_columns(df))
    download_summary_excel(summary, zone_df_all, alert_df)
