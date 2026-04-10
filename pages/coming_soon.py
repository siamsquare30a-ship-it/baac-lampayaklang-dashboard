# pages/coming_soon.py — หน้า Coming Soon สำหรับปีบัญชีที่ยังไม่ประกาศ KPI

import streamlit as st


def render(year: str = "2569") -> None:
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
        padding: 40px;
    ">
        <div style="font-size: 80px; margin-bottom: 16px;">⏳</div>
        <div style="
            font-size: 36px;
            font-weight: 800;
            color: #333;
            margin-bottom: 8px;
        ">ปีบัญชี {year}</div>
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #007bff, #6610f2);
            color: white;
            font-size: 18px;
            font-weight: 700;
            padding: 8px 28px;
            border-radius: 50px;
            margin-bottom: 24px;
            letter-spacing: 2px;
        ">COMING SOON</div>
        <div style="
            font-size: 16px;
            color: #666;
            max-width: 480px;
            line-height: 1.8;
        ">
            อยู่ระหว่างรอประกาศ KPI และบันทึกข้อตกลงผลการดำเนินงาน<br>
            ประจำปีบัญชี พ.ศ. {year}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress tracker
    st.divider()
    st.markdown("#### 📋 สถานะขั้นตอน")

    steps = [
        ("✅", "ปิดปีบัญชี 2568",                   "เสร็จสิ้น",     "#28a745"),
        ("✅", "สรุปผลการดำเนินงานปี 2568",           "เสร็จสิ้น",     "#28a745"),
        ("⏳", "ประกาศ KPI ปีบัญชี 2569",            "กำลังรอ",       "#ffc107"),
        ("⬜", "บันทึกข้อตกลงผลการดำเนินงาน (MOU)",   "ยังไม่ดำเนินการ","#adb5bd"),
        ("⬜", "เปิด Dashboard ปีบัญชี 2569",         "ยังไม่ดำเนินการ","#adb5bd"),
    ]

    for icon, label, status, color in steps:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 12px 16px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid {color};
        ">
            <span style="font-size: 22px;">{icon}</span>
            <div style="flex: 1;">
                <div style="font-size:15px; font-weight:600; color:#333;">{label}</div>
            </div>
            <div style="
                font-size: 12px;
                color: {color};
                font-weight: 700;
                background: white;
                padding: 4px 12px;
                border-radius: 20px;
                border: 1px solid {color};
            ">{status}</div>
        </div>
        """, unsafe_allow_html=True)
