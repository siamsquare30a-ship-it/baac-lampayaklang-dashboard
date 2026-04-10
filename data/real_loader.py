# data/real_loader.py — อ่านไฟล์ Excel จริง ป2หน่วยลำพญากลาง.xlsx
# โครงสร้าง: Dashboard | ผลงานรวมทีม | ผลงานรายเขต | รายบุคคล (ภิชฌา/พรพงศ์/พิราวรรณ)

import pandas as pd
import os
import re
import streamlit as st
from typing import Optional

# ชื่อไฟล์จริง (วางใน data/raw/ หรือกำหนด path ตรงๆ)
REAL_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw", "ป2หน่วยลำพญากลาง.xlsx"
)

# ชื่อ sheet พนักงานรายคน
STAFF_SHEETS = ["ภิชฌา", "พรพงศ์", "พิราวรรณ"]

STAFF_META = {
    "ภิชฌา":    {"full_name": "นายภิชฌา ไทรทอง",           "position": "หัวหน้าหน่วยอำเภอ",      "zone": "ทีม"},
    "พรพงศ์":   {"full_name": "นายพรพงศ์ สุวรรณวกุล",       "position": "พนักงานพัฒนาธุรกิจ 7",   "zone": "เขต พรพงศ์"},
    "พิราวรรณ": {"full_name": "นางพิราวรรณ สุวรรณนิตย์กุล", "position": "พนักงานพัฒนาธุรกิจ 6",  "zone": "เขต พิราวรรณ"},
}


def _parse_sts(sts_str: str) -> tuple[float, float]:
    """แยก STS. เช่น '2.00/2' → (score=2.00, max=2.0)"""
    try:
        s = str(sts_str).strip()
        if "/" in s:
            parts = s.split("/")
            return float(parts[0]), float(parts[1])
        return float(s), float(s)
    except Exception:
        return 0.0, 0.0


@st.cache_data(show_spinner=False)
def load_dashboard_summary(filepath: str = REAL_FILE) -> Optional[pd.DataFrame]:
    """
    อ่าน sheet 'Dashboard' → คะแนนรวมรายคน
    คืน DataFrame: name, position, score_performance
    """
    try:
        df = pd.read_excel(filepath, sheet_name="Dashboard", header=None)
        rows = []
        for i, row in df.iterrows():
            vals = [v for v in row if pd.notna(v) and str(v).strip()]
            if len(vals) >= 3 and i >= 3:
                rows.append({
                    "name":              str(vals[0]).strip(),
                    "position":          str(vals[1]).strip(),
                    "score_performance": float(vals[2]) if vals[2] else 0.0,
                })
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"โหลด Dashboard sheet ล้มเหลว: {e}")
        return None


@st.cache_data(show_spinner=False)
def load_team_kpi(filepath: str = REAL_FILE) -> Optional[pd.DataFrame]:
    """
    อ่าน sheet 'ผลงานรวมทีม'
    คืน DataFrame: kpi_name, sts_raw, score, max_score, target, actual, unit,
                   achievement_rate, status
    """
    try:
        df = pd.read_excel(filepath, sheet_name="ผลงานรวมทีม", header=None)
        # Column mapping (ตรวจสอบจาก raw data):
        # col0=kpi_name, col2=STS.(score/max), col3=TARGET, col4=ACTUAL, col5=UNIT

        rows = []
        for i, row in df.iterrows():
            if i == 0:   # header row
                continue
            v0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if not v0 or v0 in ("nan", " "):
                continue

            # แถว "รวม" — บันทึกคะแนนรวม
            if v0 == "รวม":
                try:
                    sts_raw = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
                    sc, mx  = _parse_sts(sts_raw)
                    rows.append({
                        "kpi_name": "รวมคะแนนทั้งหมด",
                        "sts_raw":  sts_raw,
                        "score":    sc,
                        "max_score": mx,
                        "target":   mx,
                        "actual":   sc,
                        "unit":     "คะแนน",
                        "is_total": True,
                    })
                except Exception:
                    pass
                continue

            # ข้ามแถว section header
            if any(kw in v0 for kw in ["ผลการดำเนินงาน", "กระบวนการ",
                                        "1. ผล", "หนี้ถึงกำหนด"]):
                continue

            # แถว KPI ปกติ — STS. อยู่ที่ col2, TARGET=col3, ACTUAL=col4, UNIT=col5
            try:
                sts_raw = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
                sc, mx  = _parse_sts(sts_raw)
                if sc == 0.0 and mx == 0.0:
                    continue  # ไม่มี STS = section header

                target = _to_float(row.iloc[3])
                actual = _to_float(row.iloc[4])
                unit   = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ""
                rate   = _calc_rate(v0, target, actual)

                rows.append({
                    "kpi_name":   v0.lstrip(),
                    "sts_raw":    sts_raw,
                    "score":      sc,
                    "max_score":  mx,
                    "target":     target,
                    "actual":     actual,
                    "unit":       unit,
                    "achievement_rate": rate,
                    "status":     _classify(rate, v0),
                    "is_total":   False,
                })
            except Exception:
                continue

        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"โหลด ผลงานรวมทีม ล้มเหลว: {e}")
        return None


