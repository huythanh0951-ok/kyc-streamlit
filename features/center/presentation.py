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

    # ── Action Points ──
    _render_action_points(center_name)

    st.markdown("---")

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


def _render_action_points(center_name: str):
    """Hiển thị & edit action points cho center"""
    from data_layer.repository import load_action_points, save_action_points

    role = (st.session_state.get("user") or {}).get("role", "")
    can_edit = role in ("admin", "bod")
    edit_state_key = f"ap_editing_{center_name}"
    btn_key = f"ap_btn_{center_name}"

    if edit_state_key not in st.session_state:
        st.session_state[edit_state_key] = False

    text = load_action_points(center_name)

    if can_edit:
        if st.session_state[edit_state_key]:
            new_text = _rich_text_editor(f"ap_text_{center_name}", text)
            c1, c2 = st.columns([1, 4])
            if c1.button("Lưu", key=f"ap_save_{center_name}", type="primary"):
                if save_action_points(center_name, new_text or text):
                    st.success("Đã lưu!")
                    st.session_state[edit_state_key] = False
                    st.rerun()
                else:
                    st.error("Lưu thất bại.")
            if c2.button("Hủy", key=f"ap_cancel_{center_name}"):
                st.session_state[edit_state_key] = False
                st.rerun()
        else:
            if text.strip():
                st.markdown(
                    f"""<div style="background:linear-gradient(135deg, #FFF8E1, #FFF3CD);border-radius:12px;
                    padding:16px 20px;border-left:6px solid #ff6d01;box-shadow:0 2px 6px rgba(255,109,1,0.12);
                    font-size:14px;color:#333;line-height:1.8;white-space:pre-wrap;">{text}</div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("Chưa có action points.")
            if st.button("Chỉnh sửa Action Points", key=btn_key):
                st.session_state[edit_state_key] = True
                st.rerun()
    else:
        if text.strip():
            st.markdown(
                f"""<div style="background:linear-gradient(135deg, #FFF8E1, #FFF3CD);border-radius:12px;
                padding:16px 20px;border-left:6px solid #ff6d01;box-shadow:0 2px 6px rgba(255,109,1,0.12);
                font-size:14px;color:#333;line-height:1.8;">{text}</div>""",
                unsafe_allow_html=True,
            )


def _rich_text_editor(key: str, initial_html: str):
    """Rich text editor using Quill.js. Trả về HTML khi người dùng thay đổi."""
    escaped = initial_html.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    html_code = f"""
    <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
    <script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
    <script>
    window.onerror = function(msg) {{ console.error('Quill error:', msg); }};
    </script>
    <div id="editor_{key}" style="height:220px;"></div>
    <script>
    function sendValue() {{
        var html = quill.root.innerHTML;
        window.parent.postMessage(
            {{isStreamlitMessage: true, type: 'streamlit:setComponentValue', value: html, dataType: 'json'}},
            '*'
        );
    }}
    var quill = new Quill('#editor_{key}', {{
        theme: 'snow',
        modules: {{
            toolbar: [
                ['bold', 'italic', 'underline'],
                [{{ 'color': [] }}, {{ 'background': [] }}],
                [{{ 'list': 'bullet' }}],
                ['clean']
            ]
        }}
    }});
    quill.root.innerHTML = `{escaped}`;
    quill.on('text-change', sendValue);
    // Initial send
    sendValue();
    </script>
    """
    return st.components.v1.html(html_code, height=300)
