# components/charts.py — Chart factory functions (Plotly)

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import COLOR_MAP, CATEGORIES


# =========================================================
# Gauge — ภาพรวมบรรลุเป้า
# =========================================================
def gauge_chart(rate: float, title: str = "ภาพรวมบรรลุเป้า") -> go.Figure:
    color = ("#28a745" if rate >= 100
             else "#ffc107" if rate >= 80
             else "#dc3545")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rate,
        title={"text": title, "font": {"size": 16}},
        number={"suffix": "%", "font": {"size": 28}},
        delta={"reference": 100, "valueformat": ".1f"},
        gauge={
            "axis": {"range": [0, 120], "ticksuffix": "%"},
            "bar":  {"color": color},
            "steps": [
                {"range": [0,   80],  "color": "#f8d7da"},
                {"range": [80,  100], "color": "#fff3cd"},
                {"range": [100, 120], "color": "#d4edda"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.75,
                "value": 100,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(t=60, b=10, l=20, r=20))
    return fig


# =========================================================
# Bar chart — เปรียบเทียบ achievement ตาม category
# =========================================================
def category_bar(summary_df: pd.DataFrame) -> go.Figure:
    """summary_df มีคอลัมน์: category, achievement_rate, status"""
    colors = summary_df["status"].map(COLOR_MAP).tolist()
    fig = go.Figure(go.Bar(
        x=summary_df["category"],
        y=summary_df["achievement_rate"],
        marker_color=colors,
        text=[f"{r:.1f}%" for r in summary_df["achievement_rate"]],
        textposition="outside",
    ))
    fig.add_hline(y=100, line_dash="dash", line_color="black",
                  annotation_text="เป้าหมาย 100%")
    fig.update_layout(
        title="อัตราบรรลุเป้าตามหมวด",
        yaxis_title="อัตราบรรลุเป้า (%)",
        yaxis_range=[0, 130],
        height=350,
        margin=dict(t=50, b=40),
        font=dict(family="Sarabun, sans-serif"),
    )
    return fig


# =========================================================
# Line chart — Trend รายเดือน
# =========================================================
def trend_line(trend_df: pd.DataFrame, selected_category: str = "ทั้งหมด") -> go.Figure:
    """trend_df มีคอลัมน์: month, category, actual"""
    if selected_category != "ทั้งหมด":
        df = trend_df[trend_df["category"] == selected_category]
        month_actual = df.groupby("month")["actual"].sum().reset_index()
        fig = go.Figure(go.Scatter(
            x=month_actual["month"],
            y=month_actual["actual"],
            mode="lines+markers+text",
            text=[f"{v:,.1f}" for v in month_actual["actual"]],
            textposition="top center",
            line=dict(color="#007bff", width=2),
            name=selected_category,
        ))
    else:
        fig = go.Figure()
        palette = px.colors.qualitative.Set2
        for i, cat in enumerate(trend_df["category"].unique()):
            sub = trend_df[trend_df["category"] == cat]
            ma  = sub.groupby("month")["actual"].sum().reset_index()
            fig.add_trace(go.Scatter(
                x=ma["month"], y=ma["actual"],
                mode="lines+markers",
                name=cat,
                line=dict(color=palette[i % len(palette)], width=2),
            ))

    fig.update_layout(
        title="แนวโน้มผลการดำเนินงานรายเดือน",
        yaxis_title="ผลจริง (ล้านบาท)",
        height=350,
        margin=dict(t=50, b=40),
        font=dict(family="Sarabun, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


# =========================================================
# Radar chart — Zone multi-category
# =========================================================
def radar_chart(zone_df: pd.DataFrame, zone_id: str) -> go.Figure:
    """zone_df มีคอลัมน์: zone_id, category, achievement_rate"""
    sub = zone_df[zone_df["zone_id"] == zone_id]
    cats   = sub["category"].tolist()
    values = sub["achievement_rate"].tolist()
    # ปิด polygon
    cats   += [cats[0]]
    values += [values[0]]
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=cats,
        fill="toself",
        fillcolor="rgba(0,123,255,0.15)",
        line=dict(color="#007bff"),
        name=zone_id,
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 130])),
        title=f"โปรไฟล์ {zone_id}",
        height=350,
        margin=dict(t=60, b=20),
        font=dict(family="Sarabun, sans-serif"),
    )
    return fig


# =========================================================
# Horizontal bar — Zone ranking
# =========================================================
def zone_ranking_bar(zone_overall_df: pd.DataFrame) -> go.Figure:
    df = zone_overall_df.sort_values("overall_rate")
    colors = [
        "#28a745" if r >= 100 else "#ffc107" if r >= 80 else "#dc3545"
        for r in df["overall_rate"]
    ]
    fig = go.Figure(go.Bar(
        y=df["zone_id"],
        x=df["overall_rate"],
        orientation="h",
        marker_color=colors,
        text=[f"{r:.1f}%" for r in df["overall_rate"]],
        textposition="outside",
    ))
    fig.add_vline(x=100, line_dash="dash", line_color="black")
    fig.update_layout(
        title="การจัดอันดับเขตสินเชื่อ",
        xaxis_title="อัตราบรรลุเป้าเฉลี่ย (%)",
        xaxis_range=[0, 130],
        height=max(250, len(df) * 55),
        margin=dict(t=50, b=40, l=10),
        font=dict(family="Sarabun, sans-serif"),
    )
    return fig
