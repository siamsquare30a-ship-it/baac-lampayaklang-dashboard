# pages/team_overview.py — Level 1: ภาพรวมทีม (ผลงานรวมทีม)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.real_loader import load_team_kpi, load_dashboard_summary, REAL_FILE
from components.charts import gauge_chart

# IBM Carbon status colors
COLOR_MAP = {"บรรลุเป้า": "#24a148", "ใกล้เป้า": "#b28600", "ต่ำกว่าเป้า": "#da1e28"}
EMOJI_MAP = {"บรรลุเป้า": "✅", "ใกล้เป้า": "⚠️", "ต่ำกว่าเป้า": "🔴"}
BG_MAP    = {"บรรลุเป้า": "#defbe6", "ใกล้เป้า": "#fcf4d6", "ต่ำกว่าเป้า": "#fff1f1"}


def _staff_card(name: str, position: str, score: float, max_score: float = 70.0) -> None:
    rate   = round(score / max_score * 100, 1)
    status = "บรรลุเป้า" if rate >= 100 else "ใกล้เป้า" if rate >= 80 else "ต่ำกว่าเป้า"
    color  = COLOR_MAP[status]
    bg     = BG_MAP[status]
    tag_label = {"บรรลุเป้า": "บรรลุเป้า", "ใกล้เป้า": "ใกล้เป้า", "ต่ำกว่าเป้า": "ต่ำกว่าเป้า"}[status]
    st.markdown(f"""
    <div style="background:#f4f4f4;border-left:4px solid {color};
                border-radius:0px;padding:16px;margin-bottom:8px;
                border-bottom:1px solid #e0e0e0;">
      <div style="font-size:11px;color:#525252;letter-spacing:0.32px;
                  text-transform:uppercase;margin-bottom:6px;">{position}</div>
      <div style="font-size:18px;font-weight:600;color:#161616;margin-bottom:10px;">{name}</div>
      <div style="font-size:34px;font-weight:300;color:{color};line-height:1.1;">{score:.2f}</div>
      <div style="font-size:12px;color:#525252;letter-spacing:0.32px;margin-bottom:10px;">/ {max_score:.0f} คะแนน</div>
      <span style="background:{bg};color:{color};padding:3px 10px;
                   border-radius:24px;font-size:11px;font-weight:600;
                   letter-spacing:0.16px;">{EMOJI_MAP[status]} {tag_label}</span>
    </div>
    """, unsafe_allow_html=True)


