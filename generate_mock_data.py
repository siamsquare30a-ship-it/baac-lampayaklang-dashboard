# generate_mock_data.py — สร้างข้อมูลตัวอย่างสำหรับทดสอบ Dashboard
# รัน: python generate_mock_data.py

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_FOLDER, ZONES, CATEGORIES, CATEGORY_FILES, PERIOD

np.random.seed(42)

# จำนวนลูกค้าต่อเขต
CUSTOMERS_PER_ZONE = 15

# เดือนในปีงบประมาณ (ต.ค. – ก.ย.)
MONTHS = [
    "ต.ค.", "พ.ย.", "ธ.ค.",
    "ม.ค.", "ก.พ.", "มี.ค.",
    "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.",
]

# ชื่อลูกค้าจำลอง
FIRST_NAMES = ["สมชาย", "สมหญิง", "วิชัย", "นิภา", "ประสิทธิ์", "มาลี",
               "ชาญ", "รัตนา", "สุรชัย", "อนงค์", "บุญมี", "สุดา",
               "ธนกร", "พรทิพย์", "วรวิทย์"]
LAST_NAMES  = ["ใจดี", "มีสุข", "เกษตรกร", "ดีงาม", "รักษ์ดี",
               "บุญมาก", "สุขใจ", "มั่นคง", "เจริญ", "พัฒนา",
               "ทองดี", "แสงงาม", "ชาติไทย", "รุ่งเรือง", "ศรีดี"]


def make_customer_id(zone_idx: int, cust_idx: int) -> str:
    return f"Z{zone_idx+1:02d}-C{cust_idx+1:03d}"


def make_customer_name(cust_idx: int) -> str:
    fn = FIRST_NAMES[cust_idx % len(FIRST_NAMES)]
    ln = LAST_NAMES[(cust_idx * 3) % len(LAST_NAMES)]
    return f"{fn} {ln}"


def build_records(category: str) -> pd.DataFrame:
    """สร้าง records ทุก zone/ลูกค้า/เดือน สำหรับ 1 category"""
    rows = []
    # target ระดับ branch สำหรับ category นี้ (ล้านบาท)
    base_target = {"สินเชื่อ": 5.0, "เงินฝาก": 2.0,
                   "NPL": 0.5, "ประกัน": 0.3, "ผลิตภัณฑ์": 0.2}[category]

    for zi, zone in enumerate(ZONES):
        for ci in range(CUSTOMERS_PER_ZONE):
            cid   = make_customer_id(zi, ci)
            cname = make_customer_name(ci)
            # target รายลูกค้า (สุ่มรอบ base / จำนวนลูกค้า)
            cust_target = round(base_target / CUSTOMERS_PER_ZONE
                                * np.random.uniform(0.7, 1.3), 4)
            # สร้าง actual รายเดือนแบบสะสม
            cumulative_actual = 0.0
            for month in MONTHS:
                monthly_achievement = np.random.uniform(0.6, 1.2)
                monthly_add = round(cust_target / 12 * monthly_achievement, 4)
                cumulative_actual = round(cumulative_actual + monthly_add, 4)
                rows.append({
                    "period":        PERIOD,
                    "month":         month,
                    "zone_id":       zone,
                    "customer_id":   cid,
                    "customer_name": cname,
                    "category":      category,
                    "target":        round(cust_target, 4),   # เป้าสะสมทั้งปี
                    "actual":        cumulative_actual,
                })
    return pd.DataFrame(rows)


def main():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    print(f"สร้างข้อมูลตัวอย่างใน: {DATA_FOLDER}")

    for cat, fname in CATEGORY_FILES.items():
        df = build_records(cat)
        out_path = os.path.join(DATA_FOLDER, fname)
        df.to_excel(out_path, index=False)
        print(f"  ✅ {fname}  ({len(df):,} rows)")

    print("\nสำเร็จ! วางไฟล์ Excel จริงใน data/raw/ แล้วรัน:")
    print("  streamlit run app.py")


if __name__ == "__main__":
    main()
