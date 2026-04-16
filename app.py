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

/* ── Green Minimal Elegant theme tokens ── */
:root {
  --cds-background:        #ffffff;
  --cds-layer-01:          #f0fdf4;
  --cds-layer-02:          #d1fae5;
  --cds-text-primary:      #111827;
  --cds-text-secondary:    #6b7280;
  --cds-border-subtle:     #d1fae5;
  --cds-border-strong:     #6b7280;
  --cds-interactive:       #00693e;
  --cds-support-success:   #059669;
  --cds-support-warning:   #d97706;
  --cds-support-error:     #dc2626;
}

/* ── Base typography ── */
html, body, [class*="css"] {
  font-family: 'IBM Plex Sans Thai', 'IBM Plex Sans', 'Sarabun', sans-serif !important;
  color: var(--cds-text-primary);
  background-color: var(--cds-background);
}
div[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar — white with green accent ── */
section[data-testid="stSidebar"] {
  background-color: #ffffff !important;
  border-right: 1px solid #e5e7eb !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
  color: #374151 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  color: #111827 !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] hr {
  border-color: #e5e7eb !important;
}
/* Radio selected item highlight */
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
  color: #00693e !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover span {
  color: #00693e !important;
}

/* ── Page headers ── */
h1 { font-size: 2rem !important; font-weight: 300 !important;
     color: #111827 !important; letter-spacing: 0 !important; }
h2 { font-size: 1.5rem  !important; font-weight: 300 !important;
     color: #111827 !important; }
h3 { font-size: 1.25rem !important; font-weight: 600 !important;
     color: #111827 !important; }

/* ── Metrics ── */
[data-testid="stMetricLabel"] {
  font-size: 12px !important; color: #6b7280 !important;
  letter-spacing: 0.32px !important; font-weight: 400 !important;
}
[data-testid="stMetricValue"] {
  font-size: 2rem !important; font-weight: 300 !important; color: #111827 !important;
}
[data-testid="metric-container"] {
  background: #ffffff;
  border-left: 4px solid #00693e;
  padding: 12px 16px !important;
  border-radius: 8px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}

/* ── Tabs — green underline style ── */
.stTabs [data-baseweb="tab"] {
  font-size: 14px !important; font-weight: 400 !important;
  letter-spacing: 0.16px !important; color: #6b7280 !important;
  border-radius: 0px !important;
  border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
  color: #00693e !important;
  border-bottom: 2px solid #00693e !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid #e5e7eb !important;
  gap: 0 !important;
}

/* ── Buttons — green, 6px radius ── */
.stButton > button {
  border-radius: 6px !important;
  background-color: #00693e !important;
  color: #ffffff !important;
  font-weight: 400 !important;
  font-family: 'IBM Plex Sans Thai', 'IBM Plex Sans', sans-serif !important;
  height: 48px !important;
  border: none !important;
  letter-spacing: 0.16px !important;
  font-size: 14px !important;
}
.stButton > button:hover { background-color: #005c36 !important; }
.stButton > button:active { background-color: #004d2e !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
  border-radius: 6px !important;
  border: 1px solid #d1fae5 !important;
  border-bottom: 2px solid #00693e !important;
  background-color: #f0fdf4 !important;
  font-size: 14px !important;
}

/* ── Dataframe ── */
.stDataFrame { border: none !important; }
.stDataFrame table { font-size: 14px !important; letter-spacing: 0.16px !important; }
.stDataFrame thead tr th {
  background: #00693e !important; color: #ffffff !important;
  font-weight: 600 !important; font-size: 12px !important;
  letter-spacing: 0.32px !important; border: none !important;
  text-transform: uppercase !important;
}
.stDataFrame tbody tr:nth-child(even) td { background: #f0fdf4 !important; }
.stDataFrame tbody tr:hover td { background: #d1fae5 !important; }
.stDataFrame tbody tr td { border-bottom: 1px solid #e5e7eb !important; }

/* ── Divider ── */
hr { border-color: #e5e7eb !important; margin: 24px 0 !important; }

/* ── Warning/Info banners ── */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* ═══════════════════════════════════════
   MOBILE RESPONSIVE  (< 768px)
   Reference: IBM Carbon breakpoint "md"
   ═══════════════════════════════════════ */
@media (max-width: 768px) {

  /* Block container padding ลดลง */
  .block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-top: 0.5rem !important;
  }

  /* Columns → stack แนวตั้ง */
  [data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    gap: 0 !important;
  }
  [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    min-width: 100% !important;
    flex: 1 1 100% !important;
  }

  /* Headers ย่อลง */
  h1 { font-size: 1.4rem !important; }
  h2 { font-size: 1.2rem !important; }
  h3 { font-size: 1.1rem !important; }

  /* Metric card เต็มความกว้าง */
  [data-testid="metric-container"] {
    padding: 10px 12px !important;
  }
  [data-testid="stMetricValue"] { font-size: 1.6rem !important; }

  /* Tabs — scroll แนวนอน */
  .stTabs [data-baseweb="tab-list"] {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
  }
  .stTabs [data-baseweb="tab"] {
    font-size: 13px !important;
    padding: 8px 12px !important;
    white-space: nowrap !important;
  }

  /* Chart — scroll แนวนอน */
  [data-testid="stPlotlyChart"] {
    overflow-x: auto !important;
  }

  /* Banner สูงลดลงบนมือถือ */
  .team-banner-wrap {
    height: 180px !important;
    margin-left: -1rem !important;
    margin-top: -0.5rem !important;
    width: calc(100% + 2rem) !important;
  }

  /* Staff cards — text ย่อ */
  /* Login form */
  [data-testid="stForm"] {
    padding: 24px 20px 20px !important;
    margin: 40px auto 0 !important;
  }

  /* Selectbox เต็มกว้าง */
  .stSelectbox { width: 100% !important; }

  /* Dataframe scroll */
  [data-testid="stDataFrame"] {
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
  }

  /* ซ่อน sidebar default บนมือถือ (Streamlit จัดการเองอยู่แล้ว) */
}

/* ── Logout button — เขียวเข้ม ข้อความขาวชัด ── */
section[data-testid="stSidebar"] .stButton > button {
  background-color: #00693e !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  opacity: 1 !important;
}
section[data-testid="stSidebar"] .stButton > button * {
  color: #ffffff !important;
  opacity: 1 !important;
}
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
    # Logo ธ.ก.ส. — อ่านไฟล์ SVG และ embed เป็น base64
    import base64
    _logo_path = os.path.join(_THIS_DIR, "assets", "BAAC_Logo.svg")
    try:
        with open(_logo_path, "rb") as _f:
            _logo_b64 = base64.b64encode(_f.read()).decode()
        st.markdown(
            f'<div style="padding:4px 0 8px;">'
            f'<img src="data:image/svg+xml;base64,{_logo_b64}" '
            f'width="64" style="display:block;"/></div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown('<div style="font-size:22px;padding-bottom:8px;">🏦</div>',
                    unsafe_allow_html=True)
    st.divider()

    # ---- ข้อมูลผู้ใช้ ----
    emp_name = st.session_state.get("employee_name", "")
    emp_id   = st.session_state.get("employee_id", "")
    st.markdown(
        f'<div style="font-size:11px;color:#6b7280;letter-spacing:0.32px;'
        f'text-transform:uppercase;margin-bottom:4px;">ผู้ใช้งาน</div>'
        f'<div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:2px;">{emp_name}</div>'
        f'<div style="font-size:11px;color:#6b7280;letter-spacing:0.32px;">รหัส {emp_id}</div>',
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
