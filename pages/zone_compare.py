# pages/zone_compare.py — Level 2: เปรียบเทียบรายเขต (พิราวรรณ vs พรพงศ์)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.real_loader import load_zone_kpi, REAL_FILE

COLOR_MAP = {"บรรลุเป้า": "#28a745", "ใกล้เป้า": "#ffc107", "ต่ำกว่าเป้า": "#dc3545"}
EMOJI_MAP = {"บรรลุเป้า": "✅", "ใกล้เป้า": "⚠️", "ต่ำกว่าเป้า": "🔴"}
BG_MAP    = {"บรรลุเป้า": "#d4edda", "ใกล้เป้า": "#fff3cd", "ต่ำกว่าเป้า": "#f8d7da"}

ZONE_COLORS = {
    "เขต พิราวรรณ": "#007bff",
    "เขต พรพงศ์":  "#fd7e14",
}


def _data_date_badge(filepath: str) -> None:
    try:
        dt = datetime.fromtimestamp(os.path.getmtime(filepath))
        thai_months = ["","ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.",
                       "ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]
        date_str = f"{dt.day} {thai_months[dt.month]} {dt.year + 543}"
        st.markdown(f'<div style="text-align:right;font-size:12px;color:#888;margin-top:-10px;">ข้อมูล ณ วันที่ {date_str}</div>', unsafe_allow_html=True)
    except Exception:
        pass


def render(filepath: str = REAL_FILE) -> None:
    st.header("📍 เปรียบเทียบผลงานรายเขต — พิราวรรณ vs พรพงศ์")
    _data_date_badge(filepath)

    zone_df = load_zone_kpi(filepath)
    if zone_df is None or zone_df.empty:
        st.warning("ไม่พบข้อมูล ผลงานรายเขต")
        return

    zones = zone_df["zone"].unique().tolist()

    # =========================================================
    # Summary scorecard per zone
    # =========================================================
    st.subheader("🎯 ภาพรวมแต่ละเขต")
    cols = st.columns(len(zones))
    for col, zone in zip(cols, zones):
        z_df = zone_df[zone_df["zone"] == zone]
        total_sc  = z_df["score"].sum()
        total_max = z_df["max_score"].sum()
        pct = round(total_sc / total_max * 100, 1) if total_max > 0 else 0
        achieved  = (z_df["status"] == "บรรลุเป้า").sum()
        near      = (z_df["status"] == "ใกล้เป้า").sum()
        below     = (z_df["status"] == "ต่ำกว่าเป้า").sum()
        color = ZONE_COLORS.get(zone, "#6c757d")
        with col:
            st.markdown(f"""
            <div style="border-left:6px solid {color};background:#f8f9fa;
                        border-radius:8px;padding:14px;margin-bottom:8px;">
              <div style="font-size:16px;font-weight:700;color:#333;">{zone}</div>
              <div style="font-size:24px;font-weight:800;color:{color};">
                {total_sc:.2f} <span style="font-size:13px;color:#888;">/ {total_max:.1f} คะแนน</span>
              </div>
              <div style="font-size:13px;color:{color};">ได้ {pct:.1f}% ของเต็ม</div>
              <div style="font-size:12px;margin-top:6px;">
                ✅ {achieved} &nbsp;&nbsp; ⚠️ {near} &nbsp;&nbsp; 🔴 {below}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # =========================================================
    # Grouped bar: actual vs target per KPI
    # =========================================================
    st.subheader("📊 เปรียบเทียบผลจริง vs เป้าหมาย รายหัวข้อ")

    pivot = zone_df.pivot_table(
        index="kpi_name", columns="zone",
        values="actual", aggfunc="first"
    ).reset_index()

    target_map = zone_df.drop_duplicates("kpi_name").set_index("kpi_name")["target"]
    pivot["target"] = pivot["kpi_name"].map(target_map)

    short_names = [n[:40] + "…" if len(n) > 40 else n for n in pivot["kpi_name"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="เป้าหมาย",
        y=short_names,
        x=pivot["target"],
        orientation="h",
        marker_color="rgba(0,0,0,0.15)",
        marker_pattern_shape="/",
    ))
    for zone in zones:
        if zone in pivot.columns:
            fig.add_trace(go.Bar(
                name=zone,
                y=short_names,
                x=pivot[zone],
                orientation="h",
                marker_color=ZONE_COLORS.get(zone, "#888"),
            ))

    fig.update_layout(
        barmode="group",
        title="ผลจริง vs เป้าหมาย (แยกเขต)",
        height=max(500, len(pivot) * 50),
        margin=dict(l=10, r=30, t=50, b=30),
        font=dict(family="Sarabun, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # =========================================================
    # Score achievement % per KPI per zone (heatmap-style table)
    # =========================================================
    st.subheader("🗂️ ตารางเปรียบเทียบรายหัวข้อ")

    pivot_rate = zone_df.pivot_table(
        index="kpi_name", columns="zone",
        values="achievement_rate", aggfunc="first"
    ).reset_index()
    pivot_status = zone_df.pivot_table(
        index="kpi_name", columns="zone",
        values="status", aggfunc="first"
    ).reset_index()

    # รวมเป็น display table
    display_rows = []
    for _, row in pivot_rate.iterrows():
        kpi = row["kpi_name"]
        entry = {"หัวข้อ KPI": kpi}
        for zone in zones:
            rate = row.get(zone)
            stat = pivot_status.set_index("kpi_name").loc[kpi, zone] if kpi in pivot_status["kpi_name"].values else "-"
            entry[zone] = f"{EMOJI_MAP.get(stat,'')} {rate:.1f}%" if rate is not None else "-"
            # ไม่แสดงชื่อสถานะ แสดงแค่ emoji + %
        display_rows.append(entry)

    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)

    st.divider()

    # =========================================================
    # Drill-down: เลือก zone → ไปหน้ารายบุคคล
    # =========================================================
    st.subheader("👤 ดูผลงานรายบุคคล")
    zone_to_staff = {
        "เขต พิราวรรณ": "พิราวรรณ",
        "เขต พรพงศ์":  "พรพงศ์",
    }
    c1, c2 = st.columns(2)
    with c1:
        if st.button("👤 ดูผลงาน พิราวรรณ", use_container_width=True, type="primary"):
            st.session_state["selected_staff"]  = "พิราวรรณ"
            st.session_state["current_page"]    = "individual"
            st.rerun()
    with c2:
        if st.button("👤 ดูผลงาน พรพงศ์", use_container_width=True, type="primary"):
            st.session_state["selected_staff"]  = "พรพงศ์"
            st.session_state["current_page"]    = "individual"
            st.rerun()
