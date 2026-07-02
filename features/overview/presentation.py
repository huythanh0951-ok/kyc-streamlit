import streamlit as st
import plotly.express as px
import pandas as pd
from core.constants import COLOR_PRIMARY, COLORS_CATEGORY
from core.utils import metric_card, styled_header, section_header, fmt_num
from features.charts.pie_chart import create_learning_history_pie, create_pie_chart, create_coverage_pie
from features.charts.bar_chart import create_horizontal_bar, create_top_n_bar, create_parent_job_bar
from data_layer.repository import get_last_update_time


def render_overview(students, multi):
    last_update = get_last_update_time()
    styled_header("KYC DASHBOARD — TOÀN HỆ THỐNG", f"Cập nhật: {last_update}")
    total_students = len(students)
    avg_age = students["Age"].dropna().mean()
    study_abroad = students[students["Có Du Học"] == "Có"]["Student ID"].nunique()

    # ── Row 1: Scorecards ──
    cols = st.columns(4)
    metric_card(cols[0], "TỔNG HV", fmt_num(total_students))
    with cols[1]:
        male = students[students["Gender"] == "Male"]["Student ID"].nunique()
        female = students[students["Gender"] == "Female"]["Student ID"].nunique()
        total_gender = max(male + female, 1)
        st.markdown(
            f"""<div style="background:white;border-radius:8px;padding:16px 12px;text-align:center;box-shadow:0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12);height:148px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;font-family:Montserrat,sans-serif;">
                <div style="font-size:13px;color:#888;text-transform:uppercase;letter-spacing:0.5px;">GIỚI TÍNH</div>
                <div style="font-size:16px;font-weight:600;color:{COLOR_PRIMARY};margin-top:6px;">Nam: {fmt_num(male)} ({male/total_gender*100:.0f}%)</div>
                <div style="font-size:16px;font-weight:600;color:#8b672a;margin-top:2px;">Nữ: {fmt_num(female)} ({female/total_gender*100:.0f}%)</div>
            </div>""", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(
            f"""<div style="background:white;border-radius:8px;padding:16px 12px;text-align:center;box-shadow:0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12);height:148px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;font-family:Montserrat,sans-serif;">
                <div style="font-size:13px;color:#888;text-transform:uppercase;">TUỔI TB</div>
                <div style="font-size:29px;font-weight:700;color:{COLOR_PRIMARY};margin-top:4px;">{f"{avg_age:.1f}" if pd.notna(avg_age) else "-"}</div>
            </div>""", unsafe_allow_html=True)
    metric_card(cols[3], "CÓ Ý ĐỊNH DU HỌC", f"{fmt_num(study_abroad)} ({study_abroad/max(total_students,1)*100:.1f}%)")
    st.markdown("---")

    # ── Row 2: Center + Course + Source ──
    col1, col2, col3 = st.columns(3)
    with col1:
        section_header("Học viên theo Center")
        st.plotly_chart(create_horizontal_bar(students, "Primary Center", "Student ID", COLOR_PRIMARY, height=300), config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Khóa học")
        st.plotly_chart(create_pie_chart(students, "Course Simplified", "Student ID", "Khóa học", COLORS_CATEGORY, height=300), config={"scrollZoom": False}, use_container_width=True)
    with col3:
        section_header("Nguồn tuyển sinh")
        st.plotly_chart(create_pie_chart(students, "Source Simplified", "Student ID", "Nguồn", COLORS_CATEGORY, height=300), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 3: Age + Goal + Problem ──
    col1, col2, col3 = st.columns(3)
    with col1:
        section_header("Nhóm tuổi")
        age_order = ["3-5", "6-8", "9-12", "13-15", "16+"]
        age_counts = students.groupby("Age Group")["Student ID"].nunique().reindex(age_order, fill_value=0).reset_index()
        age_counts.columns = ["Nhóm tuổi", "Học viên"]
        fig = px.bar(age_counts, x="Nhóm tuổi", y="Học viên", text_auto=True, color_discrete_sequence=[COLOR_PRIMARY])
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=250, xaxis_title="", yaxis_title="", showlegend=False, paper_bgcolor="white", plot_bgcolor="white", dragmode=False)
        fig.update_yaxes(gridcolor="#f0f0f0")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Mục tiêu (Goal)")
        st.plotly_chart(create_horizontal_bar(multi[multi["Dimension"] == "Goal"], "Value", "Student ID", "#34a853"), config={"scrollZoom": False}, use_container_width=True)
    with col3:
        section_header("Vấn đề (Problem)")
        st.plotly_chart(create_horizontal_bar(multi[multi["Dimension"] == "Problem"], "Value", "Student ID", "#be202f"), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 4: Interest + Destination ──
    col1, col2 = st.columns(2)
    with col1:
        section_header("Quan tâm (Interest)")
        st.plotly_chart(create_horizontal_bar(multi[multi["Dimension"] == "Interest"], "Value", "Student ID", "#ff6d01"), config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Điểm đến du học")
        st.plotly_chart(create_pie_chart(multi[multi["Dimension"] == "Target Destination"], "Value", "Student ID", "Điểm đến", COLORS_CATEGORY, height=250), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 5: Nghề nghiệp PH (bar + pie) ──
    col1, col2 = st.columns([2, 1])
    with col1:
        section_header("Top Nghề nghiệp PH")
        st.plotly_chart(create_parent_job_bar(students, COLOR_PRIMARY, height=300), config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Nghề nghiệp PH")
        st.plotly_chart(create_coverage_pie(students, "parent_job", [COLOR_PRIMARY, "#b5914c"], height=300), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 6: Trường học (bar + pie) ──
    col1, col2 = st.columns([2, 1])
    with col1:
        section_header("Top Trường đang theo học")
        st.plotly_chart(create_top_n_bar(students, "School Name", COLOR_PRIMARY, height=300), config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Trường học")
        st.plotly_chart(create_coverage_pie(students, "school", [COLOR_PRIMARY, "#b5914c"], height=300), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 7: Learning History ──
    section_header("Lịch sử học tập")
    st.plotly_chart(create_learning_history_pie(students, COLORS_CATEGORY), config={"scrollZoom": False}, use_container_width=True)

    st.markdown("---")
