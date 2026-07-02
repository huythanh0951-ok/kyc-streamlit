import streamlit as st
from core.constants import COLOR_PRIMARY, COLOR_HEADER


def fmt_num(n):
    if n >= 1000: return f"{n:,}"
    return str(n)


def metric_card(col, label, value, suffix=""):
    col.markdown(
        f"""
        <div style="background:white;border-radius:8px;padding:16px 12px;text-align:center;
                    box-shadow:0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12);height:148px;
                    box-sizing:border-box;
                    display:flex;flex-direction:column;justify-content:center;
                    font-family:'Montserrat',sans-serif;">
            <div style="font-size:13px;color:rgba(0,0,0,0.6);text-transform:uppercase;letter-spacing:0.5px;font-weight:500;">{label}</div>
            <div style="font-size:29px;font-weight:700;color:{COLOR_PRIMARY};margin-top:4px;">{value}</div>
            {f'<div style="font-size:13px;color:rgba(0,0,0,0.54);">{suffix}</div>' if suffix else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def styled_header(title, subtitle=""):
    from core.logo_white_b64 import LOGO_WHITE_B64
    st.markdown(
        f"""
        <div style="background:{COLOR_HEADER};padding:24px 24px 18px 24px;margin:0 -16px 16px -16px;border-radius:8px;
                    box-shadow:0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12);
                    font-family:'Montserrat',sans-serif;">
            <div style="position:relative;display:flex;justify-content:space-between;align-items:center;min-height:100px;">
                <div style="color:white;font-size:20px;font-weight:600;">{title}</div>
                <img src="data:image/png;base64,{LOGO_WHITE_B64}" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);height:100px;">
                {f'<div style="color:rgba(255,255,255,0.85);font-size:20px;font-weight:500;">{subtitle}</div>' if subtitle else '<div></div>'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(text):
    st.markdown(
        f"<h3 style='font-family:Montserrat,sans-serif;font-size:15px;font-weight:600;color:rgba(0,0,0,0.87);margin:16px 0 8px;text-transform:uppercase;letter-spacing:0.3px;'>{text}</h3>",
        unsafe_allow_html=True,
    )
