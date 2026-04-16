# pages/individual.py — Level 3: ผลงานรายบุคคล (Scorecard)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.real_loader import load_staff_kpi, load_dashboard_summary, STAFF_SHEETS, STAFF_META, REAL_FILE
from components.charts import gauge_chart

# IBM Carbon status colors
COLOR_MAP = {"บรรลุเป้า": "#24a148", "ใกล้เป้า": "#b28600", "ต่ำกว่าเป้า": "#da1e28"}
EMOJI_MAP = {"บรรลุเป้า": "✅", "ใกล้เป้า": "⚠️", "ต่ำกว่าเป้า": "🔴"}
BG_MAP    = {"บรรลุเป้า": "#defbe6", "ใกล้เป้า": "#fcf4d6", "ต่ำกว่าเป้า": "#fff1f1"}


def _waterfall_chart(df: pd.DataFrame, staff_name: str) -> go.Figure:
    """Waterfall คะแนนสะสมรายหัวข้อ"""
    data = df[df["score_obtained"].notna()].copy()
    fig = go.Figure(go.Waterfall(
        name="คะแนน",
        orientation="v",
        x=["คะแนนเริ่มต้น"] + [n[:25] + "…" if len(n) > 25 else n
                                for n in data["kpi_name"].tolist()],
        y=[0] + data["score_obtained"].tolist(),
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#28a745"}},
        decreasing={"marker": {"color": "#dc3545"}},
    ))
    fig.update_layout(
        title=f"คะแนนสะสม — {staff_name}",
        yaxis_title="คะแนน",
        height=400,
        margin=dict(t=50, b=80),
        font=dict(family="Sarabun, sans-serif"),
    )
    return fig


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
    st.header("👤 ผลงานรายบุคคล — Scorecard")
    _data_date_badge(filepath)

    # เลือกพนักงาน
    selected = st.session_state.get("selected_staff", STAFF_SHEETS[0])
    if selected not in STAFF_SHEETS:
        selected = STAFF_SHEETS[0]

    all_tabs = st.tabs([f"{'★ ' if s == selected else ''}{s}" for s in STAFF_SHEETS])

    for tab, sheet in zip(all_tabs, STAFF_SHEETS):
        with tab:
            _render_one_staff(sheet, filepath)


