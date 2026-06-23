import streamlit as st


def render_sidebar(students_df, center_list, user=None):
    st.sidebar.markdown(
        '<div style="font-size:23px;font-weight:700;color:#1A3C5E;text-align:center;'
        'padding:8px 0 4px;">KYC DASHBOARD</div>', unsafe_allow_html=True)

    pages = ["▸ Tổng quan", "▹ Theo Center"]
    role = (user or {}).get("role", "")
    if role == "admin":
        pages.append("⚙ Quản lý Users")

    page = st.sidebar.radio("Chọn trang", pages)
    selected_center = None

    if page == "▹ Theo Center":
        selected_center = st.sidebar.selectbox("Chọn Center", center_list, index=0)
        center_df = students_df[students_df["Primary Center"] == selected_center]
        total_hv = center_df["Student ID"].nunique()
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            f"""<div style="background:#e8f0fe;border-radius:8px;padding:12px;font-size:13px;">
                <b>{selected_center}</b><br>Học viên: <b>{total_hv}</b>
            </div>""", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div style="font-size:12px;color:#888;margin-bottom:8px;"><b>Bộ lọc chung</b></div>',
        unsafe_allow_html=True)

    all_courses = ["Tất cả"] + sorted([str(c) for c in students_df["Course Simplified"].dropna().unique().tolist()])
    all_sources = ["Tất cả"] + sorted([str(s) for s in students_df["Source Simplified"].dropna().unique().tolist()])
    all_genders = ["Tất cả", "Male", "Female"]
    all_ages = ["Tất cả", "3-5", "6-8", "9-12", "13-15", "16+"]

    course = st.sidebar.selectbox("Khoá học", all_courses)
    source = st.sidebar.selectbox("Nguồn", all_sources)
    gender = st.sidebar.selectbox("Giới tính", all_genders)
    age = st.sidebar.selectbox("Nhóm tuổi", all_ages)

    return page, selected_center, course, source, gender, age