def _data_date_badge(filepath: str) -> None:
    """แสดง 'ข้อมูล ณ วันที่' จากวันแก้ไขไฟล์ Excel"""
    try:
        mtime = os.path.getmtime(filepath)
        dt    = datetime.fromtimestamp(mtime)
        # แปลงเป็น พ.ศ.
        thai_months = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
                       "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
        date_str = f"{dt.day} {thai_months[dt.month]} {dt.year + 543}"
        st.markdown(
            f'<div style="text-align:right;font-size:12px;color:#888;margin-top:-10px;">'
            f'ข้อมูล ณ วันที่ {date_str}</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        pass


def render(filepath: str = REAL_FILE) -> None:
    st.header("🏦 ภาพรวมทีม — ผลการดำเนินงาน ปีบัญชี 2568")
    _data_date_badge(filepath)

    summary_df = load_dashboard_summary(filepath)
    team_df    = load_team_kpi(filepath)

    # =========================================================
    # ROW 1: Staff Score Cards
    # =========================================================
    st.subheader("🎯 คะแนน Performance รายคน")
    if summary_df is not None and not summary_df.empty:
        cols = st.columns(len(summary_df))
        for col, (_, r) in zip(cols, summary_df.iterrows()):
            with col:
                _staff_card(r["name"], r["position"], r["score_performance"])
    st.divider()

    if team_df is None or team_df.empty:
        st.warning("ไม่พบข้อมูล ผลงานรวมทีม")
        return

    kpi_df = team_df[team_df.get("is_total", False) == False].copy()

    # =========================================================
    # ROW 2: Gauge ภาพรวม + คะแนนสรุป
    # =========================================================
    total_row = team_df[team_df.get("is_total", False) == True]
    col_gauge, col_meta = st.columns([1, 2])
    with col_gauge:
        if not total_row.empty:
            sc = total_row.iloc[0]["score"]
            mx = total_row.iloc[0]["max_score"]
            overall_pct = round(sc / mx * 100, 1) if mx else 0
            st.plotly_chart(
                gauge_chart(overall_pct, f"ภาพรวมทีม\n{sc:.2f}/{mx:.0f} คะแนน"),
                use_container_width=True,
            )

    with col_meta:
        st.markdown("**สรุปผลรายหัวข้อ**")
        if not kpi_df.empty and "status" in kpi_df.columns:
            cnt = kpi_df["status"].value_counts()
            c1, c2, c3 = st.columns(3)
            c1.metric("✅ บรรลุเป้า",   cnt.get("บรรลุเป้า",   0))
            c2.metric("⚠️ ใกล้เป้า",    cnt.get("ใกล้เป้า",    0))
            c3.metric("🔴 ต่ำกว่าเป้า", cnt.get("ต่ำกว่าเป้า", 0))

    st.divider()

    # =========================================================
    # ROW 3: KPI Score Bar Chart
    # =========================================================
    if not kpi_df.empty and "score" in kpi_df.columns:
        kpi_chart = kpi_df[kpi_df["score"] > 0].copy()
        kpi_chart["pct"] = kpi_chart.apply(
            lambda r: round(r["score"] / r["max_score"] * 100, 1)
            if r["max_score"] > 0 else 0, axis=1
        )
        colors = kpi_chart["status"].map(
            lambda s: COLOR_MAP.get(s, "#aaa")
        ).tolist()

        short_names = [n[:35] + "…" if len(n) > 35 else n for n in kpi_chart["kpi_name"]]
        fig = go.Figure(go.Bar(
            y=short_names,
            x=kpi_chart["pct"],
            orientation="h",
            marker_color=colors,
            text=[f"{r['score']:.2f}/{r['max_score']:.1f} ({r['pct']:.0f}%)"
                  for _, r in kpi_chart.iterrows()],
            textposition="outside",
        ))
        fig.add_vline(x=100, line_dash="dash", line_color="black",
                      annotation_text="เกณฑ์ 100%")
        fig.update_layout(
            title=dict(text="คะแนนที่ได้ต่อคะแนนเต็ม รายหัวข้อ KPI (%)",
                       font=dict(size=16, weight=300, color="#161616")),
            xaxis=dict(title="% คะแนนที่ได้", range=[0, 100],
                       gridcolor="#e0e0e0", linecolor="#c6c6c6", tickfont=dict(color="#525252")),
            yaxis=dict(tickfont=dict(color="#161616", size=13)),
            height=max(400, len(kpi_chart) * 40),
            margin=dict(l=10, r=100, t=50, b=30),
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font=dict(family="IBM Plex Sans, Sarabun, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # =========================================================
    # ROW 4: ตาราง KPI ละเอียด
    # =========================================================
    st.subheader("📋 รายละเอียด KPI ทั้งหมด")

    # filter
    col_f1, col_f2 = st.columns([2, 1])
    with col_f2:
        status_filter = st.selectbox(
            "กรองสถานะ",
            ["ทั้งหมด", "บรรลุเป้า", "ใกล้เป้า", "ต่ำกว่าเป้า"],
            key="team_status_filter",
        )
    disp = kpi_df.copy()
    if status_filter != "ทั้งหมด":
        disp = disp[disp["status"] == status_filter]

    if not disp.empty:
        disp["สถานะ"] = disp["status"].map(
            lambda s: EMOJI_MAP.get(s, "")
        )
        show_cols = {
            "kpi_name":   "หัวข้อ KPI",
            "target":     "เป้าหมาย",
            "actual":     "ผลจริง",
            "unit":       "หน่วย",
            "score":      "คะแนนที่ได้",
            "max_score":  "คะแนนเต็ม",
            "สถานะ":      "สถานะ",
        }
        show_df = disp[[c for c in show_cols if c in disp.columns or c == "สถานะ"]].rename(columns=show_cols)

        def style_row(row):
            s = disp.loc[disp["kpi_name"] == row.get("หัวข้อ KPI", ""), "status"]
            sv = s.values[0] if len(s) else ""
            bg = BG_MAP.get(sv, "")
            return [f"background-color:{bg}"] * len(row)

        st.dataframe(show_df, use_container_width=True, hide_index=True)
