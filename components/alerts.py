# components/alerts.py — แสดงรายการแจ้งเตือน

import streamlit as st
import pandas as pd
from config import COLOR_MAP, STATUS_EMOJI


def show_alert_table(alert_df: pd.DataFrame, max_rows: int = 50) -> None:
    """แสดงตาราง alert ลูกค้า/เขตที่ต่ำกว่าเป้า"""
    if alert_df.empty:
        st.success("ไม่มีรายการที่ต่ำกว่าเกณฑ์ 🎉")
        return

    st.warning(f"พบ {len(alert_df)} รายการที่ต้องติดตาม")

    display_df = alert_df.head(max_rows).copy()
    display_df["อัตรา (%)"] = display_df["achievement_rate"].map(
        lambda x: f"{x:.1f}%"
    )
    display_df["สถานะ"] = display_df["status"].map(
        lambda s: f"{STATUS_EMOJI.get(s,'')} {s}"
    )

    # rename columns
    display_df = display_df.rename(columns={
        "zone_id":       "เขตสินเชื่อ",
        "customer_id":   "รหัสลูกค้า",
        "customer_name": "ชื่อลูกค้า",
        "category":      "หมวด",
        "target":        "เป้า",
        "actual":        "จริง",
    })

    cols_show = ["เขตสินเชื่อ", "รหัสลูกค้า", "ชื่อลูกค้า",
                 "หมวด", "เป้า", "จริง", "อัตรา (%)", "สถานะ"]
    st.dataframe(
        display_df[cols_show],
        use_container_width=True,
        hide_index=True,
    )

    if len(alert_df) > max_rows:
        st.caption(f"แสดง {max_rows} จาก {len(alert_df)} รายการ — ดาวน์โหลด Excel เพื่อดูทั้งหมด")
