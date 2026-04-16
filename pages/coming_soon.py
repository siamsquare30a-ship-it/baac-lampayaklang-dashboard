# pages/coming_soon.py — หน้า Coming Soon สำหรับปีบัญชีที่ยังไม่ประกาศ KPI

import streamlit as st


def render(year: str = "2569") -> None:
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 52vh;
        text-align: center;
        padding: 48px 40px 32px;
    ">
        <div style="font-size: 72px; margin-bottom: 24px; line-height:1;">⏳</div>
        <div style="
            font-size: 11px;
            font-weight: 600;
            color: #525252;
            letter-spacing: 0.32px;
            text-transform: uppercase;
            margin-bottom: 8px;
        ">ปีบัญชี {year}</div>
        <div style="
            font-size: 42px;
            font-weight: 300;
            color: #161616;
            margin-bottom: 16px;
            line-height: 1.19;
        ">กำลังรอประกาศ KPI</div>
        <div style="
            display: inline-block;
            background: #00693e;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
            padding: 6px 20px;
            border-radius: 6px;
            margin-bottom: 24px;
            letter-spacing: 2px;
            text-transform: uppercase;
        ">COMING SOON</div>
        <div style="
            font-size: 16px;
            color: #525252;
            max-width: 480px;
            line-height: 1.6;
        ">
            อยู่ระหว่างรอประกาศ KPI และบันทึกข้อตกลงผลการดำเนินงาน<br>
            ประจำปีบัญชี พ.ศ. {year}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress tracker
    st.divider()
    st.markdown(
        '<div style="font-size:14px;font-weight:600;color:#161616;'
        'letter-spacing:0.16px;margin-bottom:12px;">📋 สถานะขั้นตอน</div>',
        unsafe_allow_html=True,
    )

    steps = [
        ("✅", "ปิดปีบัญชี 2568",                   "เสร็จสิ้น",     "#00693e", "#ecfdf5"),
        ("✅", "สรุปผลการดำเนินงานปี 2568",           "เสร็จสิ้น",     "#00693e", "#ecfdf5"),
        ("⏳", "ประกาศ KPI ปีบัญชี 2569",            "กำลังรอ",       "#d97706", "#fffbeb"),
        ("⬜", "บันทึกข้อตกลงผลการดำเนินงาน (MOU)",   "ยังไม่ดำเนินการ","#6b7280", "#f9fafb"),
        ("⬜", "เปิด Dashboard ปีบัญชี 2569",         "ยังไม่ดำเนินการ","#6b7280", "#f9fafb"),
    ]

    for icon, label, status, color, bg in steps:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 14px 16px;
            margin-bottom: 4px;
            background: #ffffff;
            border-radius: 8px;
            border-left: 4px solid {color};
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        ">
            <span style="font-size: 20px; min-width:28px;">{icon}</span>
            <div style="flex: 1;">
                <div style="font-size:14px; font-weight:600; color:#111827;
                            letter-spacing:0.16px;">{label}</div>
            </div>
            <span style="
                font-size: 11px;
                color: {color};
                font-weight: 600;
                background: {bg};
                padding: 3px 12px;
                border-radius: 20px;
                letter-spacing: 0.16px;
                white-space: nowrap;
            ">{status}</span>
        </div>
        """, unsafe_allow_html=True)