@st.cache_data(show_spinner=False)
def load_zone_kpi(filepath: str = REAL_FILE) -> Optional[pd.DataFrame]:
    """
    อ่าน sheet 'ผลงานรายเขต'
    คอลัมน์: kpi_name, sts_raw, target, actual_pira, actual_porn, unit
    คืน DataFrame แบบ long format สำหรับเปรียบเทียบ 2 เขต
    """
    try:
        df = pd.read_excel(filepath, sheet_name="ผลงานรายเขต", header=None)
        # Column mapping (ตรวจสอบจาก raw data):
        # col0=kpi_name, col2=STS.(score/max), col3=TARGET,
        # col4=actual_พิราวรรณ, col5=actual_พรพงศ์, col6=UNIT

        rows = []
        for i, row in df.iterrows():
            if i == 0:
                continue
            v0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if not v0 or v0 in ("nan", " "):
                continue
            if any(kw in v0 for kw in ["ผลการดำเนินงาน", "กระบวนการ", "รวม",
                                        "1. ผล", "หนี้ถึงกำหนด"]):
                continue

            try:
                sts_raw = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
                sc, mx  = _parse_sts(sts_raw)
                if sc == 0.0 and mx == 0.0:
                    continue

                target  = _to_float(row.iloc[3])
                a_pira  = _to_float(row.iloc[4]) if pd.notna(row.iloc[4]) else None
                a_porn  = _to_float(row.iloc[5]) if pd.notna(row.iloc[5]) else None
                unit    = str(row.iloc[6]).strip() if (len(row) > 6 and pd.notna(row.iloc[6])) else ""

                # เพิ่มทีละแถว สำหรับแต่ละเขต
                for zone, actual in [("เขต พิราวรรณ", a_pira), ("เขต พรพงศ์", a_porn)]:
                    if actual is None:
                        continue
                    rate = _calc_rate(v0, target, actual) if target else None
                    rows.append({
                        "kpi_name":        v0.lstrip(),
                        "sts_raw":         sts_raw,
                        "score":           sc,
                        "max_score":       mx,
                        "target":          target,
                        "actual":          actual,
                        "unit":            unit,
                        "zone":            zone,
                        "achievement_rate": rate,
                        "status":          _classify(rate, v0) if rate is not None else "-",
                    })
            except Exception:
                continue

        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"โหลด ผลงานรายเขต ล้มเหลว: {e}")
        return None


