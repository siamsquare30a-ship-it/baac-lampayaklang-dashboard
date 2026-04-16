# auth/login.py

import streamlit as st


def _get_employee_map() -> dict:
    try:
        return dict(st.secrets["employees"])
    except Exception:
        return {}


def check_login() -> bool:
    return st.session_state.get("authenticated", False)


def logout() -> None:
    st.session_state["authenticated"] = False
    st.session_state["employee_name"] = ""
    st.session_state["employee_id"]   = ""
    st.rerun()


def render_login_page() -> None:
    st.markdown("""
    <style>
    /* ซ่อน sidebar, header, toolbar */
    section[data-testid="stSidebar"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"]  { display: none !important; }

    /* พื้นหลังทั้งหน้า */
    html, body, .stApp, [class*="css"] {
        background-color: #f4f4f4 !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* จัด form ให้อยู่กึ่งกลาง */
    [data-testid="stForm"] {
        background: #ffffff !important;
        border-top: 4px solid #0f62fe !important;
        border-radius: 0 !important;
        padding: 36px 40px 32px !important;
        max-width: 420px !important;
        margin: 80px auto 0 !important;
        box-shadow: none !important;
    }

    /* Input field */
    [data-testid="stForm"] .stTextInput > div > div > input {
        background: #f4f4f4 !important;
        border: none !important;
        border-bottom: 2px solid #8d8d8d !important;
        border-radius: 0 !important;
        font-size: 20px !important;
        padding: 10px 12px !important;
        color: #161616 !important;
        letter-spacing: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    [data-testid="stForm"] .stTextInput > div > div > input:focus {
        border-bottom: 2px solid #0f62fe !important;
        box-shadow: none !important;
        outline: none !important;
    }
    [data-testid="stForm"] .stTextInput label {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #525252 !important;
        letter-spacing: 0.32px !important;
        text-transform: uppercase !important;
    }

    /* Submit button */
    [data-testid="stForm"] button[kind="primaryFormSubmit"],
    [data-testid="stForm"] button[type="submit"] {
        border-radius: 0 !important;
        background: #0f62fe !important;
        color: #fff !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        height: 48px !important;
        border: none !important;
        letter-spacing: 0.32px !important;
        width: 100% !important;
        margin-top: 4px !important;
    }
    [data-testid="stForm"] button:hover { background: #0353e9 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Top bar ──
    st.markdown("""
    <div style="background:#161616;padding:14px 32px;
                display:flex;align-items:center;gap:14px;width:100%;">
      <div style="font-size:26px;line-height:1;">🏦</div>
      <div>
        <div style="font-size:14px;font-weight:600;color:#f4f4f4;letter-spacing:.16px;">
            ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร
        </div>
        <div style="font-size:11px;color:#8d8d8d;letter-spacing:.32px;text-transform:uppercase;">
            หน่วยลำพญากลาง · สาขาลำพญากลาง
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Login form (ทุกอย่างรวมอยู่ใน st.form) ──
    with st.form("login_form", clear_on_submit=False):
        st.markdown("""
        <div style="font-size:11px;color:#525252;letter-spacing:.32px;
                    text-transform:uppercase;margin-bottom:4px;">Dashboard</div>
        <div style="font-size:28px;font-weight:300;color:#161616;
                    line-height:1.2;margin-bottom:2px;">ผลการดำเนินงาน</div>
        <div style="font-size:13px;color:#525252;margin-bottom:24px;">ปีบัญชี 2568</div>
        <div style="height:1px;background:#e0e0e0;margin-bottom:24px;"></div>
        """, unsafe_allow_html=True)

        emp_id = st.text_input(
            "รหัสพนักงาน",
            placeholder="เช่น 6000261",
            max_chars=10,
        )
        submitted = st.form_submit_button(
            "เข้าสู่ระบบ →",
            use_container_width=True,
        )

        st.markdown("""
        <div style="text-align:center;margin-top:16px;
                    font-size:11px;color:#8d8d8d;letter-spacing:.32px;">
            ใช้รหัสพนักงาน ธ.ก.ส. ของท่านในการเข้าสู่ระบบ
        </div>
        """, unsafe_allow_html=True)

    if submitted:
        _do_login(emp_id.strip())

    # Error message (แสดงนอก form เพื่อไม่ให้ layout กระตุก)
    err = st.session_state.get("login_error", "")
    if err:
        st.markdown(f"""
        <div style="max-width:420px;margin:8px auto 0;
                    background:#fff1f1;border-left:4px solid #da1e28;
                    padding:12px 16px;font-size:13px;color:#da1e28;">
            🔴 {err}
        </div>
        """, unsafe_allow_html=True)


def _do_login(emp_id: str) -> None:
    employees = _get_employee_map()

    if not employees:
        # Secrets ยังไม่ได้ตั้ง
        st.session_state["login_error"] = (
            "ระบบยังไม่ได้ตั้งค่า Secrets — กรุณาแจ้งผู้ดูแลระบบ"
        )
        st.rerun()
    elif not emp_id:
        st.session_state["login_error"] = "กรุณากรอกรหัสพนักงาน"
        st.rerun()
    elif emp_id in employees:
        st.session_state["authenticated"]  = True
        st.session_state["employee_id"]    = emp_id
        st.session_state["employee_name"]  = employees[emp_id]
        st.session_state["login_error"]    = ""
        st.rerun()
    else:
        st.session_state["login_error"] = "รหัสพนักงานไม่ถูกต้อง กรุณาลองใหม่"
        st.rerun()
