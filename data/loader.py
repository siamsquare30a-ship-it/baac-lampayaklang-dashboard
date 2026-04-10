# data/loader.py — โหลดและตรวจสอบข้อมูลจาก Excel

import os
import pandas as pd
import streamlit as st
from typing import Optional
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import DATA_FOLDER, CATEGORY_FILES

# คอลัมน์ที่ต้องมีในทุกไฟล์
REQUIRED_COLUMNS = {
    "period", "zone_id", "customer_id",
    "customer_name", "target", "actual", "category",
}


def _validate(df: pd.DataFrame, filepath: str) -> tuple[bool, list[str]]:
    """ตรวจสอบโครงสร้างและคุณภาพข้อมูล"""
    issues = []

    # 1. ตรวจคอลัมน์
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        issues.append(f"ขาดคอลัมน์: {missing_cols}")
        return False, issues

    # 2. ตรวจ target ≠ 0
    zero_target = df[df["target"] == 0]
    if not zero_target.empty:
        issues.append(f"พบ target = 0 จำนวน {len(zero_target)} แถว")

    # 3. ตรวจ duplicate (customer_id + period + month ต่อ category)
    key_cols = ["customer_id", "period", "category"]
    if "month" in df.columns:
        key_cols.append("month")
    dups = df[df.duplicated(subset=key_cols, keep=False)]
    if not dups.empty:
        issues.append(f"พบข้อมูลซ้ำ {len(dups)} แถว")

    return True, issues


@st.cache_data(show_spinner=False)
def load_all() -> Optional[pd.DataFrame]:
    """
    โหลดไฟล์ Excel ทุกหมวด รวมเป็น DataFrame เดียว
    คืนค่า None หากไม่มีไฟล์เลย
    """
    frames = []
    warnings_list = []

    for category, fname in CATEGORY_FILES.items():
        fpath = os.path.join(DATA_FOLDER, fname)

        if not os.path.exists(fpath):
            warnings_list.append(f"⚠️ ไม่พบไฟล์: {fname} — ข้ามหมวด '{category}'")
            continue

        try:
            df = pd.read_excel(fpath, engine="openpyxl")
            df.columns = df.columns.str.strip().str.lower()
            ok, issues = _validate(df, fpath)

            if not ok:
                warnings_list.append(
                    f"❌ {fname} ไม่ผ่านการตรวจสอบ: {'; '.join(issues)}"
                )
                continue

            if issues:
                warnings_list.append(f"⚠️ {fname}: {'; '.join(issues)}")

            # ถ้าไฟล์ไม่มีคอลัมน์ category ให้เติมเอง
            if "category" not in df.columns or df["category"].isna().all():
                df["category"] = category

            frames.append(df)

        except Exception as e:
            warnings_list.append(f"❌ โหลด {fname} ล้มเหลว: {e}")

    # แสดง warnings ใน sidebar
    if warnings_list:
        with st.sidebar:
            st.markdown("### แจ้งเตือนข้อมูล")
            for w in warnings_list:
                st.markdown(w)

    if not frames:
        return None

    combined = pd.concat(frames, ignore_index=True)
    combined["target"] = pd.to_numeric(combined["target"], errors="coerce").fillna(0)
    combined["actual"] = pd.to_numeric(combined["actual"], errors="coerce").fillna(0)
    return combined
