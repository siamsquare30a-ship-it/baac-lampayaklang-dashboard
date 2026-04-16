# auth/login.py — หน้า Login ด้วยรหัสพนักงาน (IBM Carbon style)

import streamlit as st


def _get_employee_map() -> dict:
    """โหลดรหัสพนักงานจาก st.secrets"""
    try:
        return dict(st.secrets["employees"])
    except Exception:
        return {}


def check_login() -> bool:
    """True = ผ่านการ login แล้ว"""
    return st.session_state.get("authenticated", False)


def logout() -> None:
    st.session_state["authenticated"] = False
    st.session_state["employee_name"] = ""
    st.session_state["employee_id"] = ""
    st.rerun()


def render_login_page() -> None:
    """แสดงหน้า Login — IBM Carbon Design"""

    # ซ่อน sidebar ระหว่าง login
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Layout: top bar + centered card ──
    st.markdown("""
    <div style="
        background: #161616;
        padding: 16px 32px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 0;
    ">
        <div style="font-size:28px;">🏦</div>
        <div>
            <div style="font-size:14px;font-weight:600;color:#f4f4f4;
                        letter-spacing:0.16px;">ธนาคารเพื่อการเกษตรและสหกรณ์การเกษตร</div>
            <div style="font-size:11px;color:#8d8d8d;letter-spacing:0.32px;
                        text-transform:uppercase;">หน่วยลำพญากลาง · สาขาลำพญากลาง</div>
        </div>
    </div>

    <div style="
        min-height: calc(100vh - 64px);
        background: #f4f4f4;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px 16px;
    ">
    <div style="
        background: #ffffff;
        width: 100%;
        max-width: 400px;
        padding: 40px 40px 48px;
        border-top: 4px solid #0f62fe;
    ">
        <div style="font-size:11px;color:#525252;letter-spacing:0.32px;
                    text-transform:uppercase;margin-bottom:8px;">Dashboard</div>
        <div style="font-size:28px;font-weight:300;color:#161616;
                    line-height:1.19;margin-bottom:4px;">ผลการดำเนินงาน</div>
        <div style="font-size:14px;color:#525252;margin-bottom:32px;
                    letter-spacing:0.16px;">ปีบัญชี 2568</div>
        <div style="height:1px;background:#e0e0e0;margin-bottom:32px;"></div>
        <div style="font-size:12px;font-weight:600;color:#161616;
                    letter-spacing:0.32px;margin-bottom:4px;text-transform:uppercase;">
            รหัสพนักงาน
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Input + Button วางใน invisible container ตรงกลาง
    # ใช้ columns เพื่อจัดให้อยู่กึ่งกลาง
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        emp_id = st.text_input(
            label="รหัสพนักงาน",
            label_visibility="collapsed",
            placeholder="กรอกรหัสพนักงาน 7 หลัก",
            max_chars=10,
            key="login_emp_id_input",
        )
        login_clicked = st.button(
            "เข้าสู่ระบบ →",
            use_container_width=True,
            key="login_btn",
        )

        if login_clicked or (emp_id and st.session_state.get("_enter_pressed")):
            _do_login(emp_id.strip())

        # Error message (ถ้ามี)
        if st.session_state.get("login_error"):
            st.markdown(f"""
            <div style="
                background:#fff1f1;border-left:4px solid #da1e28;
                padding:12px 16px;margin-top:8px;
                font-size:13px;color:#da1e28;letter-spacing:0.16px;
            ">
                🔴 {st.session_state['login_error']}
            </div>
            """, unsafe_allow_html=True)

    # Footer note
    st.markdown("""
    <div style="text-align:center;margin-top:24px;">
        <div style="font-size:11px;color:#8d8d8d;letter-spacing:0.32px;">
            ใช้รหัสพนักงาน ธ.ก.ส. ของท่านในการเข้าสู่ระบบ
        </div>
    </div>
    """, unsafe_allow_html=True)


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
