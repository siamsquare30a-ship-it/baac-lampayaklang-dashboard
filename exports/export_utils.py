# exports/export_utils.py — ส่งออกข้อมูลเป็น Excel / PDF

import io
import pandas as pd
import streamlit as st
from datetime import datetime


def df_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "ข้อมูล") -> bytes:
    """แปลง DataFrame → bytes ของ .xlsx"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buf.getvalue()


def download_excel_button(
    df: pd.DataFrame,
    label: str = "ดาวน์โหลด Excel",
    filename: str = "export",
    sheet_name: str = "ข้อมูล",
) -> None:
    """แสดงปุ่ม download Excel ใน Streamlit"""
    ts   = datetime.now().strftime("%Y%m%d_%H%M")
    data = df_to_excel_bytes(df, sheet_name=sheet_name)
    st.download_button(
        label=label,
        data=data,
        file_name=f"{filename}_{ts}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


def download_summary_excel(
    branch_df: pd.DataFrame,
    zone_df: pd.DataFrame,
    alert_df: pd.DataFrame,
) -> None:
    """ส่งออก Excel หลายชีต: ภาพรวม + เขต + แจ้งเตือน"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        branch_df.to_excel(writer, index=False, sheet_name="ภาพรวมสาขา")
        zone_df.to_excel(writer, index=False, sheet_name="เขตสินเชื่อ")
        alert_df.to_excel(writer, index=False, sheet_name="แจ้งเตือน")
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📥 ดาวน์โหลดรายงานสรุป (.xlsx)",
        data=buf.getvalue(),
        file_name=f"สรุปผลการดำเนินงาน_{ts}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
