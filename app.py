# app.py — Dashboard หลัก ธ.ก.ส. หน่วยลำพญากลาง
# รัน: streamlit run app.py

import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# =========================================================
# ค้นหาไฟล์ Excel จริงอัตโนมัติ (ใน folder นี้และ folder แม่)
# =========================================================
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)

def _find_excel(filename: str) -> str:
    """ค้นหาไฟล์ Excel ใน dashboard/data/raw/ หรือ folder แม่"""
    candidates = [
        os.path.join(_THIS_DIR, "data", "raw", filename),
        os.path.join(_PARENT_DIR, filename),
        os.path.join(_THIS_DIR, filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]  # fallback (จะแสดง error ทีหลัง)

REAL_FILE = _find_excel("ป2หน่วยลำพญากลาง.xlsx")

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
    st.caption("ปีบัญชี พ.ศ. 2568")
    st.divider()

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
    st.session_state["current_page"] = page_key

    st.divider()
    st.caption(f"📂 ไฟล์: `{os.path.basename(REAL_FILE)}`")
    file_ok = os.path.exists(REAL_FILE)
    if file_ok:
        st.success("พบไฟล์ข้อมูล ✓")
    else:
        st.error("ไม่พบไฟล์ข้อมูล")

    if st.button("🔄 รีโหลดข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# =========================================================
# CHECK FILE
# =========================================================
if not file_ok:
    st.error(f"""
    ❌ ไม่พบไฟล์: `{REAL_FILE}`

    กรุณาวางไฟล์ **ป2หน่วยลำพญากลาง.xlsx** ใน:
    - `{os.path.join(_THIS_DIR, 'data', 'raw')}` หรือ
    - `{_PARENT_DIR}`
    """)
    st.stop()

# =========================================================
# ROUTE
# =========================================================
import pages.team_overview  as page_team
import pages.zone_compare   as page_zone
import pages.individual     as page_individual

current = st.session_state.get("current_page", "team")

if current == "team":
    page_team.render(REAL_FILE)
elif current == "zone":
    page_zone.render(REAL_FILE)
elif current == "individual":
    page_individual.render(REAL_FILE)
