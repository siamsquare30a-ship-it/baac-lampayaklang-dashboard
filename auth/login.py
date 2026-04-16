# auth/login.py — หน้า Login ด้วยรหัสพนักงาน

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
    # ── ซ่อน sidebar + header ──
    st.markdown("""
    <style>
    section[data-testid="stSidebar"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"]          { display: none !important; }
    .block-container                   { padding: 0 !important; max-width: 100% !important; }
    html, body, [class*="css"]         { background: #f4f4f4 !important; }

    /* ── top bar สีดำ ── */
    .login-topbar {
        background: #161616;
        padding: 14px 32px;
        display: flex;
        align-items: center;
        gap: 14px;
        width: 100%;
    }
    .login-topbar .org      { font-size:14px; font-weight:600; color:#f4f4f4; letter-spacing:.16px; }
    .login-topbar .sub      { font-size:11px; color:#8d8d8d; letter-spacing:.32px; text-transform:uppercase; }

    /* ── card กลางหน้า ── */
    .login-wrap {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding: 64px 16px 40px;
        background: #f4f4f4;
        min-height: 90vh;
    }
    .login-card {
        background: #ffffff;
        width: 420px;
        max-width: 100%;
        border-top: 4px solid #0f62fe;
        padding: 40px 40px 0px;
    }
    .login-card .label   { font-size:11px; color:#525252; letter-spacing:.32px;
                           text-transform:uppercase; margin-bottom:4px; }
    .login-card .title   { font-size:30px; font-weight:300; color:#161616;
                           line-height:1.2; margin-bottom:4px; }
    .login-card .sub     { font-size:13px; color:#525252; margin-bottom:28px; }
    .login-card .divider { height:1px; background:#e0e0e0; margin-bottom:24px; }
    .login-card .field-label {
        font-size:12px; font-weight:600; color:#161616;
        letter-spacing:.32px; text-transform:uppercase; margin-bottom:6px;
    }
    .login-footer {
        text-align:center; margin-top:16px; padding-bottom:8px;
        font-size:11px; color:#8d8d8d; letter-spacing:.32px;
    }

    /* Input field style */
    .stTextInput > div > div > input {
        background: #f4f4f4 !important;
        border: none !important;
        border-bottom: 2px solid #161616 !important;
        border-radius: 0 !important;
        font-size: 16px !important;
        padding: 10px 16px !important;
        color: #161616 !important;
        letter-spacing: .5px !important;
    }
    .stTextInput > div > div > input:focus {
        border-bottom: 2px solid #0f62fe !important;
        outline: none !important;
        box-shadow: none !important;
    }
    .stTextInput label { display: none !important; }

    /* Button */
    .stButton > button {
        border-radius: 0 !important;
        background: #0f62fe !important;
        color: #fff !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        height: 48px !important;
        border: none !important;
        letter-spacing: .32px !important;
        width: 100% !important;
        margin-top: 8px !important;
    }
    .stButton > button:hover  { background: #0353e9 !important; }
    .stButton > button:active { background: #002d9c !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Top bar ──
    st.markdown("""
    <div class="login-topbar">
      <div style="font-size:26px;line-height:1;">🏦</div>
      <div>
        <div class="org">ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร</div>
        <div class="sub">หน่วยลำพญากลาง · สาขาลำพญากลาง</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Card wrapper (HTML เฉพาะ frame) ──
    st.markdown("""
    <div class="login-wrap">
      <div class="login-card">
        <div class="label">Dashboard</div>
        <div class="title">ผลการดำเนินงาน</div>
        <div class="sub">ปีบัญชี 2568</div>
        <div class="divider"></div>
        <div class="field-label">รหัสพนักงาน</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Streamlit input + button วางในคอลัมน์กลาง ──
    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        emp_id = st.text_input(
            "รหัสพนักงาน",
            placeholder="เช่น 6000261",
            max_chars=10,
            key="login_input",
        )
        login_btn = st.button("เข้าสู่ระบบ →", key="login_btn", use_container_width=True)

        if login_btn:
            _do_login(emp_id.strip())

        err = st.session_state.get("login_error", "")
        if err:
            st.markdown(f"""
            <div style="background:#fff1f1;border-left:4px solid #da1e28;
                        padding:12px 16px;margin-top:4px;
                        font-size:13px;color:#da1e28;letter-spacing:.16px;">
              🔴 {err}
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            '<div class="login-footer">ใช้รหัสพนักงาน ธ.ก.ส. ของท่านในการเข้าสู่ระบบ</div>',
            unsafe_allow_html=True,
        )


def _do_login(emp_id: str) -> None:
    employees = _get_employee_map()
    if not emp_id:
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
