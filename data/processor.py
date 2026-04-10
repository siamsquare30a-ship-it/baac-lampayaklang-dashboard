# data/processor.py — คำนวณ KPI และจัดกลุ่มข้อมูล

import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import THRESHOLDS, COLOR_MAP, STATUS_EMOJI, LOWER_IS_BETTER


def classify_status(rate: float, category: str) -> str:
    """จำแนกสถานะตามอัตราบรรลุเป้า (%) — NPL ยิ่งต่ำยิ่งดี"""
    if category in LOWER_IS_BETTER:
        # NPL: rate ต่ำ = ดี → invert
        rate = 200 - rate  # rate=50 → 150 (ดีมาก), rate=150 → 50 (แย่)

    if rate >= THRESHOLDS["green"]:
        return "บรรลุเป้า"
    elif rate >= THRESHOLDS["yellow"]:
        return "ใกล้เป้า"
    else:
        return "ต่ำกว่าเป้า"


def add_kpi_columns(df: pd.DataFrame) -> pd.DataFrame:
    """เพิ่มคอลัมน์ achievement_rate, status, color"""
    df = df.copy()
    # ใช้ข้อมูลเดือนล่าสุดต่อลูกค้าต่อ category (สะสม)
    if "month" in df.columns:
        latest_month_idx = df.groupby(
            ["customer_id", "category", "zone_id", "period"]
        )["month"].transform(
            lambda s: s.map({m: i for i, m in enumerate(
                ["ต.ค.", "พ.ย.", "ธ.ค.", "ม.ค.", "ก.พ.", "มี.ค.",
                 "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย."]
            )})
        )
        max_idx = df.groupby(
            ["customer_id", "category", "zone_id", "period"]
        )["month"].transform(
            lambda s: s.map({m: i for i, m in enumerate(
                ["ต.ค.", "พ.ย.", "ธ.ค.", "ม.ค.", "ก.พ.", "มี.ค.",
                 "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย."]
            )}).max()
        )
        df = df[latest_month_idx == max_idx].copy()

    df["achievement_rate"] = df.apply(
        lambda r: round(r["actual"] / r["target"] * 100, 2)
        if r["target"] > 0 else 0.0, axis=1
    )
    df["status"] = df.apply(
        lambda r: classify_status(r["achievement_rate"], r["category"]), axis=1
    )
    df["color"]  = df["status"].map(COLOR_MAP)
    df["emoji"]  = df["status"].map(STATUS_EMOJI)
    return df


# =========================================================
# LEVEL 1 — ภาพรวม Branch
# =========================================================
def branch_summary(df: pd.DataFrame) -> pd.DataFrame:
    """รวม actual/target ระดับ branch แยกตาม category"""
    g = df.groupby("category", as_index=False).agg(
        target=("target", "sum"),
        actual=("actual", "sum"),
    )
    g["achievement_rate"] = g.apply(
        lambda r: round(r["actual"] / r["target"] * 100, 2)
        if r["target"] > 0 else 0.0, axis=1
    )
    g["status"] = g.apply(
        lambda r: classify_status(r["achievement_rate"], r["category"]), axis=1
    )
    g["color"]  = g["status"].map(COLOR_MAP)
    g["emoji"]  = g["status"].map(STATUS_EMOJI)
    return g


def branch_trend(df: pd.DataFrame) -> pd.DataFrame:
    """รวม actual รายเดือน ระดับ branch (ใช้ทุก category)"""
    if "month" not in df.columns:
        return pd.DataFrame()
    month_order = ["ต.ค.", "พ.ย.", "ธ.ค.", "ม.ค.", "ก.พ.", "มี.ค.",
                   "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย."]
    g = df.groupby(["month", "category"], as_index=False).agg(
        actual=("actual", "sum"),
        target=("target", "sum"),
    )
    g["month_order"] = g["month"].map({m: i for i, m in enumerate(month_order)})
    return g.sort_values("month_order")


# =========================================================
# LEVEL 2 — ภาพรวม Zone
# =========================================================
def zone_summary(df: pd.DataFrame) -> pd.DataFrame:
    """รวม actual/target ระดับ zone แยกตาม category"""
    g = df.groupby(["zone_id", "category"], as_index=False).agg(
        target=("target", "sum"),
        actual=("actual", "sum"),
    )
    g["achievement_rate"] = g.apply(
        lambda r: round(r["actual"] / r["target"] * 100, 2)
        if r["target"] > 0 else 0.0, axis=1
    )
    g["status"] = g.apply(
        lambda r: classify_status(r["achievement_rate"], r["category"]), axis=1
    )
    g["color"]  = g["status"].map(COLOR_MAP)
    g["emoji"]  = g["status"].map(STATUS_EMOJI)
    return g


def zone_overall(df: pd.DataFrame) -> pd.DataFrame:
    """คะแนนเฉลี่ยทุก category ต่อ zone (สำหรับ ranking)"""
    zs = zone_summary(df)
    g = zs.groupby("zone_id", as_index=False).agg(
        avg_achievement=("achievement_rate", "mean"),
        total_actual=("actual", "sum"),
        total_target=("target", "sum"),
    )
    g["overall_rate"] = g.apply(
        lambda r: round(r["total_actual"] / r["total_target"] * 100, 2)
        if r["total_target"] > 0 else 0.0, axis=1
    )
    g = g.sort_values("overall_rate", ascending=False).reset_index(drop=True)
    g["rank"] = g.index + 1
    return g


# =========================================================
# LEVEL 3 — รายลูกค้า
# =========================================================
def customer_summary(df: pd.DataFrame, zone_id: str) -> pd.DataFrame:
    """รายละเอียดลูกค้าใน zone นี้ ทุก category"""
    filtered = df[df["zone_id"] == zone_id]
    g = filtered.groupby(
        ["customer_id", "customer_name", "category"], as_index=False
    ).agg(
        target=("target", "sum"),
        actual=("actual", "sum"),
    )
    g["achievement_rate"] = g.apply(
        lambda r: round(r["actual"] / r["target"] * 100, 2)
        if r["target"] > 0 else 0.0, axis=1
    )
    g["status"] = g.apply(
        lambda r: classify_status(r["achievement_rate"], r["category"]), axis=1
    )
    g["color"]  = g["status"].map(COLOR_MAP)
    g["emoji"]  = g["status"].map(STATUS_EMOJI)
    return g


def customer_alerts(df: pd.DataFrame, threshold: float = 80.0) -> pd.DataFrame:
    """ดึงลูกค้าที่มีหมวดใดหมวดหนึ่งต่ำกว่า threshold"""
    proc = add_kpi_columns(df)
    bad  = proc[proc["achievement_rate"] < threshold]
    return bad[[
        "zone_id", "customer_id", "customer_name",
        "category", "target", "actual", "achievement_rate", "status"
    ]].sort_values(["zone_id", "achievement_rate"])
