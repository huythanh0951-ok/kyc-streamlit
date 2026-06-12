"""Login / logout / admin user management UI."""
import streamlit as st
from features.auth.logic import validate_login, add_user, remove_user, load_users_from_sheet


def render_login() -> bool:
    """Render login page."""
    st.markdown(
        "<h1 style='text-align:center;color:#1A3C5E;margin-top:60px;'>KYC DASHBOARD</h1>"
        "<p style='text-align:center;color:#888;font-size:14px;'>Đăng nhập để tiếp tục</p>",
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
        f"""<div style="padding:8px 0;border-bottom:1px solid #f0f0f0;margin-bottom:8px;">
            <div style="font-size:11px;color:#888;">Đã đăng nhập</div>
            <div style="font-size:14px;font-weight:600;color:#1A3C5E;">{username}</div>
            <div style="font-size:12px;color:#2196F3;">{role.upper()} | {center_label}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


def render_admin_page():
    """Admin user management page (main content area)."""
    from features.auth.logic import load_users_from_sheet, add_user, remove_user
    import streamlit as st

    users = load_users_from_sheet()
    user_list = sorted(users.keys())

    ALL_CENTERS = [
        "Bình Phước", "Hùng Vương", "Lê Duẩn", "Nguyễn Khuyến",
        "Nguyễn Trãi", "Phạm Văn Thuận", "Phước Tân",
        "Trần Phú", "Trảng Bom", "Võ Thị Sáu",
    ]

    st.markdown("<h2 style='color:#1A3C5E;'>🔧 Quản lý Users</h2>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**Thêm / Sửa User**")
        new_user = st.text_input("Username", key="admin_new_user")
        new_pass = st.text_input("Password", type="password", key="admin_new_pass")
        new_role = st.selectbox("Role", ["admin", "bod", "center"], key="admin_new_role")

        st.markdown("**Phân quyền Trung tâm** *(bắt buộc với role center)*")
        select_all = st.checkbox("Tất cả trung tâm", key="admin_all_centers")
        selected_centers = []
        if not select_all:
            cols = st.columns(2)
            for i, c in enumerate(ALL_CENTERS):
                with cols[i % 2]:
                    if st.checkbox(c, key=f"admin_center_{c}"):
                        selected_centers.append(c)

        if st.button("Lưu User", type="primary", use_container_width=True):
            if not new_user or not new_pass:
                st.error("Nhập đủ username + password!")
            elif new_role == "center" and not select_all and not selected_centers:
                st.error("Phải chọn ít nhất 1 trung tâm!")
            else:
                centers_val = "*" if (select_all or new_role in ("admin", "bod")) else ",".join(selected_centers)
                if add_user(new_user, new_pass, new_role, centers_val):
                    st.success(f"Đã lưu user '{new_user}'!")
                    st.rerun()
                else:
                    st.error("Lỗi khi lưu user!")

    with col_right:
        st.markdown("**Danh sách Users**")
        for u in user_list:
            info = users[u]
            raw_centers = info.get("centers", ["*"])
            if isinstance(raw_centers, list):
                centers_display = "Tất cả" if "*" in raw_centers else ", ".join(raw_centers)
            else:
                centers_display = str(raw_centers)
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{u}** — `{info['role']}` — *{centers_display}*")
            if c2.button("Xóa", key=f"del_{u}"):
                if u == "admin":
                    st.error("Không thể xóa admin!")
                else:
                    remove_user(u)
                    st.rerun()