@st.cache_data(show_spinner=False)
def load_staff_kpi(sheet: str, filepath: str = REAL_FILE) -> Optional[pd.DataFrame]:
    """
    อ่าน sheet พนักงานรายคน (ภิชฌา / พรพงศ์ / พิราวรรณ)
    ดึงเฉพาะส่วน Performance (rows 17 เป็นต้นไป ถึง row ~55)
    คืน DataFrame: kpi_name, weight, target, actual, score_obtained, unit, achievement_rate, status
    """
    try:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        rows = []
        in_perf = False

        for i, row in df.iterrows():
            v0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""

            # เริ่มส่วน Performance
            if "ผลการดำเนินงาน" in v0 and "น้ำหนัก" in v0:
                in_perf = True
                continue
            if "หัวข้อประเมิน" in v0:
                in_perf = True
                continue
            # หยุดเมื่อจบส่วน
            if in_perf and ("รวมคะแนน" in v0 or "4. รวมคะแนน" in v0):
                break

            if not in_perf:
                continue
            if not v0 or v0 in ("nan", " "):
                continue
            # ข้ามบรรทัด sub-header
            if v0 in ("แผนงาน", "ยุทธศาสตร์", "งานสนับสนุนยุทธศาสตร์องค์กร",
                      "งานตามภารกิจ", "งานอื่นๆ"):
                continue

            try:
                # โครงสร้าง cols ของ individual sheet (จากการตรวจสอบจริง):
                # col0=kpi_name, col5=unit, col6=น้ำหนัก(weight),
                # col7=target(เป้า=เกณฑ์ระดับ 4*), col8-12=score_levels,
                # col13=actual(ผลจริง), col14=score_obtained(คะแนนที่ได้),
                # col16=max_score(คะแนนเต็ม 5**)
                vals = list(row)
                kpi_name = v0

                weight   = _to_float(vals[6])  if len(vals) > 6  else None
                target   = _to_float(vals[7])  if len(vals) > 7  else None
                actual   = _to_float(vals[13]) if len(vals) > 13 else None
                score_ob = _to_float(vals[14]) if len(vals) > 14 else None
                max_sc   = _to_float(vals[16]) if len(vals) > 16 else None
                unit     = str(vals[5]).strip() if (len(vals) > 5 and pd.notna(vals[5])) else ""

                if weight is None or weight == 0:
                    continue
                if actual is None and score_ob is None:
                    continue

                # achievement_rate: คะแนนที่ได้/น้ำหนัก × 100
                rate = (score_ob / weight * 100) if (score_ob is not None and weight) else None
                if rate is None and target and actual is not None:
                    rate = _calc_rate(kpi_name, target, actual)

                rows.append({
                    "kpi_name":        kpi_name.lstrip(),
                    "unit":            unit,
                    "weight":          weight,
                    "max_score":       max_sc if max_sc else weight,
                    "target":          target,
                    "actual":          actual,
                    "score_obtained":  score_ob,
                    "achievement_rate": rate,
                    "status":          _classify(rate, kpi_name) if rate is not None else "-",
                })
            except Exception:
                continue

        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"โหลด sheet '{sheet}' ล้มเหลว: {e}")
        return None


# =========================================================
# Helpers
# =========================================================
def _to_float(v) -> Optional[float]:
    try:
        f = float(str(v).replace(",", "").strip())
        return None if pd.isna(f) else f
    except Exception:
        return None


NPL_KEYWORDS = ["NPL", "gross npl", "ดอกเบี้ยค้าง", "หนี้ค้าง", "ค้างชำระเกิน"]


def _is_lower_better(kpi_name: str) -> bool:
    return any(kw.lower() in kpi_name.lower() for kw in NPL_KEYWORDS)


def _calc_rate(kpi_name: str, target, actual) -> Optional[float]:
    if target is None or actual is None:
        return None
    try:
        target_f = float(target)
        actual_f = float(actual)
        if target_f == 0:
            return None
        if _is_lower_better(kpi_name):
            # NPL: actual ต่ำกว่าเป้า = ดี → invert
            return round((target_f / actual_f) * 100, 2) if actual_f != 0 else 200.0
        return round(actual_f / target_f * 100, 2)
    except Exception:
        return None


def _classify(rate, kpi_name: str = "") -> str:
    if rate is None:
        return "-"
    if rate >= 100:
        return "บรรลุเป้า"
    elif rate >= 80:
        return "ใกล้เป้า"
    else:
        return "ต่ำกว่าเป้า"
