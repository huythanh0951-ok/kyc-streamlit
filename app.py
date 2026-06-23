import streamlit as st
from data_layer.repository import load_data
from sidebar.presentation import render_sidebar
from features.overview.presentation import render_overview
from features.center.presentation import render_center
from features.auth.presentation import render_login, render_sidebar_header, render_admin_page
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="KYC Dashboard",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──
st.markdown("""
<style>
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
        gap: 9px !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        display: flex;
    }
    div[data-testid="stHorizontalBlock"] > div > div {
        flex: 1;
    }
    .stPlotlyChart {
        background: white;
        border-radius: 10px;
        padding: 9px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stElementContainer"] {
        overflow: visible !important;
    }
    div[data-testid="stFullScreenFrame"] {
        overflow: hidden !important;
    }
    .scrollbar {
        display: none !important;
    }
    /* Fix modebar bị che */
    .modebar-container {
        right: 15px !important;
        top: 2px !important;
    }
    .modebar {
        display: flex !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Auth Guard ──
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    render_login()
    st.stop()

# ── User info ──
user = st.session_state.get("user", {})
role = user.get("role", "admin")
centers = user.get("centers", ["*"])

# ── Data ──
students_df, multi_df = load_data()

# ── Filter by role ──
if role in ("center",) and "*" not in centers:
    students_df = students_df[students_df["Primary Center"].isin(centers)].copy()
    valid_ids = students_df["Student ID"].unique()
    multi_df = multi_df[multi_df["Student ID"].isin(valid_ids)]
# admin & bod → xem tất cả

# ── Sidebar ──
all_centers = sorted(students_df["Primary Center"].unique().tolist())
render_sidebar_header()
page, selected_center, course_filter, source_filter, gender_filter, age_filter = render_sidebar(students_df, all_centers, user)

# ── Filters ──
filtered_students = students_df.copy()
if course_filter != "Tất cả":
    filtered_students = filtered_students[filtered_students["Course Simplified"] == course_filter]
if source_filter != "Tất cả":
    filtered_students = filtered_students[filtered_students["Source Simplified"] == source_filter]
if gender_filter != "Tất cả":
    filtered_students = filtered_students[filtered_students["Gender"] == gender_filter]
if age_filter != "Tất cả":
    filtered_students = filtered_students[filtered_students["Age Group"] == age_filter]

valid_ids = filtered_students["Student ID"].unique()
filtered_multi = multi_df[multi_df["Student ID"].isin(valid_ids)]

if page == "▸ Tổng quan":
    render_overview(filtered_students, filtered_multi)
elif page == "⚙ Quản lý Users":
    render_admin_page()
else:
    render_center(filtered_students, filtered_multi, selected_center)


