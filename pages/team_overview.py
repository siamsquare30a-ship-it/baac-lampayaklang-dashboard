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

COLOR_MAP = {"บรรลุเป้า": "#059669", "ใกล้เป้า": "#d97706", "ต่ำกว่าเป้า": "#dc2626"}
EMOJI_MAP = {"บรรลุเป้า": "✅", "ใกล้เป้า": "⚠️", "ต่ำกว่าเป้า": "🔴"}
BG_MAP    = {"บรรลุเป้า": "#ecfdf5", "ใกล้เป้า": "#fffbeb", "ต่ำกว่าเป้า": "#fef2f2"}

import re as _re

def _kpi_sort_key(name: str):
    nums = _re.findall(r'\d+', name.split()[0] if name.strip() else "")
    return tuple(int(n) for n in nums) if nums else (999,)

def _sort_kpi(df: pd.DataFrame) -> pd.DataFrame:
    if "kpi_name" not in df.columns:
        return df
    df = df.copy()
    df["_sort_key"] = df["kpi_name"].apply(_kpi_sort_key)
    df = df.sort_values("_sort_key").drop(columns=["_sort_key"])
    return df.reset_index(drop=True)


def _staff_card(name: str, position: str, score: float, max_score: float = 70.0) -> None:
    rate   = round(score / max_score * 100, 1)
    status = "บรรลุเป้า" if rate >= 100 else "ใกล้เป้า" if rate >= 80 else "ต่ำกว่าเป้า"
    color  = COLOR_MAP[status]
    bg     = BG_MAP[status]
    tag_label = {"บรรลุเป้า": "บรรลุเป้า", "ใกล้เป้า": "ใกล้เป้า", "ต่ำกว่าเป้า": "ต่ำกว่าเป้า"}[status]
    st.markdown(f"""
    <div style="background:#ffffff;border-left:4px solid {color};
                border-radius:8px;padding:16px;margin-bottom:8px;
                box-shadow:0 1px 3px rgba(0,0,0,0.08);">
      <div style="font-size:11px;color:#6b7280;letter-spacing:0.32px;
                  text-transform:uppercase;margin-bottom:6px;">{position}</div>
      <div style="font-size:18px;font-weight:600;color:#111827;margin-bottom:10px;">{name}</div>
      <div style="font-size:34px;font-weight:300;color:{color};line-height:1.1;">{score:.2f}</div>
      <div style="font-size:12px;color:#6b7280;letter-spacing:0.32px;margin-bottom:10px;">/ {max_score:.0f} คะแนน</div>
      <span style="background:{bg};color:{color};padding:2px 10px;
                   border-radius:20px;font-size:11px;font-weight:600;
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


def _team_banner() -> None:
    """Banner รูปทีม พร้อม overlay ชื่อหน่วยงาน"""
    import base64, os as _os
    banner_path = _os.path.join(_os.path.dirname(__file__), "..", "assets", "team_banner.jpg")
    try:
        with open(banner_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <style>
        /* ดัน banner ชิดขอบบน — ลบ padding ของ block-container เฉพาะหน้านี้ */
        .team-banner-wrap {{
            position: relative;
            width: calc(100% + 8rem);
            margin-left: -4rem;
            margin-top: -4rem;
            height: 320px;
            overflow: hidden;
            margin-bottom: 28px;
        }}
        @media (max-width: 768px) {{
            .team-banner-wrap {{ width: calc(100% + 2rem); margin-left: -1rem; margin-top: -2rem; }}
        }}
        </style>
        <div class="team-banner-wrap">
          <img src="data:image/jpeg;base64,{b64}"
               style="width:100%;height:100%;object-fit:cover;object-position:center 15%;" />
          <div style="
              position: absolute; inset: 0;
              background: linear-gradient(to right,
                  rgba(0,60,30,0.78) 0%,
                  rgba(0,60,30,0.40) 55%,
                  transparent 100%);
              display: flex; align-items: flex-end;
              padding: 0 40px 32px;
          ">
            <div>
              <div style="font-size:11px;color:#a7f3d0;letter-spacing:0.32px;
                          text-transform:uppercase;margin-bottom:6px;">
                  ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร
              </div>
              <div style="font-size:32px;font-weight:300;color:#ffffff;line-height:1.2;">
                  หน่วยลำพญากลาง
              </div>
              <div style="font-size:14px;color:#d1fae5;margin-top:6px;">
                  ผลการดำเนินงาน ปีบัญชี 2568
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass


def render(filepath: str = REAL_FILE) -> None:
    _team_banner()
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

    kpi_df = _sort_kpi(team_df[team_df.get("is_total", False) == False].copy())

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
    # ROW 3: KPI Score Bar Chart — แยก ต้องติดตาม / บรรลุแล้ว
    # =========================================================
    if not kpi_df.empty and "score" in kpi_df.columns:
        kpi_chart = kpi_df[kpi_df["score"] > 0].copy()
        kpi_chart["pct"] = kpi_chart.apply(
            lambda r: round(r["score"] / r["max_score"] * 100, 1)
            if r["max_score"] > 0 else 0, axis=1
        )

        needs_attn = kpi_chart[kpi_chart["pct"] < 100].copy()
        on_track   = kpi_chart[kpi_chart["pct"] >= 100].copy()

        def _make_team_bar(df: pd.DataFrame) -> go.Figure:
            colors      = df["status"].map(lambda s: COLOR_MAP.get(s, "#aaa")).tolist()
            short_names = [n[:35] + "…" if len(n) > 35 else n for n in df["kpi_name"]]
            fig = go.Figure(go.Bar(
                y=short_names, x=df["pct"], orientation="h",
                marker_color=colors,
                width=0.18,
                text=[f"{r['score']:.2f}/{r['max_score']:.1f} ({r['pct']:.0f}%)"
                      for _, r in df.iterrows()],
                textposition="outside",
                textfont=dict(size=11, color="#374151"),
            ))
            fig.add_vline(x=100, line_dash="dash", line_color="#9ca3af", line_width=1)
            fig.update_layout(
                xaxis=dict(title=None, range=[0, 130],
                           gridcolor="#f9fafb", linecolor="#e5e7eb",
                           tickfont=dict(color="#9ca3af", size=11)),
                yaxis=dict(tickfont=dict(color="#374151", size=12)),
                height=max(120, len(df) * 22 + 50),
                margin=dict(l=10, r=150, t=8, b=8),
                plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                font=dict(family="IBM Plex Sans, Sarabun, sans-serif"),
                showlegend=False,
                bargap=0.75,
            )
            return fig

        # ── ต้องติดตาม ──
        if not needs_attn.empty:
            st.markdown(
                f'<div style="font-size:13px;font-weight:600;color:#d97706;'
                f'margin-bottom:4px;">⚠️ ต้องติดตาม ({len(needs_attn)} รายการ)</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(_make_team_bar(needs_attn), use_container_width=True)
        else:
            st.markdown(
                '<div style="background:#ecfdf5;border-left:4px solid #059669;'
                'padding:12px 16px;border-radius:8px;font-size:14px;color:#059669;'
                'font-weight:600;">✅ ทุกหัวข้อ KPI ของทีมบรรลุเป้าหมายแล้ว!</div>',
                unsafe_allow_html=True,
            )

        # ── บรรลุแล้ว (ซ่อนไว้ใน expander) ──
        if not on_track.empty:
            with st.expander(f"✅ KPI ที่บรรลุเป้าแล้ว ({len(on_track)} รายการ)"):
                st.plotly_chart(_make_team_bar(on_track), use_container_width=True)

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
