"""Login / logout / admin user management UI."""
import streamlit as st
import base64
from features.auth.logic import validate_login, add_user, remove_user, load_users_from_sheet

# Cache logo base64
@st.cache_resource
def _logo_b64():
    with open("static/logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_login() -> bool:
    """Render login page."""
    logo = _logo_b64()
    st.markdown(
        f"<div style='text-align:center;margin-top:30px;'>"
        f"<img src='data:image/png;base64,{logo}' style='width:280px;'>"
        f"</div>"
        "<h1 style='text-align:center;color:#be202f;margin-top:10px;'>KYC DASHBOARD</h1>"
        "<p style='text-align:center;color:rgba(0,0,0,0.6);font-size:14px;font-family:Montserrat,sans-serif;'>Đăng nhập để tiếp tục</p>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("Tên đăng nhập", key="login_user")
        password = st.text_input("Mật khẩu", type="password", key="login_pass")
        if st.button("Đăng nhập", type="primary", use_container_width=True):
            if not username or not password:
                st.error("Vui lòng nhập đầy đủ!")
                return False
            user = validate_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu!")
                return False
    return False


def render_sidebar_header():
    """Show user info + logout + admin panel in sidebar."""
    user = st.session_state.get("user", {})
    role = user.get("role", "")
    username = user.get("username", "")
    centers = user.get("centers", ["*"])

    center_label = "Toàn hệ thống" if "*" in centers else ", ".join(centers)
    st.sidebar.markdown(
        f"<div style='text-align:center;margin-bottom:10px;'>"
        f"<img src='data:image/png;base64,{_logo_b64()}' style='width:140px;'>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"""<div style="padding:8px 0;border-bottom:1px solid #f0f0f0;margin-bottom:8px;">
            <div style="font-size:11px;color:rgba(0,0,0,0.6);font-family:Montserrat,sans-serif;">Đã đăng nhập</div>
            <div style="font-size:14px;font-weight:600;color:#be202f;font-family:Montserrat,sans-serif;">{username}</div>
            <div style="font-size:12px;color:#be202f;font-family:Montserrat,sans-serif;">{role.upper()} | {center_label}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


def render_admin_page():
    """Admin user management page (main content area)."""
    import streamlit as st

    users = load_users_from_sheet()
    user_list = sorted(users.keys())

    ALL_CENTERS = [
        "Bình Phước", "Hùng Vương", "Lê Duẩn", "Nguyễn Khuyến",
        "Nguyễn Trãi", "Phạm Văn Thuận", "Phước Tân",
        "Trần Phú", "Trảng Bom", "Võ Thị Sáu",
    ]

    st.markdown("<h2 style='font-family:Montserrat,sans-serif;color:#be202f;'>Quản lý Users</h2>", unsafe_allow_html=True)

    # Pre-fill from edit button
    if "edit_user" not in st.session_state:
        st.session_state.edit_user = None

    col_left, col_right = st.columns([1, 1])

    with col_left:
        # ── Block 1: Tạo User mới ──
        st.markdown("### Tạo User mới")
        new_user = st.text_input("Username", key="new_user_name")
        new_pass = st.text_input("Password", type="password", key="new_user_pass")
        new_role = st.selectbox("Role", ["admin", "bod", "center"], key="new_user_role")

        st.markdown("**Phân quyền Trung tâm**")
        select_all_new = st.checkbox("Tất cả trung tâm", key="new_all_centers")
        selected_new = []
        if not select_all_new:
            cols = st.columns(2)
            for i, c in enumerate(ALL_CENTERS):
                with cols[i % 2]:
                    if st.checkbox(c, key=f"new_center_{c}"):
                        selected_new.append(c)

        if st.button("Tạo User", type="primary", use_container_width=True):
            if not new_user or not new_pass:
                st.error("Nhập đủ username + password!")
            elif new_role == "center" and not select_all_new and not selected_new:
                st.error("Phải chọn ít nhất 1 trung tâm!")
            else:
                centers_val = "*" if (select_all_new or new_role in ("admin", "bod")) else ",".join(selected_new)
                if add_user(new_user, new_pass, new_role, centers_val):
                    st.success(f"Đã tạo user '{new_user}'!")
                    st.rerun()
                else:
                    st.error("Lỗi khi tạo user!")

    with col_right:
        # ── Block 2: Sửa User ──
        st.markdown("### Sửa User")
        edit_username = st.selectbox("Chọn user cần sửa", [""] + user_list, key="edit_user_select")
        if edit_username:
            info = users[edit_username]
            st.markdown(f"Role hiện tại: **{info['role']}** | Centers: *{info.get('centers', ['*'])}*")
            edit_pass = st.text_input("Password mới", type="password", key="edit_user_pass",
                                      placeholder="Để trống nếu không đổi")
            edit_role = st.selectbox("Role", ["admin", "bod", "center"], key="edit_user_role",
                                     index=["admin", "bod", "center"].index(info["role"]))

            st.markdown("**Phân quyền Trung tâm**")
            select_all_edit = st.checkbox("Tất cả trung tâm", key="edit_all_centers")
            selected_edit = []
            if not select_all_edit:
                cols = st.columns(2)
                for i, c in enumerate(ALL_CENTERS):
                    with cols[i % 2]:
                        if st.checkbox(c, key=f"edit_center_{c}"):
                            selected_edit.append(c)

            c1, c2 = st.columns(2)
            if c1.button("Cập nhật", type="primary", use_container_width=True):
                centers_val = "*" if (select_all_edit or edit_role in ("admin", "bod")) else ",".join(selected_edit)
                if add_user(edit_username, edit_pass, edit_role, centers_val):
                    st.success(f"Đã cập nhật '{edit_username}'!")
                    st.rerun()
                else:
                    st.error("Lỗi khi cập nhật!")
            if c2.button("Xóa user này", use_container_width=True):
                if edit_username == "admin":
                    st.error("Không thể xóa admin!")
                else:
                    remove_user(edit_username)
                    st.rerun()
