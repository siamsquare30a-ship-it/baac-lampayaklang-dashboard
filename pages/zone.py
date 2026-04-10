# pages/zone.py — Level 2: เขตสินเชื่อ

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import ZONES, COLOR_MAP, STATUS_EMOJI
from data.processor import zone_summary, zone_overall, add_kpi_columns
from components.charts import radar_chart, zone_ranking_bar
from exports.export_utils import download_excel_button


def _color_rate(val: float) -> str:
    if val >= 100:
        return "background-color:#d4edda"
    elif val >= 80:
        return "background-color:#fff3cd"
    else:
        return "background-color:#f8d7da"


def render(df: pd.DataFrame) -> None:
    st.header("📍 ผลการดำเนินงานระดับเขตสินเชื่อ")

    proc     = add_kpi_columns(df)
    zone_df  = zone_summary(proc)
    overall  = zone_overall(proc)

    # =========================================================
    # Ranking bar
    # =========================================================
    col_rank, col_sel = st.columns([2, 1])
    with col_rank:
        st.plotly_chart(zone_ranking_bar(overall), use_container_width=True)

    with col_sel:
        st.markdown("**TOP / BOTTOM**")
        st.dataframe(
            overall[["rank", "zone_id", "overall_rate"]].rename(columns={
                "rank":         "อันดับ",
                "zone_id":      "เขต",
                "overall_rate": "อัตรา (%)",
            }),
            hide_index=True,
            use_container_width=True,
        )

    st.divider()

    # =========================================================
    # เลือกเขต → Radar + ตาราง
    # =========================================================
    available_zones = zone_df["zone_id"].unique().tolist()
    selected_zone   = st.selectbox("เลือกเขตสินเชื่อเพื่อดูรายละเอียด",
                                   available_zones, key="zone_select")

    col_radar, col_table = st.columns([1, 2])

    with col_radar:
        st.plotly_chart(
            radar_chart(zone_df, selected_zone),
            use_container_width=True,
        )

    with col_table:
        sub = zone_df[zone_df["zone_id"] == selected_zone].copy()
        sub["สถานะ"] = sub["status"].map(
            lambda s: f"{STATUS_EMOJI.get(s,'')} {s}"
        )
        display = sub[["category", "target", "actual",
                        "achievement_rate", "สถานะ"]].rename(columns={
            "category":        "หมวด",
            "target":          "เป้า (ล้านบาท)",
            "actual":          "จริง (ล้านบาท)",
            "achievement_rate":"อัตรา (%)",
        })

        def style_row(row):
            rate = sub.loc[sub["category"] == row["หมวด"], "achievement_rate"]
            v = rate.values[0] if len(rate) else 50
            return [_color_rate(v)] * len(row)

        st.dataframe(
            display.style.apply(style_row, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        download_excel_button(
            sub, label="📥 ดาวน์โหลดข้อมูลเขตนี้",
            filename=f"zone_{selected_zone}",
            sheet_name=selected_zone,
        )

    # ปุ่ม drill-down ไป Level 3
    st.divider()
    if st.button(f"👤 ดูรายลูกค้าใน {selected_zone}", use_container_width=True,
                 type="primary"):
        st.session_state["selected_zone"]    = selected_zone
        st.session_state["current_page"]     = "customer"
        st.rerun()
