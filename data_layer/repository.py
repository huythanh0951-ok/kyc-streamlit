import pandas as pd
from pathlib import Path
import streamlit as st


# ── Constants ──
CENTER_MAP = {
    "Tran Van Xa": "Nguyễn Khuyến", "Le Duan": "Lê Duẩn",
    "Vo Thi Sau": "Võ Thị Sáu", "Pham Van Thuan": "Phạm Văn Thuận",
    "Nguyen Trai": "Nguyễn Trãi", "Hung Vuong": "Hùng Vương",
    "Phuoc Tan": "Phước Tân", "Tran Phu": "Trần Phú",
    "Binh Phuoc": "Bình Phước",
}
MULTI_SELECT_COLS = ["Interest", "Problem", "Goal", "Target Destination"]


def load_data():
    """Đọc raw wide format → trả về (students_df, multi_df)"""
    raw = _read_raw_wide()

    # ── 1. students_df: single-value columns ──
    single_cols = [c for c in raw.columns if c not in MULTI_SELECT_COLS]
    students = raw[single_cols].copy()

    # Clean center names
    students["Primary Center"] = students["Primary Center"].map(CENTER_MAP).fillna(students["Primary Center"])
    students["Age"] = pd.to_numeric(students["Age"], errors="coerce")

    # Clean "0" → "Không có thông tin"
    for col in ["Parent 1 Job", "Parent 2 Job"]:
        if col in students.columns:
            students[col] = students[col].replace("0", "Không có thông tin")
            students[col] = students[col].replace(0, "Không có thông tin")

    # Rule: có tên PH + ko có job → "Không có thông tin"; ko có tên PH + ko job → bỏ qua
    for pname, pjob in [("Parent 1 Name", "Parent 1 Job"), ("Parent 2 Name", "Parent 2 Job")]:
        if pname in students.columns:
            mask = students[pname].notna() & (students[pjob].isna() | (students[pjob] == "Không có thông tin"))
            students.loc[mask, pjob] = "Không có thông tin"

    # Clean "Trường ." và các variant → "Không có thông tin"
    def _is_noise_school(name):
        if pd.isna(name):
            return True
        s = str(name).strip().lower()
        if not s or s in ("-", "--", ".", "..", "chưa có", "khong", "không", "ko", "none"):
            return True
        # Pattern: "trường" hoặc "truong" + optional dấu chấm
        if s.replace(" ", "").replace(".", "") in ("trường", "truong", "tr", "t"):
            return True
        import re
        if re.match(r'^(trường|truong)\s*\.+$', s):
            return True
        return False
    students.loc[students["School Name"].apply(_is_noise_school), "School Name"] = "Không có thông tin"

    # Age Group
    bins, labels = [0, 5, 8, 12, 15, 200], ["3-5", "6-8", "9-12", "13-15", "16+"]
    students["Age Group"] = pd.cut(students["Age"], bins=bins, labels=labels, right=True).astype(str)

    # Study Abroad Flag
    def study_flag(cost):
        if pd.isna(cost): return "Không"
        c = str(cost).strip().lower()
        return "Không" if c in ("-none-", "no information yet", "") else "Có"
    students["Có Du Học"] = students["Study Abroad Cost"].apply(study_flag)

    # Course Simplified
    def course_simple(c):
        if pd.isna(c): return None
        orig = str(c).strip()
        uc = orig.upper()
        if "EGENIUS" in uc.replace("-", ""): return "B2C-EGENIUS"
        if "IELTS" in uc: return "B2C-IELTSNEXTGEN"
        if "EPIONEER" in uc: return "B2C-EPIONEER"
        return orig
    students["Course Simplified"] = students["Course Category"].apply(course_simple)

    # Source Simplified
    def source_simple(s):
        if pd.isna(s): return "Khác"
        s = str(s).strip()
        return s if s in ("Walk in", "Local Data", "EC Referral", "Digital Marketing", "Trade Show") else "Khác"
    students["Source Simplified"] = students["Source"].apply(source_simple)

    # Learning History Group
    def history_group(h):
        if pd.isna(h) or str(h).strip().lower() in ("-none-", "chưa có", ""):
            return "Không có"
        h_lower = str(h).strip().lower()
        if "đang" in h_lower and ("vmg" in h_lower or "vmc" in h_lower): return "Đang học tại VMG"
        if "cũ" in h_lower and ("vmg" in h_lower or "vmc" in h_lower): return "Từng học VMG"
        if "từng" in h_lower and ("vmg" in h_lower or "vmc" in h_lower): return "Từng học VMG"
        if ("kiểm tra" in h_lower or "test" in h_lower) and ("vmg" in h_lower or "vmc" in h_lower): return "Đã test đầu vào VMG"
        if "trường" in h_lower or "chỉ học" in h_lower or "học ở" in h_lower: return "Chỉ học ở trường"
        if "trung tâm" in h_lower or "hvg" in h_lower: return "Từng học TT khác"
        if "chưa" in h_lower: return "Chưa học TA"
        return "Khác"
    students["Learning History Group"] = students["Learning History"].apply(history_group)

    # ── 2. multi_df: unpivot multi-select columns ──
    multi_rows = []
    for _, row in raw.iterrows():
        sid = row["Student ID"]
        for col in MULTI_SELECT_COLS:
            val = row.get(col)
            if pd.isna(val):
                continue
            for item in str(val).split(","):
                item = item.strip()
                if item and item.lower() != "-none-":
                    multi_rows.append({"Student ID": sid, "Dimension": col, "Value": item})

    multi = pd.DataFrame(multi_rows)

    # Add "Không có dữ liệu" for students with zero multi-select data
    students_with_multi = set(multi["Student ID"].unique()) if not multi.empty else set()
    no_data_students = [s for s in students["Student ID"] if s not in students_with_multi]
    if no_data_students:
        no_data_rows = [{"Student ID": s, "Dimension": "Không có dữ liệu", "Value": "–"} for s in no_data_students]
        multi = pd.concat([multi, pd.DataFrame(no_data_rows)], ignore_index=True)

    return students, multi


