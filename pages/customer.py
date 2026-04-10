# pages/customer.py — Level 3: รายลูกค้า

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import CATEGORIES, COLOR_MAP, STATUS_EMOJI
from data.processor import customer_summary, add_kpi_columns
from components.kpi_card import kpi_card
from exports.export_utils import download_excel_button


def _flag_row(achievement_rate: float) -> str:
    """สีแถวในตาราง"""
    if achievement_rate >= 100:
        return "background-color:#d4edda"
    elif achievement_rate >= 80:
        return "background-color:#fff3cd"
    else:
        return "background-color:#f8d7da"


def render(df: pd.DataFrame) -> None:
    # ดึง zone จาก session_state (drill-down จากหน้า zone)
    selected_zone = st.session_state.get("selected_zone", None)

    available_zones = df["zone_id"].unique().tolist()
    selected_zone   = st.selectbox(
        "เลือกเขตสินเชื่อ",
        available_zones,
        index=available_zones.index(selected_zone)
        if selected_zone in available_zones else 0,
        key="cust_zone_select",
    )
    st.session_state["selected_zone"] = selected_zone

    st.header(f"👤 รายลูกค้า — {selected_zone}")

    cust_df = customer_summary(add_kpi_columns(df), selected_zone)

    # =========================================================
    # SEARCH & FILTER
    # =========================================================
    col_search, col_cat, col_status = st.columns([2, 1, 1])
    with col_search:
        search = st.text_input("ค้นหาชื่อ / รหัสลูกค้า", key="cust_search")
    with col_cat:
        cat_filter = st.selectbox("หมวด", ["ทั้งหมด"] + CATEGORIES, key="cust_cat")
    with col_status:
        status_opts = ["ทั้งหมด", "บรรลุเป้า", "ใกล้เป้า", "ต่ำกว่าเป้า"]
        status_filter = st.selectbox("สถานะ", status_opts, key="cust_status")

    filtered = cust_df.copy()
    if search:
        mask = (
            filtered["customer_name"].str.contains(search, na=False) |
            filtered["customer_id"].str.contains(search, na=False)
        )
        filtered = filtered[mask]
    if cat_filter != "ทั้งหมด":
        filtered = filtered[filtered["category"] == cat_filter]
    if status_filter != "ทั้งหมด":
        filtered = filtered[filtered["status"] == status_filter]

    st.caption(f"แสดง {len(filtered):,} รายการ")

    # =========================================================
    # ตารางลูกค้า
    # =========================================================
    display = filtered[[
        "customer_id", "customer_name", "category",
        "target", "actual", "achievement_rate", "status"
    ]].copy()
    display["สถานะ"] = display["status"].map(
        lambda s: f"{STATUS_EMOJI.get(s,'')} {s}"
    )
    display = display.rename(columns={
        "customer_id":   "รหัสลูกค้า",
        "customer_name": "ชื่อลูกค้า",
        "category":      "หมวด",
        "target":        "เป้า",
        "actual":        "จริง",
        "achievement_rate": "อัตรา (%)",
    })

    def style_func(row):
        rate_vals = filtered.loc[
            (filtered["customer_id"] == row["รหัสลูกค้า"]) &
            (filtered["category"]    == row["หมวด"]),
            "achievement_rate"
        ]
        v = rate_vals.values[0] if len(rate_vals) else 50
        return [_flag_row(v)] * len(row)

    st.dataframe(
        display.drop(columns=["status"]).style.apply(style_func, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    download_excel_button(
        filtered, label="📥 ดาวน์โหลดรายลูกค้า",
        filename=f"customers_{selected_zone}",
        sheet_name="รายลูกค้า",
    )

    st.divider()

    # =========================================================
    # Customer Profile Card
    # =========================================================
    st.subheader("🪪 โปรไฟล์ลูกค้ารายคน")
    cust_ids = filtered["customer_id"].unique().tolist()
    if not cust_ids:
        st.info("ไม่พบลูกค้า — ลองเปลี่ยนเงื่อนไขการค้นหา")
        return

    selected_cust = st.selectbox("เลือกลูกค้า", cust_ids, key="cust_profile_sel")
    cust_data     = cust_df[cust_df["customer_id"] == selected_cust]

    if not cust_data.empty:
        cname = cust_data["customer_name"].iloc[0]
        st.markdown(f"### {cname} ({selected_cust})")

        cols = st.columns(len(CATEGORIES))
        for col, cat in zip(cols, CATEGORIES):
            row = cust_data[cust_data["category"] == cat]
            with col:
                if row.empty:
                    st.markdown(f"**{cat}**\n\n_ไม่มีข้อมูล_")
                else:
                    r = row.iloc[0]
                    kpi_card(
                        label=cat,
                        target=r["target"],
                        actual=r["actual"],
                        rate=r["achievement_rate"],
                        status=r["status"],
                    )
