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
            background: #0f62fe;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
            padding: 6px 20px;
            border-radius: 0px;
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

    # IBM Carbon status: success=#24a148, warning=#b28600, neutral=#8d8d8d
    steps = [
        ("✅", "ปิดปีบัญชี 2568",                   "เสร็จสิ้น",     "#24a148", "#defbe6"),
        ("✅", "สรุปผลการดำเนินงานปี 2568",           "เสร็จสิ้น",     "#24a148", "#defbe6"),
        ("⏳", "ประกาศ KPI ปีบัญชี 2569",            "กำลังรอ",       "#b28600", "#fcf4d6"),
        ("⬜", "บันทึกข้อตกลงผลการดำเนินงาน (MOU)",   "ยังไม่ดำเนินการ","#8d8d8d", "#f4f4f4"),
        ("⬜", "เปิด Dashboard ปีบัญชี 2569",         "ยังไม่ดำเนินการ","#8d8d8d", "#f4f4f4"),
    ]

    for icon, label, status, color, bg in steps:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 14px 16px;
            margin-bottom: 2px;
            background: #f4f4f4;
            border-radius: 0px;
            border-left: 4px solid {color};
            border-bottom: 1px solid #e0e0e0;
        ">
            <span style="font-size: 20px; min-width:28px;">{icon}</span>
            <div style="flex: 1;">
                <div style="font-size:14px; font-weight:600; color:#161616;
                            letter-spacing:0.16px;">{label}</div>
            </div>
            <span style="
                font-size: 11px;
                color: {color};
                font-weight: 600;
                background: {bg};
                padding: 4px 12px;
                border-radius: 24px;
                letter-spacing: 0.16px;
                white-space: nowrap;
            ">{status}</span>
        </div>
        """, unsafe_allow_html=True)