def _read_raw_wide():
    """Đọc raw wide format từ Google Sheets hoặc fallback CSV"""
    import os

    # ── Try Google Sheets ──
    try:
        sheets_id = _secret("SHEETS_ID")
        if sheets_id:
            client = _get_gspread_client()
            sheet = client.open_by_key(sheets_id)
            ws = sheet.sheet1
            rows = ws.get_all_records()
            df = pd.DataFrame(rows)
            if not df.empty:
                df.columns = [c.replace("\xa0", "").strip() for c in df.columns]
                return df
    except Exception:
        pass

    # ── Fallback: CSV/Excel local ──
    paths = ["storage/data.csv", "storage/data.xlsx"]
    for p in paths:
        if Path(p).exists():
            if p.endswith('.csv'):
                df = pd.read_csv(p)
            else:
                df = pd.read_excel(p, engine="openpyxl")
            df.columns = [c.replace("\xa0", "").strip() for c in df.columns]
            return df

    st.error("❌ Không tìm thấy dữ liệu! Cần Google Sheets secrets hoặc file data.csv trong storage/")
    st.stop()


# ── User management (Google Sheets) ──

def _secret(key, default=""):
    """Đọc secret từ st.secrets (Streamlit Cloud) → fallback os.environ"""
    import os
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)


def _get_gspread_client():
    """Kết nối gspread với service account từ env vars"""
    import os
    import gspread
    from google.oauth2.service_account import Credentials

    creds_info = {
        "type": _secret("GCP_TYPE", "service_account"),
        "project_id": _secret("GCP_PROJECT_ID", ""),
        "private_key_id": _secret("GCP_PRIVATE_KEY_ID", ""),
        "private_key": _secret("GCP_PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": _secret("GCP_CLIENT_EMAIL", ""),
        "client_id": _secret("GCP_CLIENT_ID", ""),
        "auth_uri": _secret("GCP_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": _secret("GCP_TOKEN_URI", "https://oauth2.googleapis.com/token"),
    }
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)


def load_users_from_sheet():
    """Đọc tab Users từ Google Sheet, fallback default admin"""
    try:
        sheets_id = _secret("SHEETS_ID")
        if not sheets_id:
            return _default_users()
        client = _get_gspread_client()
        sheet = client.open_by_key(sheets_id)

        # Tạo tab Users nếu chưa có
        try:
            ws = sheet.worksheet("Users")
        except:
            ws = sheet.add_worksheet("Users", 10, 5)
            ws.append_row(["username", "password_hash", "plain_password", "role", "centers"])
            # Insert default admin
            import hashlib, secrets
            salt = secrets.token_hex(16)
            h = hashlib.pbkdf2_hmac("sha256", "admin123".encode(), salt.encode(), 100_000).hex()
            admin_hash = f"pbkdf2$100000${salt}${h}"
            ws.append_row(["admin", admin_hash, "admin123", "admin", "*"])
            return _default_users()

        rows = ws.get_all_records()
        users = {}
        for r in rows:
            uname = str(r.get("username", "")).strip()
            if not uname:
                continue
            centers_raw = str(r.get("centers", "*")).strip()
            centers = ["*"] if centers_raw == "*" else [c.strip() for c in centers_raw.split(",") if c.strip()]
            users[uname] = {
                "password_hash": str(r.get("password_hash", "")).strip(),
                "plain_password": str(r.get("plain_password", "***")).strip(),
                "role": str(r.get("role", "")).strip(),
                "centers": centers,
            }
        return users if users else _default_users()
    except Exception:
        return _default_users()


def save_user_to_sheet(username, password_hash, plain_password, role, centers):
    """Thêm hoặc cập nhật user trong sheet"""
    sheets_id = _secret("SHEETS_ID")
    if not sheets_id:
        return False
    client = _get_gspread_client()
    sheet = client.open_by_key(sheets_id)
    ws = sheet.worksheet("Users")

    # Đảm bảo header có đủ 5 cột
    headers = ws.row_values(1)
    if len(headers) < 5 or "plain_password" not in [h.strip().lower() for h in headers]:
        ws.update("A1:E1", [["username", "password_hash", "plain_password", "role", "centers"]])

    rows = ws.get_all_records()

    # Tìm row có username, nếu có thì update
    for i, r in enumerate(rows, start=2):
        if str(r.get("username", "")).strip() == username:
            ws.update(f"B{i}", [[password_hash]])
            ws.update(f"C{i}", [[plain_password]])
            ws.update(f"D{i}", [[role]])
            ws.update(f"E{i}", [[centers]])
            return True

    # Không có → append
    ws.append_row([username, password_hash, plain_password, role, centers])
    return True


def delete_user_from_sheet(username):
    """Xóa user khỏi sheet"""
    sheets_id = _secret("SHEETS_ID")
    if not sheets_id:
        return False
    client = _get_gspread_client()
    sheet = client.open_by_key(sheets_id)
    ws = sheet.worksheet("Users")
    rows = ws.get_all_records()
    for i, r in enumerate(rows, start=2):
        if str(r.get("username", "")).strip() == username:
            ws.delete_rows(i)
            return True
    return False


def _default_users():
    import hashlib, secrets
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", "admin123".encode(), salt.encode(), 100_000).hex()
    return {
        "admin": {
            "password_hash": f"pbkdf2$100000${salt}${h}",
            "plain_password": "admin123",
            "role": "admin",
            "centers": ["*"],
        }
    }
