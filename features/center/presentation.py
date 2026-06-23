import streamlit as st
import plotly.express as px
import pandas as pd
from core.constants import COLOR_PRIMARY, COLORS_CATEGORY
from core.utils import metric_card, styled_header, section_header, fmt_num
from features.charts.pie_chart import create_learning_history_pie, create_pie_chart, create_coverage_pie
from features.charts.bar_chart import create_horizontal_bar, create_top_n_bar, create_parent_job_bar


def render_center(students_all, multi_all, center_name):
    students = students_all[students_all["Primary Center"] == center_name].copy()
    valid_ids = students["Student ID"].unique()
    multi = multi_all[multi_all["Student ID"].isin(valid_ids)]

    if len(students) == 0:
        st.warning(f"Không có dữ liệu cho center {center_name} với bộ lọc hiện tại.")
        return

    total_students = len(students)
    avg_age = students["Age"].dropna().mean()
    study_abroad = students[students["Có Du Học"] == "Có"]["Student ID"].nunique()
    styled_header(f"CENTER: {center_name.upper()}", f"{fmt_num(total_students)} học viên | Cập nhật: 08/06/2026")

    # ── Row 1: Scorecards ──
    cols = st.columns(4)
    metric_card(cols[0], "TỔNG HV", fmt_num(total_students))
    with cols[1]:
        male = students[students["Gender"] == "Male"]["Student ID"].nunique()
        female = students[students["Gender"] == "Female"]["Student ID"].nunique()
        total_gender = max(male + female, 1)
        st.markdown(
            f"""<div style="background:white;border-radius:10px;padding:16px 12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.06);height:148px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;">
                <div style="font-size:13px;color:#888;text-transform:uppercase;letter-spacing:0.5px;">GIỚI TÍNH</div>
                <div style="font-size:16px;font-weight:600;color:{COLOR_PRIMARY};margin-top:6px;">Nam: {fmt_num(male)} ({male/total_gender*100:.0f}%)</div>
                <div style="font-size:16px;font-weight:600;color:#ea4335;margin-top:2px;">Nữ: {fmt_num(female)} ({female/total_gender*100:.0f}%)</div>
            </div>""", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(
            f"""<div style="background:white;border-radius:10px;padding:16px 12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.06);height:148px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;">
                <div style="font-size:13px;color:#888;text-transform:uppercase;">TUỔI TB</div>
                <div style="font-size:29px;font-weight:700;color:{COLOR_PRIMARY};margin-top:4px;">{f"{avg_age:.1f}" if pd.notna(avg_age) else "-"}</div>
            </div>""", unsafe_allow_html=True)
    metric_card(cols[3], "CÓ Ý ĐỊNH DU HỌC", f"{fmt_num(study_abroad)} ({study_abroad/max(total_students,1)*100:.1f}%)")
    st.markdown("---")

    # ── Action Points (AI-driven) ──
    _render_action_points(students, multi, center_name)

    # ── Row 2: Source + Course + Age ──
    col1, col2, col3 = st.columns(3)
    with col1:
        section_header("Nguồn tuyển sinh")
        st.plotly_chart(create_pie_chart(students, "Source Simplified", "Student ID", "Nguồn", COLORS_CATEGORY, height=250), config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Khóa học")
        st.plotly_chart(create_horizontal_bar(students, "Course Simplified", "Student ID", COLOR_PRIMARY, height=250), config={"scrollZoom": False}, use_container_width=True)
    with col3:
        section_header("Nhóm tuổi")
        age_order = ["3-5", "6-8", "9-12", "13-15", "16+"]
        age_counts = students.groupby("Age Group")["Student ID"].nunique().reindex(age_order, fill_value=0).reset_index()
        age_counts.columns = ["Nhóm tuổi", "Học viên"]
        fig = px.bar(age_counts, x="Nhóm tuổi", y="Học viên", text_auto=True, color_discrete_sequence=COLORS_CATEGORY)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=250, xaxis_title="", yaxis_title="", showlegend=False, paper_bgcolor="white", plot_bgcolor="white", dragmode=False)
        fig.update_yaxes(gridcolor="#f0f0f0")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, config={"scrollZoom": False}, use_container_width=True)

    # ── Row 3: Problem + Goal (Top 5) ──
    col1, col2 = st.columns(2)
    with col1:
        section_header("Vấn đề (Top 5)")
        st.plotly_chart(create_horizontal_bar(multi[multi["Dimension"] == "Problem"], "Value", "Student ID", "#ea4335", top_n=5), config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Mục tiêu (Top 5)")
        st.plotly_chart(create_horizontal_bar(multi[multi["Dimension"] == "Goal"], "Value", "Student ID", "#34a853", top_n=5), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 4: Interest + Destination ──
    col1, col2 = st.columns(2)
    with col1:
        section_header("Quan tâm (Top 5)")
        st.plotly_chart(create_horizontal_bar(multi[multi["Dimension"] == "Interest"], "Value", "Student ID", "#ff6d01", top_n=5), config={"scrollZoom": False}, use_container_width=True)
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
        st.plotly_chart(create_coverage_pie(students, "parent_job", [COLOR_PRIMARY, "#e0e0e0"], height=300), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 6: Trường học (bar + pie) ──
    col1, col2 = st.columns([2, 1])
    with col1:
        section_header("Top Trường đang theo học")
        st.plotly_chart(create_top_n_bar(students, "School Name", COLOR_PRIMARY, height=300), config={"scrollZoom": False}, use_container_width=True)
    with col2:
        section_header("Trường học")
        st.plotly_chart(create_coverage_pie(students, "school", [COLOR_PRIMARY, "#e0e0e0"], height=300), config={"scrollZoom": False}, use_container_width=True)

    # ── Row 7: Learning History ──
    section_header("Lịch sử học tập")
    st.plotly_chart(create_learning_history_pie(students, COLORS_CATEGORY), config={"scrollZoom": False}, use_container_width=True)

    st.markdown("---")


def _render_action_points(students, multi, center_name):
    """AI-driven action points dựa trên dữ liệu center"""
    points = _generate_action_points(students, multi)
    if not points:
        return

    section_header("Action Points")

    priorities = {"cao": "#ea4335", "trung bình": "#ff6d01", "thấp": "#34a853"}
    priority_icons = {"cao": "🔴", "trung bình": "🟠", "thấp": "🟢"}

    for i, p in enumerate(points):
        color = priorities.get(p.get("priority", "trung bình"), COLOR_PRIMARY)
        icon = priority_icons.get(p.get("priority", "trung bình"), "⚪")
        with st.container():
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:14px 18px;margin-bottom:10px;
                        border-left:5px solid {color};box-shadow:0 1px 3px rgba(0,0,0,0.06);">
                <div style="display:flex;align-items:flex-start;gap:10px;">
                    <span style="font-size:18px;">{icon}</span>
                    <div style="flex:1;">
                        <div style="font-weight:600;font-size:14px;color:#1A3C5E;margin-bottom:4px;">{p['title']}</div>
                        <div style="font-size:13px;color:#666;line-height:1.5;">{p['detail']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def _generate_action_points(students, multi):
    """Sinh action points từ dữ liệu (demo: rules → sau này AI)"""
    points = []
    total = max(len(students), 1)

    # Source analysis
    fb = students[students["Source Simplified"] == "Facebook"]["Student ID"].nunique()
    if fb / total > 0.4:
        points.append({
            "title": "Đa dạng hóa nguồn tuyển sinh",
            "detail": f"{fb/total*100:.0f}% học viên đến từ Facebook. Cân nhắc đẩy mạnh Zalo ads, TikTok, Google Ads để giảm phụ thuộc.",
            "priority": "cao",
        })

    zalo = students[students["Source Simplified"] == "Zalo"]["Student ID"].nunique()
    if zalo / total < 0.15 and total > 20:
        points.append({
            "title": "Tiềm năng từ Zalo Ads",
            "detail": f"Zalo chỉ chiếm {zalo/total*100:.0f}% nguồn. Đây là kênh chi phí thấp, đối tượng phụ huynh phù hợp — nên test.",
            "priority": "trung bình",
        })

    # Parent job coverage
    ph1_has = students["Parent 1 Name"].notna() & students["Parent 1 Job"].notna()
    # Lọc noise jobs
    noise = {"tổng", "tong", "total", "khác", "khong", "-", "--", "", "0"}
    ph1_valid = ph1_has & ~students["Parent 1 Job"].astype(str).str.strip().str.lower().isin(noise)
    ph2_has = students["Parent 2 Name"].notna() & students["Parent 2 Job"].notna()
    ph2_valid = ph2_has & ~students["Parent 2 Job"].astype(str).str.strip().str.lower().isin(noise)
    ph_rows = ph1_valid | ph2_valid
    job_rate = ph_rows.sum() / total
    if job_rate < 0.5:
        points.append({
            "title": "Thu thập nghề nghiệp phụ huynh",
            "detail": f"Chỉ {job_rate*100:.0f}% học viên có thông tin nghề PH. Dữ liệu này quan trọng để phân khúc và tư vấn chính xác.",
            "priority": "cao",
        })

    # Study abroad interest
    abroad = students[students["Có Du Học"] == "Có"]["Student ID"].nunique()
    if abroad > 0:
        points.append({
            "title": "Tiềm năng tư vấn du học",
            "detail": f"{abroad} học viên có ý định du học ({abroad/total*100:.0f}%). Xây dựng gói tư vấn du học chuyên sâu cho nhóm này.",
            "priority": "trung bình",
        })

    # Age group analysis
    young = students[students["Age Group"].isin(["3-5", "6-8"])]["Student ID"].nunique()
    if young / total > 0.5:
        points.append({
            "title": "Tập trung khóa học thiếu nhi",
            "detail": f"{young/total*100:.0f}% học viên dưới 8 tuổi. Ưu tiên mở thêm lớp Kids, đầu tư giáo trình và GV thiếu nhi.",
            "priority": "cao",
        })

    # School coverage
    school_known = students["School Name"].notna() & (students["School Name"].str.strip().str.lower() != "trường .") & ~students["School Name"].astype(str).str.strip().str.lower().isin(["", "-", "--", "chưa có", "không có"])
    school_rate = school_known.sum() / total
    if school_rate < 0.5:
        points.append({
            "title": "Cập nhật thông tin trường học",
            "detail": f"Chỉ {school_rate*100:.0f}% có thông tin trường. Dữ liệu này giúp xác định phân khúc và đối thủ cạnh tranh.",
            "priority": "cao",
        })

    # Sort by priority
    order = {"cao": 0, "trung bình": 1, "thấp": 2}
    points.sort(key=lambda p: order.get(p["priority"], 3))

    return points[:6]
