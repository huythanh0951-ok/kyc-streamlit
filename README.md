---
title: KYC Dashboard
emoji: 📊
colorFrom: blue
colorTo: blue
sdk: docker
app_file: Dockerfile
pinned: false
---

# KYC Dashboard

Phân tích dữ liệu học viên KYC - toàn hệ thống và từng center.

Data source: Google Sheets

## Chạy local

```xóa cahe
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
```

```bash
streamlit run app.py
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
