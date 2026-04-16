# pages/zone_compare.py — Level 2: เปรียบเทียบรายเขต (พิราวรรณ vs พรพงศ์)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.real_loader import load_zone_kpi, REAL_FILE

COLOR_MAP = {"บรรลุเป้า": "#059669", "ใกล้เป้า": "#d97706", "ต่ำกว่าเป้า": "#dc2626"}
EMOJI_MAP = {"บรรลุเป้า": "✅", "ใกล้เป้า": "⚠️", "ต่ำกว่าเป้า": "🔴"}
BG_MAP    = {"บรรลุเป้า": "#ecfdf5", "ใกล้เป้า": "#fffbeb", "ต่ำกว่าเป้า": "#fef2f2"}

ZONE_COLORS = {
    "เขต พิราวรรณ": "#00693e",
    "เขต พรพงศ์":   "#059669",
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
            <div style="background:#ffffff;border-left:4px solid {color};
                        border-radius:8px;padding:16px;margin-bottom:8px;
                        box-shadow:0 1px 3px rgba(0,0,0,0.08);">
              <div style="font-size:11px;color:#6b7280;letter-spacing:0.32px;
                          text-transform:uppercase;margin-bottom:6px;">{zone}</div>
              <div style="font-size:36px;font-weight:300;color:{color};line-height:1.1;">{total_sc:.2f}</div>
              <div style="font-size:12px;color:#6b7280;letter-spacing:0.32px;margin-bottom:10px;">/ {total_max:.1f} คะแนน</div>
              <div style="font-size:13px;font-weight:600;color:{color};margin-bottom:10px;">ได้ {pct:.1f}% ของเต็ม</div>
              <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <span style="background:#ecfdf5;color:#059669;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">✅ {achieved}</span>
                <span style="background:#fffbeb;color:#d97706;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">⚠️ {near}</span>
                <span style="background:#fef2f2;color:#dc2626;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">🔴 {below}</span>
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
        title=dict(text="ผลจริง vs เป้าหมาย (แยกเขต)",
                   font=dict(size=16, weight=300, color="#161616")),
        height=max(500, len(pivot) * 55),
        margin=dict(l=10, r=30, t=50, b=30),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(family="IBM Plex Sans, Sarabun, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    font=dict(size=13, color="#161616")),
        xaxis=dict(gridcolor="#e0e0e0", linecolor="#c6c6c6", tickfont=dict(color="#525252")),
        yaxis=dict(tickfont=dict(color="#161616", size=13)),
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
