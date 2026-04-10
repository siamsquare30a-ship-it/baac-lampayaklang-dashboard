# app.py — Dashboard หลัก ธ.ก.ส. หน่วยลำพญากลาง
# รัน: streamlit run app.py

import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# =========================================================
# ค้นหาไฟล์ Excel อัตโนมัติ
# =========================================================
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)

def _find_excel(filename: str) -> str:
    candidates = [
        os.path.join(_THIS_DIR, "data", "raw", filename),
        os.path.join(_PARENT_DIR, filename),
        os.path.join(_THIS_DIR, filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

# ไฟล์แต่ละปีบัญชี
YEAR_FILES = {
    "2568": _find_excel("ป2หน่วยลำพญากลาง.xlsx"),
    "2569": None,  # ยังไม่มีไฟล์ — Coming Soon
}

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Dashboard | ธ.ก.ส. ลำพญากลาง",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sarabun', sans-serif !important; }
div[data-testid="stSidebarNav"] { display: none; }
.stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    try:
        st.image(
            "https://upload.wikimedia.org/wikipedia/th/thumb/9/9d/Logo_BAAC.png/240px-Logo_BAAC.png",
            width=100,
        )
    except Exception:
        pass
    st.markdown("### 🏦 ธ.ก.ส. หน่วยลำพญากลาง")
    st.divider()

    # ---- เลือกปีบัญชี ----
    selected_year = st.radio(
        "📅 ปีบัญชี",
        options=["2568", "2569"],
        format_func=lambda y: f"พ.ศ. {y}" + (" ✅" if y == "2568" else " ⏳"),
        key="year_select",
        horizontal=True,
    )
    st.session_state["selected_year"] = selected_year
    st.divider()

    # เมนูหลัก — แสดงเฉพาะปีที่มีข้อมูล
    if selected_year == "2568":
        page = st.radio(
            "เมนูหลัก",
            options=["🏦 ภาพรวมทีม", "📍 เปรียบเทียบรายเขต", "👤 รายบุคคล"],
            key="nav",
        )
        page_key = {
            "🏦 ภาพรวมทีม":         "team",
            "📍 เปรียบเทียบรายเขต":  "zone",
            "👤 รายบุคคล":           "individual",
        }[page]
    else:
        page_key = "coming_soon"
        st.info("⏳ รอประกาศ KPI ปีบัญชี 2569")

    st.session_state["current_page"] = page_key

    st.divider()
    if selected_year == "2568":
        file_ok = os.path.exists(YEAR_FILES["2568"])
        st.caption(f"📂 `ป2หน่วยลำพญากลาง.xlsx`")
        if file_ok:
            st.success("พบไฟล์ข้อมูล ✓")
        else:
            st.error("ไม่พบไฟล์")
        if st.button("🔄 รีโหลดข้อมูล", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# =========================================================
# ROUTE
# =========================================================
import pages.team_overview  as page_team
import pages.zone_compare   as page_zone
import pages.individual     as page_individual
import pages.coming_soon    as page_coming_soon

current = st.session_state.get("current_page", "team")

if current == "coming_soon":
    page_coming_soon.render(year="2569")

elif current in ("team", "zone", "individual"):
    REAL_FILE = YEAR_FILES["2568"]
    if not os.path.exists(REAL_FILE):
        st.error(f"❌ ไม่พบไฟล์ข้อมูล กรุณาวางไฟล์ **ป2หน่วยลำพญากลาง.xlsx** ใน `data/raw/`")
        st.stop()

    if current == "team":
        page_team.render(REAL_FILE)
    elif current == "zone":
        page_zone.render(REAL_FILE)
    elif current == "individual":
        page_individual.render(REAL_FILE)