def _render_one_staff(sheet: str, filepath: str) -> None:
    meta   = STAFF_META.get(sheet, {})
    kpi_df = load_staff_kpi(sheet, filepath)

    # Header card
    summary_df = load_dashboard_summary(filepath)
    score_perf = 0.0
    if summary_df is not None:
        match = summary_df[summary_df["name"].str.contains(
            meta.get("full_name", "").split()[-1], na=False
        )]
        score_perf = match["score_performance"].values[0] if len(match) else 0.0

    max_perf = 70.0
    pct = round(score_perf / max_perf * 100, 1) if max_perf else 0
    status = "บรรลุเป้า" if pct >= 100 else "ใกล้เป้า" if pct >= 80 else "ต่ำกว่าเป้า"
    color  = COLOR_MAP[status]

    c_info, c_gauge = st.columns([2, 1])
    with c_info:
        tag_label = {"บรรลุเป้า": "บรรลุเป้า", "ใกล้เป้า": "ใกล้เป้า", "ต่ำกว่าเป้า": "ต่ำกว่าเป้า"}[status]
        st.markdown(f"""
        <div style="background:#f4f4f4;border-left:4px solid {color};
                    border-radius:0px;padding:16px 20px;margin-bottom:10px;
                    border-bottom:1px solid #e0e0e0;">
          <div style="font-size:11px;color:#525252;letter-spacing:0.32px;
                      text-transform:uppercase;margin-bottom:6px;">
            {meta.get('position','')} &nbsp;·&nbsp; {meta.get('zone','')}
          </div>
          <div style="font-size:22px;font-weight:600;color:#161616;margin-bottom:8px;">
            {meta.get('full_name', sheet)}
          </div>
          <div style="font-size:38px;font-weight:300;color:{color};line-height:1.1;">{score_perf:.2f}</div>
          <div style="font-size:12px;color:#525252;letter-spacing:0.32px;margin-bottom:12px;">
            / {max_perf:.0f} คะแนน Performance
          </div>
          <span style="background:{BG_MAP[status]};color:{color};padding:4px 12px;
                       border-radius:24px;font-size:11px;font-weight:600;letter-spacing:0.16px;">
            {EMOJI_MAP[status]} {tag_label}
          </span>
        </div>
        """, unsafe_allow_html=True)

    with c_gauge:
        st.plotly_chart(
            gauge_chart(pct, f"Performance\n{score_perf:.2f}/{max_perf:.0f}"),
            use_container_width=True,
        )

    if kpi_df is None or kpi_df.empty:
        st.info(f"ไม่พบข้อมูล KPI ของ {sheet}")
        return

    # Quick metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("✅ บรรลุเป้า",   (kpi_df["status"] == "บรรลุเป้า").sum())
    m2.metric("⚠️ ใกล้เป้า",   (kpi_df["status"] == "ใกล้เป้า").sum())
    m3.metric("🔴 ต่ำกว่าเป้า", (kpi_df["status"] == "ต่ำกว่าเป้า").sum())

    # Horizontal bar: score obtained vs weight
    chart_df = kpi_df[kpi_df["score_obtained"].notna()].copy()
    if not chart_df.empty:
        chart_df["pct_score"] = chart_df.apply(
            lambda r: round(r["score_obtained"] / r["weight"] * 100, 1)
            if r["weight"] and r["weight"] > 0 else 0, axis=1
        )
        colors = chart_df["status"].map(
            lambda s: COLOR_MAP.get(s, "#aaa")
        ).tolist()
        short = [n[:40] + "…" if len(n) > 40 else n for n in chart_df["kpi_name"]]
        fig = go.Figure(go.Bar(
            y=short,
            x=chart_df["pct_score"],
            orientation="h",
            marker_color=colors,
            text=[f"{r['score_obtained']:.2f}/{r['weight']:.1f}" for _, r in chart_df.iterrows()],
            textposition="outside",
        ))
        fig.add_vline(x=100, line_dash="dash", line_color="black")
        fig.update_layout(
            title=dict(text="คะแนนที่ได้ vs คะแนนเต็ม รายหัวข้อ (%)",
                       font=dict(size=16, weight=300, color="#161616")),
            xaxis=dict(range=[0, 100], title="% คะแนน",
                       gridcolor="#e0e0e0", linecolor="#c6c6c6", tickfont=dict(color="#525252")),
            yaxis=dict(tickfont=dict(color="#161616", size=13)),
            height=max(350, len(chart_df) * 42),
            margin=dict(l=10, r=100, t=50, b=30),
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font=dict(family="IBM Plex Sans, Sarabun, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ตารางละเอียด
    st.subheader(f"📋 ตาราง KPI — {sheet}")
    disp = kpi_df.copy()
    disp["สถานะ"] = disp["status"].map(lambda s: EMOJI_MAP.get(s, ""))
    disp = disp.rename(columns={
        "kpi_name":      "หัวข้อ KPI",
        "unit":          "หน่วย",
        "weight":        "น้ำหนัก",
        "target":        "เป้าหมาย",
        "actual":        "ผลจริง",
        "score_obtained":"คะแนนที่ได้",
        "achievement_rate": "อัตรา (%)",
    })
    show_cols = ["หัวข้อ KPI", "หน่วย", "น้ำหนัก", "เป้าหมาย",
                 "ผลจริง", "คะแนนที่ได้", "อัตรา (%)", "สถานะ"]
    show_cols = [c for c in show_cols if c in disp.columns]
    st.dataframe(disp[show_cols], use_container_width=True, hide_index=True)
