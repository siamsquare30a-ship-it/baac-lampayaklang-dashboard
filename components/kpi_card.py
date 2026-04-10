# components/kpi_card.py — KPI Card component

import streamlit as st
from config import COLOR_MAP


def kpi_card(label: str, target: float, actual: float,
             rate: float, status: str, unit: str = "ล้านบาท") -> None:
    """
    แสดง KPI Card 1 ตัว
    Args:
        label:  ชื่อหมวด
        target: เป้าหมาย
        actual: ผลจริง
        rate:   achievement_rate (%)
        status: บรรลุเป้า / ใกล้เป้า / ต่ำกว่าเป้า
        unit:   หน่วย
    """
    color = COLOR_MAP.get(status, "#6c757d")
    bg    = {"บรรลุเป้า": "#d4edda",
             "ใกล้เป้า":  "#fff3cd",
             "ต่ำกว่าเป้า": "#f8d7da"}.get(status, "#f8f9fa")

    st.markdown(f"""
    <div style="
        background:{bg};
        border-left: 6px solid {color};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    ">
        <div style="font-size:13px; color:#555; font-weight:600;">{label}</div>
        <div style="font-size:22px; font-weight:700; color:{color};">{rate:.1f}%</div>
        <div style="font-size:12px; color:#666;">
            จริง: <b>{actual:,.2f}</b> / เป้า: <b>{target:,.2f}</b> {unit}
        </div>
        <div style="font-size:11px; color:{color}; font-weight:600; margin-top:4px;">
            {"✅" if status == "บรรลุเป้า" else "⚠️" if status == "ใกล้เป้า" else "🔴"}
        </div>
    </div>
    """, unsafe_allow_html=True)
