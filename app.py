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
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@300;400;600&family=IBM+Plex+Sans:wght@300;400;600&family=Sarabun:wght@300;400;600&display=swap');

/* ── IBM Carbon Design System tokens ── */
:root {
  --cds-background:        #ffffff;
  --cds-layer-01:          #f4f4f4;
  --cds-layer-02:          #e0e0e0;
  --cds-text-primary:      #161616;
  --cds-text-secondary:    #525252;
  --cds-border-subtle:     #c6c6c6;
  --cds-border-strong:     #8d8d8d;
  --cds-interactive:       #0f62fe;
  --cds-support-success:   #24a148;
  --cds-support-warning:   #b28600;
  --cds-support-error:     #da1e28;
}

/* ── Base typography ── */
html, body, [class*="css"] {
  font-family: 'IBM Plex Sans Thai', 'IBM Plex Sans', 'Sarabun', sans-serif !important;
  color: var(--cds-text-primary);
  background-color: var(--cds-background);
}
div[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar — Carbon Gray 100 dark ── */
section[data-testid="stSidebar"] {
  background-color: #161616 !important;
  border-right: 1px solid #393939 !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
  color: #c6c6c6 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  color: #f4f4f4 !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] hr {
  border-color: #393939 !important;
}
/* Radio selected item highlight */
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover span {
  color: #ffffff !important;
}

/* ── Page headers ── */
h1 { font-size: 2rem !important; font-weight: 300 !important;
     color: #161616 !important; letter-spacing: 0 !important; }
h2 { font-size: 1.5rem  !important; font-weight: 300 !important;
     color: #161616 !important; }
h3 { font-size: 1.25rem !important; font-weight: 600 !important;
     color: #161616 !important; }

/* ── Metrics ── */
[data-testid="stMetricLabel"] {
  font-size: 12px !important; color: #525252 !important;
  letter-spacing: 0.32px !important; font-weight: 400 !important;
}
[data-testid="stMetricValue"] {
  font-size: 2rem !important; font-weight: 300 !important; color: #161616 !important;
}
[data-testid="metric-container"] {
  background: #f4f4f4;
  border-left: 4px solid #0f62fe;
  padding: 12px 16px !important;
  border-radius: 0px !important;
}

/* ── Tabs — Carbon underline style ── */
.stTabs [data-baseweb="tab"] {
  font-size: 14px !important; font-weight: 400 !important;
  letter-spacing: 0.16px !important; color: #525252 !important;
  border-radius: 0px !important;
  border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
  color: #161616 !important;
  border-bottom: 2px solid #0f62fe !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid #e0e0e0 !important;
  gap: 0 !important;
}

/* ── Buttons — Carbon primary, 0px radius ── */
.stButton > button {
  border-radius: 0px !important;
  background-color: #0f62fe !important;
  color: #ffffff !important;
  font-weight: 400 !important;
  font-family: 'IBM Plex Sans Thai', 'IBM Plex Sans', sans-serif !important;
  height: 48px !important;
  border: none !important;
  letter-spacing: 0.16px !important;
  font-size: 14px !important;
}
.stButton > button:hover { background-color: #0353e9 !important; }
.stButton > button:active { background-color: #002d9c !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
  border-radius: 0px !important;
  border: none !important;
  border-bottom: 2px solid #161616 !important;
  background-color: #f4f4f4 !important;
  font-size: 14px !important;
}

/* ── Dataframe ── */
.stDataFrame { border: none !important; }
.stDataFrame table { font-size: 14px !important; letter-spacing: 0.16px !important; }
.stDataFrame thead tr th {
  background: #161616 !important; color: #f4f4f4 !important;
  font-weight: 600 !important; font-size: 12px !important;
  letter-spacing: 0.32px !important; border: none !important;
  text-transform: uppercase !important;
}
.stDataFrame tbody tr:nth-child(even) td { background: #f4f4f4 !important; }
.stDataFrame tbody tr:hover td { background: #e8e8e8 !important; }
.stDataFrame tbody tr td { border-bottom: 1px solid #e0e0e0 !important; }

/* ── Divider ── */
hr { border-color: #e0e0e0 !important; margin: 24px 0 !important; }

/* ── Warning/Info banners ── */
[data-testid="stAlert"] { border-radius: 0px !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# AUTHENTICATION GATE
# =========================================================
from auth.login import check_login, render_login_page, logout

if not check_login():
    render_login_page()
    st.stop()

# =========================================================
# SIDEBAR (เฉพาะผู้ที่ login แล้ว)
# =========================================================
with st.sidebar:
    try:
        st.image(
            "https://upload.wikimedia.org/wikipedia/th/thumb/9/9d/Logo_BAAC.png/240px-Logo_BAAC.png",
            width=80,
        )
    except Exception:
        pass
    st.markdown("### 🏦 ธ.ก.ส. หน่วยลำพญากลาง")
    st.divider()

    # ---- ข้อมูลผู้ใช้ ----
    emp_name = st.session_state.get("employee_name", "")
    emp_id   = st.session_state.get("employee_id", "")
    st.markdown(
        f'<div style="font-size:11px;color:#8d8d8d;letter-spacing:0.32px;'
        f'text-transform:uppercase;margin-bottom:4px;">ผู้ใช้งาน</div>'
        f'<div style="font-size:14px;font-weight:600;color:#f4f4f4;margin-bottom:2px;">{emp_name}</div>'
        f'<div style="font-size:11px;color:#6f6f6f;letter-spacing:0.32px;">รหัส {emp_id}</div>',
        unsafe_allow_html=True,
    )
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
    # ---- ปุ่ม Logout ----
    if st.button("🔓 ออกจากระบบ", use_container_width=True):
        logout()

    if selected_year == "2568":
        file_ok = os.path.exists(YEAR_FILES["2568"])

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
